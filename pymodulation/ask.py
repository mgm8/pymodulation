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

from pymodulation.modulation import Modulation

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

        :param order: ASK order.
        :type: int

        :return: None
        """
        self._order = order

    def get_order(self):
        """
        Gets the current order of the ASK modulation.

        :return: The order of the ASK modulation.
        :rtype: int
        """
        return self._order

    def modulate(self, data: list) -> tuple(np.ndarray, int, float):
        """
        Modulate data into ASK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        return np.ndarray(), int(), float()

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Demodulate ASK IQ samples into bits.

        :param samples: IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return: Demodulated bits (0 or 1).
        """
        return list()
