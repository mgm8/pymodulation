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

import pytest
import numpy as np

from gfsk import GFSK

# Parameterized test cases
MODULATION_INDICES = [0.3, 0.5, 1.0]
BT_PRODUCTS = [0.3, 0.5, 1.0]
BAUD_RATES = [1200, 9600, 19200]

# Test fixtures
@pytest.fixture
def gfsk_modulator():
    """Fixture providing a default GFSK modulator instance"""
    return GFSK(modidx=0.5, bt=0.3, baud=9600)

@pytest.fixture
def test_data():
    """Fixture providing test data (simple byte sequence)"""
    return [random.randint(0, 255) for _ in range(1000)]

def test_initialization(gfsk_modulator):
    """Test that initialization sets the correct parameters"""
    assert gfsk_modulator.get_modulation_index() == 0.5
    assert gfsk_modulator.get_bt() == 0.3
    assert gfsk_modulator.get_baudrate() == 9600

@pytest.mark.parametrize("modidx", MODULATION_INDICES)
def test_modulation_index_setter(gfsk_modulator, modidx):
    """Test modulation index setter/getter"""
    gfsk_modulator.set_modulation_index(modidx)
    assert gfsk_modulator.get_modulation_index() == modidx

@pytest.mark.parametrize("bt", BT_PRODUCTS)
def test_bt_setter(gfsk_modulator, bt):
    """Test BT product setter/getter"""
    gfsk_modulator.set_bt(bt)
    assert gfsk_modulator.get_bt() == bt

@pytest.mark.parametrize("baud", BAUD_RATES)
def test_baudrate_setter(gfsk_modulator, baud):
    """Test baudrate setter/getter"""
    gfsk_modulator.set_baudrate(baud)
    assert gfsk_modulator.get_baudrate() == baud

def test_modulate_output_shapes(gfsk_modulator, test_data):
    """Test that modulate returns outputs with correct shapes/types"""
    s_complex, fs, dur = gfsk_modulator.modulate(test_data)

    assert isinstance(s_complex, np.ndarray)
    assert isinstance(fs, (int, float))
    assert isinstance(dur, float)
    assert len(s_complex) > 0

def test_modulate_time_domain_output(gfsk_modulator, test_data):
    """Test time domain modulation output"""
    s_t, t, samp, dur = gfsk_modulator.modulate_time_domain(test_data)

    assert isinstance(s_t, np.ndarray)
    assert isinstance(t, np.ndarray)
    assert isinstance(samp, (int, float))
    assert isinstance(dur, float)
    assert len(s_t) == len(t)

def test_get_iq_output(gfsk_modulator, test_data):
    """Test IQ generation output"""
    I, Q, fs, dur = gfsk_modulator.get_iq(test_data)

    assert isinstance(I, np.ndarray)
    assert isinstance(Q, np.ndarray)
    assert isinstance(fs, (int, float))
    assert isinstance(dur, float)
    assert len(I) == len(Q)

def test_gaussian_lpf(gfsk_modulator):
    """Test Gaussian LPF coefficient generation"""
    Tb = 1/9600
    L = 100
    k = 1
    h_norm = gfsk_modulator._gaussian_lpf(Tb, L, k)

    assert isinstance(h_norm, np.ndarray)
    assert len(h_norm) > 0
    assert np.isclose(np.sum(h_norm), 1.0, rtol=1e-5)  # Should be normalized

def test_int_to_bit_conversion(gfsk_modulator):
    """Test integer to bit list conversion"""
    input_data = [0x01, 0x03]  # 00000001, 00000011
    expected_output = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]

    result = gfsk_modulator._int_list_to_bit_list(input_data)
    assert result == expected_output

def test_demodulation(gfsk_modulator, test_data):
    """Test demodulation round-trip"""
    # Modulate the test data
    s_complex, fs, _ = gfsk_modulator.modulate(test_data)

    # Demodulate
    demod_bits, sampled_signal = gfsk_modulator.demodulate(fs, s_complex)

    # Convert original data to bits for comparison
    original_bits = gfsk_modulator._int_list_to_bit_list(test_data)

    # We can't expect perfect reconstruction, but basic checks:
    assert len(demod_bits) > 0
    assert isinstance(demod_bits, list)
    assert isinstance(sampled_signal, np.ndarray)
    assert len(demod_bits)-2 <= len(original_bits)  # May lose some bits at edges

def test_frequency_discriminator(gfsk_modulator):
    """Test frequency discriminator"""
    # Create a simple IQ signal with known frequency deviation
    t = np.linspace(0, 1, 1000)
    freq_dev = 0.1
    iq_samples = np.exp(1j * 2 * np.pi * freq_dev * t)

    result = gfsk_modulator._frequency_discriminator(iq_samples)

    assert isinstance(result, np.ndarray)
    assert len(result) == len(iq_samples)

def test_gaussian_filter(gfsk_modulator):
    """Test Gaussian filter generation"""
    L = 10
    sps = 100
    g = gfsk_modulator._gaussian_filter(L, sps)

    assert isinstance(g, np.ndarray)
    assert len(g) == 2 * L + 1
    assert np.isclose(np.sum(g), 1.0, rtol=1e-5)  # Should be normalized

def test_modulator_demodulator(gfsk_modulator, test_data):
    """Test modulation and demoulation"""
    samples, fs, dur = gfsk_modulator.modulate(test_data)

    demod_bits, signal = gfsk_modulator.demodulate(fs, samples)

    data_res = list()

    for i in range(1, len(demod_bits) - 1, 8):
        result = int()
        pos = 8 - 1
        for j in range(8):
            result = result | (demod_bits[i + j] << pos)
            pos -= 1
        data_res.append(result)

    assert test_data == data_res
