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

    def modulate(self, data: list, L=_ASK_DEFAULT_OVERSAMPLING_FACTOR) -> tuple(np.ndarray, int, float):
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
