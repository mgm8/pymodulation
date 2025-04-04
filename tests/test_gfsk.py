#
# test_gfsk.py
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

import random

from gfsk import GFSK

def test_modulator_demodulator():
    data = [random.randint(0, 255) for _ in range(1000)]

    gfsk = GFSK(1.5, 0.5, 1200)

    samples, fs, dur = gfsk.modulate(data)

    demod_bits, signal = gfsk.demodulate(fs, samples)

    data_res = list()

    for i in range(1, len(demod_bits) - 1, 8):
        result = int()
        pos = 8 - 1
        for j in range(8):
            result = result | (demod_bits[i + j] << pos)
            pos -= 1
        data_res.append(result)

    assert data == data_res
