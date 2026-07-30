#
# qpsk.py
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

from pymodulation.modulation import Modulation

_QPSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class QPSK(Modulation):
    """
    QPSK modulator/demodulator.
    """

    # Gray-coded QPSK constellation: dibit -> complex symbol
    QPSK_MAP = {
        (0, 0): complex(1, 1),
        (0, 1): complex(-1, 1),
        (1, 1): complex(-1, -1),
        (1, 0): complex(1, -1),
    }

    def modulate(self, data: list, L=_QPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Modulate data into QPSK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        s_bb, _ = self.modulate_time_domain(data, L)
        samples = s_bb.astype(np.complex64)

        # QPSK conveys two bits per symbol.  The public baudrate follows the
        # convention used by the other modulations and denotes the bit rate.
        f_sym = self.get_baudrate() / 2
        fs = L * f_sym
        dur = len(data) * 8 / self.get_baudrate()

        return samples, fs, dur

    def modulate_time_domain(self, data, L=_QPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Generates the QPSK modulated signal in time domain (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Baseband signal in time domain (length N*L).
        :rtype: np.ndarray

        :return: Discrete time base (length N*L).
        :rtype: np.ndarray
        """
        bits = self._int_list_to_bit_list(data)
        if len(bits) % 2:
            bits.append(0)

        symbols = np.array(
            [self.QPSK_MAP[(bits[i], bits[i + 1])] for i in range(0, len(bits), 2)],
            dtype=np.complex128,
        ) / np.sqrt(2)

        # Rectangular pulse shaping: each symbol occupies L samples.
        s_bb = np.repeat(symbols, L)
        t = np.arange(len(s_bb))

        return s_bb, t

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Demodulate QPSK IQ samples into bits.

        :param samples: IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return: Demodulated bits (0 or 1).
        :rtype: list
        """
        # The sample rate is L times the QPSK symbol rate (baudrate / 2).
        L = int(fs / (self.get_baudrate() / 2))

        # Integrate each rectangular symbol interval and sample at its end.
        integrated = np.convolve(samples, np.ones(L))
        symbols = integrated[L - 1::L]

        bits = []
        for symbol in symbols:
            # This is the inverse of QPSK_MAP: the first bit selects the Q
            # arm and the second bit selects the I arm.
            bits.extend((int(symbol.imag < 0), int(symbol.real < 0)))

        return bits
