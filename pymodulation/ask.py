#
# ask.py
#
# Copyright The PyModulation Contributors.
#
# This file is part of PyModulation library.
#
# PyModulation library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyModulation library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PyModulation library. If not, see <http://www.gnu.org/licenses/>.
#
#

import numpy as np
from scipy.signal import firwin, filtfilt

from pymodulation.modulation import Modulation

_ASK_DEFAULT_OVERSAMPLING_FACTOR=100

class ASK(Modulation):
    """
    ASK modulator/demodulator.
    """

    def __init__(self, order, baud):
        """
        ASK modulation constructor.

        :param order: ASK order.
        :type: int

        :param baud: The desired data rate in bps.
        :type: int

        :return None
        """
        super().__init__(baud)

        self._order = int()

        self.set_order(order)

    def set_order(self, order):
        """
        Sets the order of the ASK modulation.

        :note: The possible order values are 2, 4 or 8.

        :param order: ASK order (2, 4 or 8).
        :type: int

        :return: None
        """
        if order not in (2, 4, 8):
            raise ValueError("ASK order must be 2, 4 or 8!")

        self._order = order

    def get_order(self):
        """
        Gets the current order of the ASK modulation.

        :return: The order of the ASK modulation.
        :rtype: int
        """
        return self._order

    def modulate(self, data: list, L=_ASK_DEFAULT_OVERSAMPLING_FACTOR) -> tuple:
        """
        Modulate data into ASK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        bits_per_symbol = int(np.log2(self.get_order()))

        # Convert to array of bits
        bits = np.array(self._int_list_to_bit_list(data))

        # Bits -> symbol indices
        symbols = bits.reshape(-1, bits_per_symbol)
        # Treat each row as a big-endian binary number
        weights = 1 << np.arange(bits_per_symbol - 1, -1, -1)
        indices = symbols @ weights  # Integer symbol index in [0, order-1]

        # Symbol index -> amplitude (Normalize)
        amplitudes = indices / (self.get_order() - 1)  # float in [0, 1]

        # Pulse shaping: rectangular (repeat each amplitude)
        envelope = np.repeat(amplitudes, L).astype(np.float32)

        # Build baseband IQ (Q = 0 for real ASK)
        iq = envelope.astype(np.complex64)

        fs = L * self.get_baudrate()                # Sample rate
        dur = len(data) * 8 /self.get_baudrate()    # Signal duration

        return iq, fs, dur

    def modulate_time_domain(self, data: list, sps: int = _ASK_DEFAULT_OVERSAMPLING_FACTOR, carrier_phase: float = 0.0) -> tuple:
        """
        Generates the ASK modulated signal in time domain.

        :param data: Input integer list to modulate (bytes as integers).
        :type data: list[int]

        :param sps: Samples per symbol.
        :type sps: int

        :param carrier_phase: Initial carrier phase φ₀ in radians.
        :type carrier_phase: float

        :return s_t: ASK modulated signal with carrier s(t) (time domain).
        :rtype s_t: np.ndarray

        :return t: Time base for RF carrier in seconds.
        :rtype t: np.ndarray

        :return samp: Sample rate in S/s.
        :rtype samp: int

        :return dur: Signal duration in seconds.
        :rtype dur: float
        """
        # Derive sample rate and time base from baudrate and sps,
        # mirroring: fs = sps * fc  and  Ts = 1/fs
        fc = self.get_baudrate()    # Carrier freq = symbol rate in Hz
        fs = sps * fc               # Sample rate in S/s
        Ts = 1.0 / fs               # Sample period

        # Step 1: bytes -> bits -> per-symbol amplitudes
        bits = np.array(self._int_list_to_bit_list(data))
        amplitudes = self._bits_to_symbols(bits)

        # Step 2: baseband envelope — rectangular pulse shaping
        envelope = np.repeat(amplitudes, sps).astype(np.float64)

        # Step 3: time base (matches GFSK convention: Ts * arange(len(signal)))
        t = Ts * np.arange(start=0, stop=len(envelope))
        dur = float(t[-1])          # Signal duration in seconds

        # Step 4: time-domain carrier multiplication
        # For pure ASK, Q = 0, so s(t) reduces to: envelope(t) * cos(2*pi*fc*t + φ₀)
        s_t = envelope * np.cos(2.0 * np.pi * fc * t + carrier_phase)

        return s_t, t, int(fs), dur

    def demodulate(self, samples: np.ndarray, fs, lpf_cutoff=1000.0, use_kmeans=True) -> list:
        """
        Demodulate ASK IQ samples into bits.

        :param samples: Base band IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return: Demodulated bits (0 or 1).
        """
        bits_per_symbol = int(np.log2(self.get_order()))
        samples_per_symbol = int(fs/self.get_baudrate())

        # Envelope extraction
        envelope_raw = np.abs(samples).astype(np.float32)

        # Low-pass filter
        if samples_per_symbol is not None:
            symbol_rate = fs / samples_per_symbol
        else:
            # Rough estimate for filter design; refined below
            symbol_rate = fs / 10.0

        if lpf_cutoff is None:
            lpf_cutoff = 0.75 * symbol_rate
            # Clamp to usable range
            lpf_cutoff = max(lpf_cutoff, fs * 0.01)
            lpf_cutoff = min(lpf_cutoff, fs * 0.45)

        envelope = self._lowpass_filter(envelope_raw, lpf_cutoff, fs)

        # Step 4 – Symbol timing recovery
        if samples_per_symbol is None:
            sps_max = max(2, len(envelope) // 4)
            samples_per_symbol = estimate_samples_per_symbol(envelope, fs, sps_max=min(sps_max, 512))

            # Now that we have SPS, re-filter with correct cutoff
            if lpf_cutoff is None:
                lpf_cutoff = 0.75 * (fs / samples_per_symbol)
                lpf_cutoff = max(lpf_cutoff, fs * 0.01)
                lpf_cutoff = min(lpf_cutoff, fs * 0.45)
                envelope = self._lowpass_filter(envelope_raw, lpf_cutoff, fs)

        symbol_offset = self._find_symbol_offset(envelope, samples_per_symbol)

        symbol_amps = envelope[symbol_offset::samples_per_symbol].astype(np.float32)

        # Step 5 & 6 – Amplitude slicing / decision
        if use_kmeans:
            levels = self._estimate_levels(symbol_amps, self.get_order())
        else:
            lo, hi = float(symbol_amps.min()), float(symbol_amps.max())
            levels = np.linspace(lo, hi, self.get_order(), dtype=np.float32)

        symbol_indices = self._decide_symbols(symbol_amps, levels)

        # Step 7 – Symbols -> bits
        bits = self._symbols_to_bits(symbol_indices, bits_per_symbol, msb_first=True)

        return list(bits)

    def _lowpass_filter(self, signal: np.ndarray, cutoff: float, sample_rate: float, num_taps: int = 64) -> np.ndarray:
        """
        Zero-phase FIR low-pass filter using a Hann-windowed sinc kernel.

        :param signal: 1-D real array.
        :type: np.ndarray

        :param cutoff: cutoff frequency in Hz.
        :type: float

        :param sample_rate: Sample rate in S/sec.
        :type: float

        :param num_taps: Filter length (must be even; +1 added internally for symmetry).
        :type: int

        :return: Filtered signal (same length as input, no group-delay shift).
        :rtype: np.ndarray
        """
        nyq = sample_rate / 2.0
        # filtfilt needs signal length > padlen ≈ 3 * num_taps; clamp accordingly
        max_taps = max(3, (len(signal) // 3) - 1)
        num_taps = min(num_taps, max_taps)
        if num_taps % 2 == 0:
            num_taps -= 1        # firwin needs odd length for symmetric filter
        num_taps = max(num_taps, 3)
        taps = firwin(num_taps, cutoff / nyq, window="hann")

        return filtfilt(taps, [1.0], signal).astype(np.float32)

    def _estimate_levels(self, symbol_amps: np.ndarray, order: int, min_cluster_ratio: float = 0.5) -> np.ndarray:
        """
        Estimate ASK amplitude levels from received symbol amplitudes using
        k-means clustering (1-D, converges in a few iterations).

        If the data does not exercise all ``order`` amplitude levels (e.g. a
        short packet that never contains the lowest level), k-means will split
        real clusters incorrectly.  The function detects this via a minimum
        inter-centroid spacing check and falls back to uniformly-spaced levels
        anchored to the observed [min, max] range.

        :param symbol_amps: 1-D float array of sampled amplitudes.
        :type: np.ndarray

        :param order: Number of ASK levels (must be a power of 2).
        :type: int

        :param min_cluster_ratio: Centroids whose nearest-neighbour gap is smaller than ``min_cluster_ratio × expected_gap`` trigger the uniform fallback.
        :type: float

        :return: Sorted array of ``order`` estimated level centroids.
        :rtype:
        """
        lo, hi = float(symbol_amps.min()), float(symbol_amps.max())

        # Degenerate: all symbols identical
        if hi - lo < 1e-6:
            return np.linspace(0.0, 1.0, order, dtype=np.float32)

        # Initialise centroids uniformly between observed min and max
        centroids = np.linspace(lo, hi, order, dtype=np.float64)

        for _ in range(200):
            dists = np.abs(symbol_amps[:, None] - centroids[None, :])
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array(
                [
                    symbol_amps[labels == k].mean() if np.any(labels == k) else centroids[k]
                    for k in range(order)
                ],
                dtype=np.float64,
            )
            if np.allclose(centroids, new_centroids, atol=1e-9):
                break
            centroids = new_centroids

        centroids = np.sort(centroids)

        # Sanity-check: if adjacent centroids are suspiciously close the payload
        # likely doesn't cover all levels → fall back to a uniform grid.
        if order > 1:
            gaps = np.diff(centroids)
            expected_gap = (hi - lo) / (order - 1)
            if np.any(gaps < min_cluster_ratio * expected_gap):
                centroids = np.linspace(lo, hi, order, dtype=np.float64)

        return centroids.astype(np.float32)

    def _find_symbol_offset(self, envelope: np.ndarray, sps: int) -> int:
        """
        Find the best sampling phase within one symbol period.

        Picks the offset that maximises the variance of sampled values —
        high variance means we're sampling near symbol centres rather than
        transitions.

        :param envelope: Real envelope signal.
        :type: np.ndarray

        :param sps: Samples per symbol.
        :type: int

        :return: Best integer offset in [0, sps-1].
        :rtype: int
        """
        best_offset, best_var = 0, -1.0
        for offset in range(sps):
            samples = envelope[offset::sps]
            v = float(np.var(samples))
            if v > best_var:
                best_var = v
                best_offset = offset

        return best_offset

    def _decide_symbols(self, symbol_amps: np.ndarray, levels: np.ndarray) -> np.ndarray:
        """
        Map each amplitude sample to the nearest level index.

        :param symbol_amps: 1-D float array.
        :type: np.ndarray

        :param levels: Sorted array of level centroids (length = ASK order).
        :type: np.ndarray

        :return: Integer array of symbol indices in [0, order-1].
        :rtype: np.ndarray
        """
        dists = np.abs(symbol_amps[:, None] - levels[None, :])

        return np.argmin(dists, axis=1).astype(np.uint8)

    def _bits_to_symbols(self, bits: np.ndarray) -> np.ndarray:
        """
        Pack `log2(order)` consecutive bits into one symbol amplitude.

        :param bits: flat uint8 bit array (MSB-first within each symbol)
        :type: np.ndarray

        :return: float32 array of per-symbol amplitudes, length = len(bits) / log2(order)
        :rtype: np.ndarray
        """
        bps = int(np.log2(self.get_order()))
        pad = (-len(bits)) % bps
        if pad:
            bits = np.append(bits, np.zeros(pad, dtype=np.uint8))

        weights = 1 << np.arange(bps - 1, -1, -1)   # Big-endian weights
        indices = bits.reshape(-1, bps) @ weights   # Integer indices

        return (indices / (self.get_order() - 1)).astype(np.float32)

    def _symbols_to_bits(self, indices: np.ndarray, bits_per_symbol: int, msb_first: bool = True) -> np.ndarray:
        """
        Convert symbol indices to a flat bit array.

        :param indices: Integer array of symbol indices.
        :type: np.ndarray

        :param bits_per_symbol: Bits per symbol.
        :type: int

        :param msb_first: Flag for bit order within each symbol.
        :type: bool

        :return: Flat uint8 bit array
        :rtype: np.ndarray
        """
        bits = np.zeros(len(indices) * bits_per_symbol, dtype=np.uint8)
        for i, idx in enumerate(indices):
            for b in range(bits_per_symbol):
                bit_pos = (bits_per_symbol - 1 - b) if msb_first else b
                bits[i * bits_per_symbol + b] = (int(idx) >> bit_pos) & 1

        return bits
