#
# gmsk.py
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

from pymodulation.gfsk import GFSK

class GMSK(GFSK):
    """
    GMSK modulator.
    """
    def __init__(self, bt, baud):
        """
        Class constructor with modulation initialization.

        :param bt: BT product (bandwidth x bit period) for GMSK
        :type: float

        :param baud: The desired data rate in bps
        :type: int

        :return: None.
        """
        super().__init__(0.5, bt, baud)

    def set_modulation_index(self, modidx):
        """
        Sets the modulation index.

        :note: For GMSK, the modulation index must always be 0.5.

        :param modidx: The new modulation index (always 0.5).
        :type: float

        :return: None.
        """
        if modidx != 0.5:
            raise ValueError("The modulation index of GMSK must be always 0.5! If you change the modulation index it will not be GMSK anymore!")
        else:
            super().set_modulation_index(modidx)
