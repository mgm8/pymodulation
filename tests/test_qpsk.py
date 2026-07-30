#
# test_qpsk.py
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
import numpy as np

from qpsk import QPSK, _QPSK_DEFAULT_OVERSAMPLING_FACTOR

# Shared oversampling factor used in all tests (kept small for speed)
L = 10

@pytest.fixture
def qpsk():
    return QPSK(baud=1000)

def test_modulate_time_domain_uses_normalized_gray_constellation(qpsk):
    signal, time = qpsk.modulate_time_domain([0x1B], L)

    expected_symbols = np.array([
        1 + 1j, -1 + 1j, 1 - 1j, -1 - 1j,
    ]) / np.sqrt(2)
    np.testing.assert_array_equal(signal, np.repeat(expected_symbols, L))
    np.testing.assert_array_equal(time, np.arange(len(signal)))

def test_modulate_returns_complex_samples_and_qpsk_timing(qpsk):
    samples, fs, duration = qpsk.modulate([0xA5, 0x5A], L)

    assert samples.dtype == np.complex64
    assert len(samples) == 2 * 8 // 2 * L
    assert fs == pytest.approx(qpsk.get_baudrate() / 2 * L)
    assert duration == pytest.approx(16 / qpsk.get_baudrate())

@pytest.mark.parametrize("data", [
    [0x00],
    [0xFF],
    [0xA5],
    [0xDE, 0xAD, 0xBE, 0xEF],
    list(range(256)),
])
def test_round_trip_recovers_bits(qpsk, data):
    samples, fs, _ = qpsk.modulate(data, L)

    assert qpsk.demodulate(samples, fs) == qpsk._int_list_to_bit_list(data)

def test_round_trip_with_small_complex_awgn(qpsk):
    data = list(range(16))
    samples, fs, _ = qpsk.modulate(data, L)
    rng = np.random.default_rng(seed=42)
    noise = rng.normal(0, 0.05, len(samples)) + 1j * rng.normal(0, 0.05, len(samples))

    assert qpsk.demodulate(samples + noise, fs) == qpsk._int_list_to_bit_list(data)
