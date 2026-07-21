#
# test_modulation.py
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

import pytest

from modulation import Modulation

# Parameterized test cases
BAUD_RATES  = [1200, 2400, 4800, 9600, 19200]

# Test fixtures
@pytest.fixture
def modulator():
    """Fixture providing a default modulator instance"""
    return Modulation(baud=9600)

def test_initialization(modulator):
    """Test that initialization sets the correct parameters"""
    assert modulator.get_baudrate() == 9600

@pytest.mark.parametrize("baud", BAUD_RATES)
def test_baudrate_setter(modulator, baud):
    """Test baudrate setter/getter"""
    modulator.set_baudrate(baud)
    assert modulator.get_baudrate() == baud

def test_int_to_bit_conversion(modulator):
    """Test integer to bit list conversion"""
    input_data = [0x01, 0x03]  # 00000001, 00000011
    expected_output = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]

    result = modulator._int_list_to_bit_list(input_data)

    assert result == expected_output
