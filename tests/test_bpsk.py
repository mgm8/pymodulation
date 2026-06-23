#
# test_bpsk.py
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

from bpsk import BPSK, _BPSK_DEFAULT_OVERSAMPLING_FACTOR

# Shared oversampling factor used in all tests (kept small for speed)
L = 10

@pytest.fixture
def bpsk():
    """Default BPSK instance with baudrate = 1000."""
    return BPSK(baud=1000)

# 1. Constructor & baudrate accessors
class TestBaudrate:
    def test_initial_baudrate(self, bpsk):
        assert bpsk.get_baudrate() == 1000

    def test_set_baudrate(self, bpsk):
        bpsk.set_baudrate(9600)
        assert bpsk.get_baudrate() == 9600

    def test_set_baudrate_zero(self, bpsk):
        """Baudrate of 0 is technically settable; callers must avoid division by zero."""
        bpsk.set_baudrate(0)
        assert bpsk.get_baudrate() == 0

# 2. _int_list_to_bit_list (private helper — tested via known byte values)
class TestIntListToBitList:
    def test_single_zero_byte(self, bpsk):
        assert bpsk._int_list_to_bit_list([0x00]) == [0] * 8

    def test_single_full_byte(self, bpsk):
        assert bpsk._int_list_to_bit_list([0xFF]) == [1] * 8

    def test_known_byte(self, bpsk):
        # 0xA5 = 1010 0101
        assert bpsk._int_list_to_bit_list([0xA5]) == [1, 0, 1, 0, 0, 1, 0, 1]

    def test_multiple_bytes_length(self, bpsk):
        result = bpsk._int_list_to_bit_list([0x00, 0xFF, 0xA5])
        assert len(result) == 24

    def test_multiple_bytes_values(self, bpsk):
        result = bpsk._int_list_to_bit_list([0x00, 0xFF])
        assert result == [0] * 8 + [1] * 8

    def test_output_contains_only_bits(self, bpsk):
        result = bpsk._int_list_to_bit_list([0x55, 0xAA])
        assert all(b in (0, 1) for b in result)

    def test_empty_list(self, bpsk):
        assert bpsk._int_list_to_bit_list([]) == []

# 3. modulate_time_domain
class TestModulateTimeDomain:
    def test_output_lengths_match(self, bpsk):
        """s_bb and t must have the same length."""
        data = [0xAB]
        s_bb, t = bpsk.modulate_time_domain(data, L)
        assert len(s_bb) == len(t)

    def test_output_length_is_n_bits_times_L(self, bpsk):
        data = [0x00, 0xFF]          # 2 bytes = 16 bits
        s_bb, t = bpsk.modulate_time_domain(data, L)
        assert len(s_bb) == 16 * L
        assert len(t) == 16 * L

    def test_time_base_starts_at_zero(self, bpsk):
        s_bb, t = bpsk.modulate_time_domain([0x00], L)
        assert t[0] == 0

    def test_time_base_is_contiguous(self, bpsk):
        s_bb, t = bpsk.modulate_time_domain([0xAB], L)
        np.testing.assert_array_equal(t, np.arange(len(t)))

    def test_nrz_symbols_are_plus_minus_one(self, bpsk):
        """After rectangular pulse shaping every sample must be +1 or -1."""
        data = [0xA5]
        s_bb, t = bpsk.modulate_time_domain(data, L)
        unique = set(np.unique(s_bb))
        assert unique == {-1.0, 1.0}

    def test_all_zeros_gives_minus_one(self, bpsk):
        s_bb, t = bpsk.modulate_time_domain([0x00], L)
        np.testing.assert_array_equal(s_bb, -np.ones(8 * L))

    def test_all_ones_gives_plus_one(self, bpsk):
        s_bb, t = bpsk.modulate_time_domain([0xFF], L)
        np.testing.assert_array_equal(s_bb, np.ones(8 * L))

# 4. modulate
class TestModulate:
    def test_return_is_tuple_of_three(self, bpsk):
        result = bpsk.modulate([0x00], L)
        assert isinstance(result, tuple) and len(result) == 3

    def test_samples_are_complex64(self, bpsk):
        samples, fs, dur = bpsk.modulate([0xAB], L)
        assert samples.dtype == np.complex64

    def test_samples_are_purely_real(self, bpsk):
        """BPSK at baseband has no imaginary component."""
        samples, fs, dur = bpsk.modulate([0xA5, 0x5A], L)
        np.testing.assert_array_equal(np.imag(samples), 0)

    def test_sample_rate(self, bpsk):
        _, fs, _ = bpsk.modulate([0x00], L)
        assert fs == pytest.approx(bpsk.get_baudrate() * L)

    def test_duration_one_byte(self, bpsk):
        """1 byte = 8 bits; duration = 8 / baudrate."""
        _, _, dur = bpsk.modulate([0x00], L)
        expected = 8 / bpsk.get_baudrate()
        assert dur == pytest.approx(expected)

    def test_duration_scales_with_byte_count(self, bpsk):
        _, _, dur1 = bpsk.modulate([0x00], L)
        _, _, dur4 = bpsk.modulate([0x00] * 4, L)
        assert dur4 == pytest.approx(4 * dur1)

    def test_sample_count(self, bpsk):
        """Number of samples must equal n_bits * L."""
        data = [0xAB, 0xCD]
        samples, _, _ = bpsk.modulate(data, L)
        assert len(samples) == len(data) * 8 * L

    def test_default_oversampling_factor(self, bpsk):
        """Calling modulate without L should use the module-level default."""
        samples, fs, dur = bpsk.modulate([0x00])
        assert len(samples) == 8 * _BPSK_DEFAULT_OVERSAMPLING_FACTOR

# 5. demodulate
class TestDemodulate:
    def test_output_is_list(self, bpsk):
        samples, _, _ = bpsk.modulate([0xAB], L)
        bits = bpsk.demodulate(samples, L)
        assert isinstance(bits, list)

    def test_output_contains_only_bits(self, bpsk):
        samples, _, _ = bpsk.modulate([0xA5], L)
        bits = bpsk.demodulate(samples, L)
        assert all(b in (0, 1) for b in bits)

    def test_demodulate_zero_byte(self, bpsk):
        samples, _, _ = bpsk.modulate([0x00], L)
        bits = bpsk.demodulate(samples, L)
        assert bits == [0] * 8

    def test_demodulate_full_byte(self, bpsk):
        samples, _, _ = bpsk.modulate([0xFF], L)
        bits = bpsk.demodulate(samples, L)
        assert bits == [1] * 8

    def test_demodulate_known_byte(self, bpsk):
        # 0xA5 = 1010 0101
        samples, _, _ = bpsk.modulate([0xA5], L)
        bits = bpsk.demodulate(samples, L)
        assert bits == [1, 0, 1, 0, 0, 1, 0, 1]

    def test_output_bit_count_equals_input_bit_count(self, bpsk):
        data = [0xDE, 0xAD, 0xBE, 0xEF]
        samples, _, _ = bpsk.modulate(data, L)
        bits = bpsk.demodulate(samples, L)
        assert len(bits) == len(data) * 8

    def test_accepts_imaginary_input(self, bpsk):
        """demodulate should ignore the imaginary part and work correctly."""
        samples, _, _ = bpsk.modulate([0xA5], L)
        noisy = samples + 1j * np.ones_like(samples)  # add imaginary noise
        bits = bpsk.demodulate(noisy, L)
        assert bits == [1, 0, 1, 0, 0, 1, 0, 1]

# 6. Full round-trip: modulate -> demodulate
class TestRoundTrip:
    @pytest.mark.parametrize("data", [
        [0x00],
        [0xFF],
        [0xA5],
        [0x55],
        [0xAA],
        [0xDE, 0xAD, 0xBE, 0xEF],
        list(range(256)),             # all byte values
    ])
    def test_roundtrip_noiseless(self, bpsk, data):
        """Modulating then demodulating must recover the original bits exactly."""
        original_bits = bpsk._int_list_to_bit_list(data)
        samples, _, _ = bpsk.modulate(data, L)
        recovered_bits = bpsk.demodulate(samples, L)
        assert recovered_bits == original_bits

    def test_roundtrip_with_small_awgn(self, bpsk):
        """
        A small amount of additive white Gaussian noise must not flip any bits.
        SNR is kept very high (sigma = 0.05, signal amplitude = 1) so BER = 0.
        """
        rng = np.random.default_rng(seed=42)
        data = list(range(16))  # 16 bytes = 128 bits
        original_bits = bpsk._int_list_to_bit_list(data)
        samples, _, _ = bpsk.modulate(data, L)
        noise = rng.normal(0, 0.05, size=len(samples)).astype(np.float32)
        recovered_bits = bpsk.demodulate(samples + noise, L)
        assert recovered_bits == original_bits

    def test_roundtrip_different_baudrates(self):
        """Round-trip must work regardless of the configured baudrate."""
        data = [0xA5, 0x5A]
        for baud in [100, 1000, 9600, 115200]:
            modem = BPSK(baud=baud)
            original_bits = modem._int_list_to_bit_list(data)
            samples, _, _ = modem.modulate(data, L)
            recovered_bits = modem.demodulate(samples, L)
            assert recovered_bits == original_bits, f"Failed at baudrate={baud}"
