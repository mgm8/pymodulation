#
# lora.py
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

_LORA_DEFAULT_OVERSAMPLING_FACTOR = 100

class LoRa(Modulation):
    """
    LoRa modulator/demodulator.
    """

    def modulate(self, data: list, L=_LORA_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Modulate data into LoRa IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Oversampling factor (Tb/Ts)
        :type: int

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        pass

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Demodulate LoRa IQ samples into bits.

        :param samples: IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return: Demodulated bits (0 or 1).
        :rtype: list
        """
        pass
