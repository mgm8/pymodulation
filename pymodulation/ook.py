#
# ook.py
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

from pymodulation.ask import ASK

class OOK(ASK):
    """
    OOK modulator/demodulator
    """

    def __init__(self, baud):
        """
        OOK modulation constructor.

        :param baud: The desired data rate in bps.
        :type: int

        :return None
        """
        super().__init__(2, baud)

    def set_order(self, order):
        """
        Sets the order of the OOK modulation.

        :note: For OOK, the ASK order must be 2!

        :param order: OOK order (must be 2).
        :type: int

        :return: None
        """
        if order != 2:
            raise ValueError("The order of OOK modulation must be always 2! If you change the order it will not be OOK anymore!")
        else:
            super().set_order(order)
