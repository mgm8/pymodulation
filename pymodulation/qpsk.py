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
from scipy.signal import upfirdn

from pymodulation.modulation import Modulation

_QPSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class QPSK(Modulation):
    """
    QPSK modulator/demodulator.
    """

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
        # QPSK

        return None

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
        # TODO

        return None

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
        # TODO

        return None
