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

_BPSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class BPSK:
    """
    Simple BPSK modulator and demodulator.

    - Modulation: bits {0,1} -> symbols {-1,+1}
    - Demodulation: decision based on real part of IQ samples
    """

    def __init__(self, baud):
        """
        Class constructor.

        :param baud: Baudrate in bps.
        :type: int

        :return: None
        """
        self._baudrate = baud

    def set_baudrate(self, baud):
        """
        """
        self._baudrate = baud

    def get_baudrate(self):
        """
        """
        return self._baudrate

    def modulate(self, data: list, L=_BPSK_DEFAULT_OVERSAMPLING_FACTOR) -> np.ndarray:
        """
        Modulate data into BPSK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: IQ samples
        :rtype: np.ndarray
        """
        s_bb, t = self.modulate_time_domain(data, L)

        samples = s_bb.astype(np.complex64) # BPSK is purely real at baseband

        # Timing parameters
        fc = self.get_baudrate()    # Carrier frequency = Data transfer rate in bps
        fs = L*fc                   # Sample frequency in Hz
        Ts = 1.0/fs                 # Sample period in seconds
        Tb = L*Ts                   # Bit period in seconds
        dur = len(data)*Tb          # Transmission duration in seconds

        return samples, fs, dur

    def modulate_time_domain(self, data, L=_BPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Generates the BPSK modulated signal in time domain (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Baseband signal in time domain.
        :rtype: np.ndarray

        :return: Time base
        :rtype: np.ndarray
        """
        # Convert to array of bits
        bits = np.array(self._int_list_to_bit_list(data))

        s_bb = upfirdn(h=[1]*L, x=2*bits-1, up=L)   # NRZ encoder
        t = np.arange(start=0, stop=len(bits)*L)    # Discrete time base

        return s_bb, t

    def demodulate(self, samples: np.ndarray, L=_BPSK_DEFAULT_OVERSAMPLING_FACTOR) -> np.ndarray:
        """
        Demodulate BPSK IQ samples into bits.

        :param iq: IQ samples.
        :type: np.ndarray

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Demodulated bits (0 or 1).
        :rtype: list
        """
        x = np.real(samples)            # I arm
        x = np.convolve(x, np.ones(L))  # Integrate for Tb duration (L samples)
        x = x[L-1:-1:L]                 # I arm - sample at every L
        bits = (x > 0).transpose()      # Threshold detector

        return list(map(int, bits))

    def _int_list_to_bit_list(self, n):
        """
        Converts a integer list (bytes) to a bit list.

        :param n: An integer list.
        :type: list

        :return res: The given integer list as a bit list
        :rtype: list
        """
        res = list()

        for i in n:
            res = res + [int(digit) for digit in bin(i)[2:].zfill(8)]

        return res
