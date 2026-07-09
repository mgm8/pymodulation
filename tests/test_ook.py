#
# test_ook.py
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

from ook import OOK

# Parameterized test cases
BAUD_RATES  = [1200, 2400, 4800, 9600, 19200]

# Test fixtures
@pytest.fixture
def ook_modulator():
    """Fixture providing a default OOK modulator instance"""
    return OOK(baud=9600)

@pytest.fixture
def test_data():
    """Fixture providing test data (simple byte sequence)"""
    return [random.randint(0, 255) for _ in range(1000)]

def test_initialization(ook_modulator):
    """Test that initialization sets the correct parameters"""
    assert ook_modulator.get_order() == 2
    assert ook_modulator.get_baudrate() == 9600

@pytest.mark.parametrize("order", [2, 4, 8, 16])
def test_order_setter(ook_modulator, order):
    """Test order setter/getter"""
    if order == 2:
        ook_modulator.set_order(order)
        assert ook_modulator.get_order() == order
    else:
        with pytest.raises(Exception) as exc_info:
            ook_modulator.set_order(order)

        assert exc_info.type is ValueError

@pytest.mark.parametrize("baud", BAUD_RATES)
def test_baudrate_setter(ook_modulator, baud):
    """Test baudrate setter/getter"""
    ook_modulator.set_baudrate(baud)
    assert ook_modulator.get_baudrate() == baud

def test_modulate_output_shapes(ook_modulator, test_data):
    """Test that modulate returns outputs with correct shapes/types"""
    s_complex, fs, dur = ook_modulator.modulate(test_data)

    assert isinstance(s_complex, np.ndarray)
    assert isinstance(fs, (int, float))
    assert isinstance(dur, float)
    assert len(s_complex) > 0

def test_int_to_bit_conversion(ook_modulator):
    """Test integer to bit list conversion"""
    input_data = [0x01, 0x03]  # 00000001, 00000011
    expected_output = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1]

    result = ook_modulator._int_list_to_bit_list(input_data)
    assert result == expected_output

def test_demodulation(ook_modulator, test_data):
    """Test demodulation round-trip"""
    # Modulate the test data
    s_complex, fs, _ = ook_modulator.modulate(test_data)

    # Demodulate
    demod_bits = ook_modulator.demodulate(s_complex, fs)

    # Convert original data to bits for comparison
    original_bits = ook_modulator._int_list_to_bit_list(test_data)

    # We can't expect perfect reconstruction, but basic checks:
    assert len(demod_bits) > 0
    assert isinstance(demod_bits, list)
    assert len(demod_bits) - 2 <= len(original_bits)  # May lose some bits at edges

def test_modulator_demodulator(ook_modulator, test_data):
    """Test modulation and demoulation"""
    test_data_bits = list()
    for i in test_data:
        test_data_bits += [int(digit) for digit in bin(i)[2:].zfill(8)]

    samples, fs, dur = ook_modulator.modulate(test_data)

    demod_bits = ook_modulator.demodulate(samples, fs)

    assert test_data_bits == demod_bits

def test_lowpass_filter_preserves_low_frequency_and_attenuates_high_frequency(ook_modulator):
    """Test low-pass filter"""
    sample_rate = 1000.0
    duration = 2.0

    t = np.arange(0, duration, 1 / sample_rate)

    # 50 Hz should pass
    low_freq = np.sin(2 * np.pi * 50 * t)

    # 200 Hz should be attenuated
    high_freq = 0.5 * np.sin(2 * np.pi * 200 * t)

    signal = low_freq + high_freq

    filtered = ook_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

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

def test_lowpass_filter_has_zero_phase(ook_modulator):
    """Test zero-phase of the low-pass filter"""
    sample_rate = 1000.0
    t = np.arange(0, 1.0, 1 / sample_rate)

    signal = np.sin(2 * np.pi * 20 * t)

    filtered = ook_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

    # Maximum correlation should occur at zero lag
    correlation = np.correlate(filtered, signal, mode="full")
    lag = np.argmax(correlation) - (len(signal) - 1)

    assert lag == 0

def test_lowpass_filter_short_signal(ook_modulator):
    """Test low-pass filter for short signals"""
    sample_rate = 1000.0
    signal = np.random.randn(30)

    filtered = ook_modulator._lowpass_filter(signal, cutoff=100.0, sample_rate=sample_rate)

    assert filtered.shape == signal.shape
    assert filtered.dtype == np.float32
    assert np.all(np.isfinite(filtered))

def test_estimate_levels_recovers_all_clusters(ook_modulator):
    """Test level estimate when all ASK levels are present"""
    rng = np.random.default_rng(42)

    true_levels = np.array([0.0, 1.0])

    samples = np.concatenate([rng.normal(level, 0.03, 200) for level in true_levels])

    estimated = ook_modulator._estimate_levels(samples, order=2)

    assert estimated.dtype == np.float32
    assert len(estimated) == 2

    np.testing.assert_allclose(estimated, true_levels, atol=0.1)

def test_estimate_levels_identical_samples(ook_modulator):
    """If every sample is identical, a normalized grid is returned."""
    samples = np.full(100, 2.5)

    estimated = ook_modulator._estimate_levels(samples, order=2)

    np.testing.assert_allclose(estimated, np.array([0.0, 1.0], dtype=np.float32))

    assert estimated.dtype == np.float32

def test_estimate_levels_returns_sorted_levels(ook_modulator):
    """Output is sorted"""
    rng = np.random.default_rng(7)

    samples = np.concatenate([rng.normal(3.0, 0.05, 100), rng.normal(0.0, 0.05, 100), rng.normal(2.0, 0.05, 100), rng.normal(1.0, 0.05, 100)])

    rng.shuffle(samples)

    estimated = ook_modulator._estimate_levels(samples, order=2)

    assert np.all(np.diff(estimated) > 0)

def test_find_symbol_offset(ook_modulator):
    """Finds the correct offset"""
    sps = 8
    offset = 3

    # Two ASK levels sampled at the symbol center
    symbols = np.array([0, 1] * 50, dtype=float)

    envelope = np.zeros(len(symbols) * sps)

    for i, sym in enumerate(symbols):
        envelope[i * sps + offset] = sym

    estimated = ook_modulator._find_symbol_offset(envelope, sps)

    assert estimated == offset

def test_find_symbol_offset_constant_signal(ook_modulator):
    """Constant envelope"""
    sps = 8
    envelope = np.ones(100)

    estimated = ook_modulator._find_symbol_offset(envelope, sps)

    assert estimated == 0

def test_find_symbol_offset_range(ook_modulator):
    """Result is within bounds"""
    rng = np.random.default_rng(42)

    sps = 16
    envelope = rng.normal(size=1000)

    estimated = ook_modulator._find_symbol_offset(envelope, sps)

    assert isinstance(estimated, int)
    assert 0 <= estimated < sps

def test_find_symbol_offset_with_noise(ook_modulator):
    """Robust against noise"""
    rng = np.random.default_rng(42)

    sps = 10
    offset = 4

    symbols = rng.integers(0, 2, 300).astype(float)

    envelope = rng.normal(scale=0.05, size=len(symbols) * sps)

    for i, sym in enumerate(symbols):
        envelope[i * sps + offset] += sym

    estimated = ook_modulator._find_symbol_offset(envelope, sps)

    assert estimated == offset

@pytest.mark.parametrize("sps,offset", [
    (4, 0),
    (4, 2),
    (8, 3),
    (10, 7),
    (16, 11),
])
def test_find_symbol_offset(ook_modulator, sps, offset):
    """Parametized find symbol offset test"""
    rng = np.random.default_rng(42)

    symbols = rng.integers(0, 2, 300).astype(float)

    envelope = rng.normal(scale=0.02, size=len(symbols) * sps)

    for i, sym in enumerate(symbols):
        envelope[i * sps + offset] += sym

    estimated = ook_modulator._find_symbol_offset(envelope, sps)

    assert estimated == offset

@pytest.mark.parametrize(
    "amps, expected",
    [
        ([0.05, 0.9, 1.95, 2.8], [0, 1, 2, 3]),
        ([0.5, 1.5], [0, 1]),                   # midpoint -> lower index
        ([-1.0, 4.0], [0, 3]),                  # outside range
        ([0.0, 1.0, 2.0, 3.0], [0, 1, 2, 3]),   # exact levels
    ],
)
def test_decide_symbols(ook_modulator, amps, expected):
    """Correct symbol decisions"""
    levels = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float32)

    symbols = ook_modulator._decide_symbols(np.asarray(amps), levels)

    np.testing.assert_array_equal(symbols, np.asarray(expected, dtype=np.uint8))

    assert symbols.dtype == np.uint8

def test_decide_symbols_midpoints(ook_modulator):
    """Midpoint (tie) behavior"""
    levels = np.array([0.0, 1.0, 2.0], dtype=np.float32)

    symbol_amps = np.array([
        0.5,   # between 0 and 1
        1.5,   # between 1 and 2
    ])

    symbols = ook_modulator._decide_symbols(symbol_amps, levels)

    expected = np.array([0, 1], dtype=np.uint8)

    np.testing.assert_array_equal(symbols, expected)

def test_decide_symbols_exact_levels(ook_modulator):
    """Exact level values"""
    levels = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float32)

    symbols = ook_modulator._decide_symbols(levels, levels)

    np.testing.assert_array_equal(symbols, np.arange(4, dtype=np.uint8))

def test_decide_symbols_outside_range(ook_modulator):
    """Values outside the range"""
    levels = np.array([0.0, 1.0, 2.0], dtype=np.float32)

    symbol_amps = np.array([-10.0, 10.0])

    symbols = ook_modulator._decide_symbols(symbol_amps, levels)

    expected = np.array([0, 2], dtype=np.uint8)

    np.testing.assert_array_equal(symbols, expected)

@pytest.mark.parametrize(
    "indices,bps,msb_first,expected",
    [
        (
            [0, 1, 2, 3],
            2,
            True,
            [0, 0, 0, 1, 1, 0, 1, 1],
        ),
        (
            [0, 1, 2, 3],
            2,
            False,
            [0, 0, 1, 0, 0, 1, 1, 1],
        ),
        (
            [5, 2],
            3,
            True,
            [1, 0, 1, 0, 1, 0],
        ),
        (
            [5, 2],
            3,
            False,
            [1, 0, 1, 0, 1, 0],
        ),  # 5=101 and 2=010 are palindromes
    ],
)
def test_symbols_to_bits(ook_modulator, indices, bps, msb_first, expected):
    """MSB-first (default)"""
    bits = ook_modulator._symbols_to_bits(np.asarray(indices, dtype=np.uint8), bits_per_symbol=bps, msb_first=msb_first)

    np.testing.assert_array_equal(bits, np.asarray(expected, dtype=np.uint8))

    assert bits.dtype == np.uint8

def test_symbols_to_bits_lsb_first(ook_modulator):
    """LSB-first"""
    indices = np.array([0, 1, 2, 3], dtype=np.uint8)

    bits = ook_modulator._symbols_to_bits( indices, bits_per_symbol=2, msb_first=False)

    expected = np.array([
        0, 0,   # 0 -> 00
        1, 0,   # 1 -> 10
        0, 1,   # 2 -> 01
        1, 1,   # 3 -> 11
    ], dtype=np.uint8)

    np.testing.assert_array_equal(bits, expected)

def test_symbols_to_bits_three_bits(ook_modulator):
    """Three bits per symbol"""
    indices = np.array([5, 2], dtype=np.uint8)

    bits = ook_modulator._symbols_to_bits(indices, bits_per_symbol=3)

    expected = np.array([
        1, 0, 1,   # 5 -> 101
        0, 1, 0,   # 2 -> 010
    ], dtype=np.uint8)

    np.testing.assert_array_equal(bits, expected)

def test_symbols_to_bits_empty(ook_modulator):
    """Empty input"""
    bits = ook_modulator._symbols_to_bits(np.array([], dtype=np.uint8), bits_per_symbol=2)

    assert bits.dtype == np.uint8
    assert bits.size == 0
