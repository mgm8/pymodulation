#
# bpsk.py
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
from scipy.signal import upfirdn

from pymodulation.modulation import Modulation

_BPSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class BPSK(Modulation):
    """
    BPSK modulator/demodulator.
    """

    def modulate(self, data: list, L=_BPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Modulate data into BPSK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        s_bb, t = self.modulate_time_domain(data, L)
        samples = s_bb.astype(np.complex64) # BPSK is purely real at baseband

        f_sym = self.get_baudrate()         # Symbol rate in baud
        fs = L * f_sym                      # Sample rate in Hz

        n_bits = len(data) * 8
        dur = n_bits / f_sym                # Transmission duration in seconds

        return samples, fs, dur

    def modulate_time_domain(self, data, L=_BPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Generates the BPSK modulated signal in time domain (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Baseband signal in time domain (length N*L).
        :rtype: np.ndarray

        :return: Discrete time base (length N*L).
        :rtype: np.ndarray
        """
        # Convert to array of bits
        bits = np.array(self._int_list_to_bit_list(data))
        n_bits = len(bits)

        # NRZ encoder: upfirdn with h=[1]*L produces output of length N*L + L-1
        s_bb_full = upfirdn(h=[1] * L, x=2 * bits - 1, up=L)

        s_bb = s_bb_full[:n_bits * L]

        t = np.arange(start=0, stop=n_bits * L)  # Discrete time base

        return s_bb, t

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Demodulate BPSK IQ samples into bits.

        :param samples: IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return: Demodulated bits (0 or 1).
        :rtype: list
        """
        L = int(fs/self.get_baudrate()) # Oversampling factor (Samples/bit)
        x = np.real(samples)            # I arm
        x = np.convolve(x, np.ones(L))  # Integrate for Tb duration (L samples)

        x = x[L - 1::L]                 # Sample at the end of each integration window

        bits = (x > 0).transpose()      # Threshold detector

        return list(map(int, bits))
