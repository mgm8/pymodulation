#
# test_ask.py
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

from ask import ASK

# Parameterized test cases
ORDERS      = [2, 4, 8]
BAUD_RATES  = [1200, 9600, 19200]

# Test fixtures
@pytest.fixture
def ask_modulator():
    """Fixture providing a default ASK modulator instance"""
    return ASK(order=2, baud=9600)

@pytest.fixture
def test_data():
    """Fixture providing test data (simple byte sequence)"""
    return [random.randint(0, 255) for _ in range(1000)]

def test_initialization(ask_modulator):
    """Test that initialization sets the correct parameters"""
    assert ask_modulator.get_order() == 2
    assert ask_modulator.get_baudrate() == 9600

@pytest.mark.parametrize("order", ORDERS)
def test_order_setter(ask_modulator, order):
    """Test order setter/getter"""
    ask_modulator.set_order(order)
    assert ask_modulator.get_order() == order

@pytest.mark.parametrize("baud", BAUD_RATES)
def test_baudrate_setter(ask_modulator, baud):
    """Test baudrate setter/getter"""
    ask_modulator.set_baudrate(baud)
    assert ask_modulator.get_baudrate() == baud

def test_modulate_output_shapes(ask_modulator, test_data):
    """Test that modulate returns outputs with correct shapes/types"""
    s_complex, fs, dur = ask_modulator.modulate(test_data)

    assert isinstance(s_complex, np.ndarray)
    assert isinstance(fs, (int, float))
    assert isinstance(dur, float)
    assert len(s_complex) > 0

def test_int_to_bit_conversion(ask_modulator):
    """Test integer to bit list conversion"""
    input_data = [0x01, 0x03]  # 00000001, 00000011
    expected_output = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]

    result = ask_modulator._int_list_to_bit_list(input_data)
    assert result == expected_output

def test_demodulation(ask_modulator, test_data):
    """Test demodulation round-trip"""
    # Modulate the test data
    s_complex, fs, _ = ask_modulator.modulate(test_data)

    # Demodulate
    demod_bits = ask_modulator.demodulate(s_complex, fs)

    # Convert original data to bits for comparison
    original_bits = ask_modulator._int_list_to_bit_list(test_data)

    # We can't expect perfect reconstruction, but basic checks:
    assert len(demod_bits) > 0
    assert isinstance(demod_bits, list)
    assert len(demod_bits) - 2 <= len(original_bits)  # May lose some bits at edges

def test_modulator_demodulator(ask_modulator, test_data):
    """Test modulation and demoulation"""
    test_data_bits = list()
    for i in test_data:
        test_data_bits += [int(digit) for digit in bin(i)[2:].zfill(8)]

    samples, fs, dur = ask_modulator.modulate(test_data)

    demod_bits = ask_modulator.demodulate(samples, fs)

    assert test_data_bits == demod_bits

def test_lowpass_filter_preserves_low_frequency_and_attenuates_high_frequency(ask_modulator):
    """Test low-pass filter"""
    sample_rate = 1000.0
    duration = 2.0

    t = np.arange(0, duration, 1 / sample_rate)

    # 50 Hz should pass
    low_freq = np.sin(2 * np.pi * 50 * t)

    # 200 Hz should be attenuated
    high_freq = 0.5 * np.sin(2 * np.pi * 200 * t)

    signal = low_freq + high_freq

    filtered = ask_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

    # Output properties
    assert filtered.shape == signal.shape
    assert filtered.dtype == np.float32

    # Frequency-domain analysis
    freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)

    spectrum_in = np.abs(np.fft.rfft(signal))
    spectrum_out = np.abs(np.fft.rfft(filtered))

    idx_50 = np.argmin(np.abs(freqs - 50))
    idx_200 = np.argmin(np.abs(freqs - 200))

    gain_50 = spectrum_out[idx_50] / spectrum_in[idx_50]
    gain_200 = spectrum_out[idx_200] / spectrum_in[idx_200]

    # 50 Hz should remain nearly unchanged
    assert gain_50 > 0.90

    # 200 Hz should be strongly attenuated
    assert gain_200 < 0.10

def test_lowpass_filter_has_zero_phase(ask_modulator):
    """Test zero-phase of the low-pass filter"""
    sample_rate = 1000.0
    t = np.arange(0, 1.0, 1 / sample_rate)

    signal = np.sin(2 * np.pi * 20 * t)

    filtered = ask_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

    # Maximum correlation should occur at zero lag
    correlation = np.correlate(filtered, signal, mode="full")
    lag = np.argmax(correlation) - (len(signal) - 1)

    assert lag == 0

def test_lowpass_filter_short_signal(ask_modulator):
    """Test low-pass filter for short signals"""
    sample_rate = 1000.0
    signal = np.random.randn(30)

    filtered = ask_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

    assert filtered.shape == signal.shape
    assert filtered.dtype == np.float32
    assert np.all(np.isfinite(filtered))

def test_estimate_levels_recovers_all_clusters(ask_modulator):
    """Test level estimate when all ASK levels are present"""
    rng = np.random.default_rng(42)

    true_levels = np.array([0.0, 1.0, 2.0, 3.0])

    samples = np.concatenate([rng.normal(level, 0.03, 200) for level in true_levels])

    estimated = ask_modulator._estimate_levels(samples, order=4)

    assert estimated.dtype == np.float32
    assert len(estimated) == 4

    np.testing.assert_allclose(estimated, true_levels, atol=0.1)

def test_estimate_levels_identical_samples(ask_modulator):
    """If every sample is identical, a normalized grid is returned."""
    samples = np.full(100, 2.5)

    estimated = ask_modulator._estimate_levels(samples, order=4)

    np.testing.assert_allclose(estimated, np.array([0.0, 1 / 3, 2 / 3, 1.0], dtype=np.float32))

    assert estimated.dtype == np.float32

def test_estimate_levels_missing_cluster_falls_back_to_uniform(ask_modulator):
    """
    Missing one amplitude level should trigger the uniform-grid fallback.
    """
    rng = np.random.default_rng(123)

    # Missing the lowest level
    samples = np.concatenate([rng.normal(1.0, 0.02, 200), rng.normal(2.0, 0.02, 200), rng.normal(3.0, 0.02, 200)])

    estimated = ask_modulator._estimate_levels(samples, order=4)

    expected = np.linspace(samples.min(), samples.max(), 4, dtype=np.float32)

    np.testing.assert_allclose(estimated, expected, atol=0.05)

def test_estimate_levels_returns_sorted_levels(ask_modulator):
    """Output is sorted"""
    rng = np.random.default_rng(7)

    samples = np.concatenate([rng.normal(3.0, 0.05, 100), rng.normal(0.0, 0.05, 100), rng.normal(2.0, 0.05, 100), rng.normal(1.0, 0.05, 100)])

    rng.shuffle(samples)

    estimated = ask_modulator._estimate_levels(samples, order=4)

    assert np.all(np.diff(estimated) > 0)

@pytest.mark.parametrize("order", ORDERS)
def test_estimate_levels_all_orders(ask_modulator, order):
    """Parameterized test over the modulation order."""
    rng = np.random.default_rng(42)

    true_levels = np.arange(order, dtype=float)

    samples = np.concatenate([rng.normal(level, 0.02, 200) for level in true_levels])

    estimated = ask_modulator._estimate_levels(samples, order)

    np.testing.assert_allclose(estimated, true_levels, atol=0.1)
