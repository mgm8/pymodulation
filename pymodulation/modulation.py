#
# modulation.py
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

class Modulation:
    """
    Generic modulation class.
    """

    def __init__(self, baud):
        """
        Generic digital modulation constructor.

        :param baud: The desired data rate in bps.
        :type: int

        :return None
        """
        self._baudrate = int()

        self.set_baudrate(baud)

    def set_baudrate(self, baud):
        """
        Sets the baudrate.

        :param baud: The new baudrate in bps.
        :type: int

        :return: None.
        """
        self._baudrate = baud

    def get_baudrate(self):
        """
        Gets the current baudrate.

        :return: The configured baudrate in bps.
        :rtype: int
        """
        return self._baudrate

    def _int_list_to_bit_list(self, n):
        """
        Converts an integer list (bytes) to a bit list.

        :param n: An integer list.
        :type: list

        :return res: The given integer list as a bit list
        :rtype: list
        """
        res = list()
        for i in n:
            res += [int(digit) for digit in bin(i)[2:].zfill(8)]

        return res
