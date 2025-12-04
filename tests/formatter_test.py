# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the self.formatter utility."""

from unittest import TestCase
from google.ads.datamanager_util import Formatter, Encoding


class FormatterTest(TestCase):

    def setUp(self):
        super().setUp()
        self.formatter = Formatter()

    def test_format_email_address_valid_inputs(self):
        self.assertEqual(
            "quinny@example.com",
            self.formatter.format_email_address("QuinnY@example.com"),
            "Case should be normalized in name",
        )
        self.assertEqual(
            "quinny@example.com",
            self.formatter.format_email_address("QuinnY@EXAMPLE.com"),
            "Case should be normalized in name",
        )
        self.assertEqual(
            "jeffersonloveshiking@gmail.com",
            self.formatter.format_email_address(
                "Jefferson.Loves.hiking@gmail.com"
            ),
            "Periods should be stripped from gmail.com address",
        )
        self.assertEqual(
            "jeffersonloveshiking@googlemail.com",
            self.formatter.format_email_address(
                "Jefferson.LOVES.Hiking@googlemail.com"
            ),
            "Periods should be stripped from googlemail.com address",
        )

    def test_format_email_address_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.formatter.format_email_address(None)
        with self.assertRaises(ValueError):
            self.formatter.format_email_address("")
        with self.assertRaises(ValueError):
            self.formatter.format_email_address("  ")
        with self.assertRaises(ValueError):
            self.formatter.format_email_address("quinn")
        with self.assertRaises(ValueError):
            self.formatter.format_email_address(" @googlemail.com")
        with self.assertRaises(ValueError):
            self.formatter.format_email_address(" ...@gmail.com")

    def test_format_phone_number_valid_inputs(self):
        cases = [
            ("1 800 555 0100", "+18005550100"),
            ("18005550100", "+18005550100"),
            ("+1 800-555-0100", "+18005550100"),
            ("441134960987", "+441134960987"),
            ("+441134960987", "+441134960987"),
            ("+44-113-496-0987", "+441134960987"),
        ]
        for case in cases:
            self.assertEqual(
                case[1], self.formatter.format_phone_number(case[0])
            )

    def test_format_phone_number_invalid_inputs(self):
        # None
        with self.assertRaises(ValueError):
            self.formatter.format_phone_number(None)
        # Empty
        with self.assertRaises(ValueError):
            self.formatter.format_phone_number("")
        # Blank
        with self.assertRaises(ValueError):
            self.formatter.format_phone_number("  ")
        # No digits
        with self.assertRaises(ValueError):
            self.formatter.format_phone_number(" +A BCD EFG ")

    def test_hash_string_valid_inputs(self):
        self.assertEqual(
            "509e933019bb285a134a9334b8bb679dff79d0ce023d529af4bd744d47b4fd8a",
            self.formatter.hash_string("alexz@example.com").hex(),
        )
        self.assertEqual(
            "fb4f73a6ec5fdb7077d564cdd22c3554b43ce49168550c3b12c547b78c517b30",
            self.formatter.hash_string("+18005550100").hex(),
        )
        self.assertEqual(
            bytes,
            type(self.formatter.hash_string("abc")),
            "hash_string should return a bytes object",
        )

    def test_hash_string_invalid_inputs(self):
        # None
        with self.assertRaises(ValueError):
            self.formatter.hash_string(None)
        # Empty
        with self.assertRaises(ValueError):
            self.formatter.hash_string("")
        # Blank
        with self.assertRaises(ValueError):
            self.formatter.hash_string(" ")
        with self.assertRaises(ValueError):
            self.formatter.hash_string("   ")

    def test_hex_encode_valid_inputs(self):
        self.assertEqual(
            str,
            type(self.formatter.hex_encode("abc".encode())),
            "hex_encode should return a string",
        )
        self.assertEqual(
            "61634b313233", self.formatter.hex_encode("acK123".encode())
        )
        self.assertEqual(
            "3939395f58595a", self.formatter.hex_encode("999_XYZ".encode())
        )

    def test_hex_encode_invalid_inputs(self):
        # None
        with self.assertRaises(ValueError):
            self.formatter.hex_encode(None)
        # Empty
        with self.assertRaises(ValueError):
            self.formatter.hex_encode("".encode())

    def test_base64_encode_valid_inputs(self):
        self.assertEqual(
            str,
            type(self.formatter.base64_encode("abc".encode())),
            "base64_encode should return a string",
        )
        self.assertEqual(
            "YWNLMTIz", self.formatter.base64_encode("acK123".encode())
        )
        self.assertEqual(
            "OTk5X1hZWg==", self.formatter.base64_encode("999_XYZ".encode())
        )

    def test_base64_encode_invalid_inputs(self):
        # None
        with self.assertRaises(ValueError):
            self.formatter.base64_encode(None)
        # Empty
        with self.assertRaises(ValueError):
            self.formatter.base64_encode("".encode())

    def test_process_email_address_valid_inputs_hex_encoding(self):
        encoded_hash = (
            "509e933019bb285a134a9334b8bb679dff79d0ce023d529af4bd744d47b4fd8a"
        )
        variants = [
            "alexz@example.com",
            "  alexz@example.com",
            "  alexz@example.com",
            "  ALEXZ@example.com   ",
            "  alexz@EXAMPLE.com   ",
        ]
        for email_variant in variants:
            self.assertEqual(
                encoded_hash,
                self.formatter.process_email_address(
                    email_variant, Encoding.HEX
                ),
            )

    def test_process_email_address_valid_inputs_base64_encoding(self):
        encoded_hash = "UJ6TMBm7KFoTSpM0uLtnnf950M4CPVKa9L10TUe0/Yo="
        variants = [
            "alexz@example.com",
            "  alexz@example.com",
            "  alexz@example.com",
            "  ALEXZ@example.com   ",
            "  alexz@EXAMPLE.com   ",
        ]
        for email_variant in variants:
            self.assertEqual(
                encoded_hash,
                self.formatter.process_email_address(
                    email_variant, Encoding.BASE64
                ),
            )

    def test_process_phone_number_valid_inputs_hex_encoding(self):
        encoded_hash = (
            "fb4f73a6ec5fdb7077d564cdd22c3554b43ce49168550c3b12c547b78c517b30"
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number("+18005550100", Encoding.HEX),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number(
                "   +1-800-555-0100", Encoding.HEX
            ),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number(
                "1-800-555-0100   ", Encoding.HEX
            ),
        )

    def test_process_phone_number_valid_inputs_base64_encoding(self):
        encoded_hash = "+09zpuxf23B31WTN0iw1VLQ85JFoVQw7EsVHt4xRezA="
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number(
                "+18005550100", Encoding.BASE64
            ),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number(
                "   +1-800-555-0100", Encoding.BASE64
            ),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_phone_number(
                "1-800-555-0100   ", Encoding.BASE64
            ),
        )

    def test_process_given_name_valid_inputs_hex_encoding(self):
        # Hex-encoded hash of "givenname".
        encoded_hash = (
            "128a07bfe2df877c52076e60d7774cf5baaa046c5a6c48daf30ff43ecca2f814"
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_given_name("Givenname", Encoding.HEX),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_given_name("  GivenName  ", Encoding.HEX),
        )

    def test_process_given_name_valid_inputs_base64_encoding(self):
        # Base64-encoded hash of "givenname".
        encoded_hash = "EooHv+Lfh3xSB25g13dM9bqqBGxabEja8w/0Psyi+BQ="
        self.assertEqual(
            encoded_hash,
            self.formatter.process_given_name("Givenname", Encoding.BASE64),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_given_name("  GivenName  ", Encoding.BASE64),
        )

    def test_process_family_name_valid_inputs_hex_encoding(self):
        # Hex-encoded hash of "familyname".
        encoded_hash = (
            "77762c287e61ce065bee5c15464012c6fbe088398b8057627d5577249430d574"
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_family_name("Familyname", Encoding.HEX),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_family_name("  FamilyName ", Encoding.HEX),
        )

    def test_process_family_name_valid_inputs_base64_encoding(self):
        # Base64-encoded hash of "familyname".
        encoded_hash = "d3YsKH5hzgZb7lwVRkASxvvgiDmLgFdifVV3JJQw1XQ="
        self.assertEqual(
            encoded_hash,
            self.formatter.process_family_name("Familyname", Encoding.BASE64),
        )
        self.assertEqual(
            encoded_hash,
            self.formatter.process_family_name(
                "  FamilyName ", Encoding.BASE64
            ),
        )

    def test_process_region_code_valid_inputs(self):
        self.assertEqual("US", self.formatter.process_region_code(" us"))
        self.assertEqual("US", self.formatter.process_region_code(" uS "))

    def test_process_postal_code_valid_inputs(self):
        self.assertEqual(
            "1229-076", self.formatter.process_postal_code("1229-076")
        )
        self.assertEqual(
            "1229-076", self.formatter.process_postal_code(" 1229-076  ")
        )
