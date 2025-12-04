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
"""Formatting utilities for the Data Manager API."""

import hashlib
import re
from base64 import standard_b64encode
from enum import Enum
from typing import Optional

from google.ads.datamanager_util.encrypt import Encrypter


class Encoding(Enum):
    HEX = 1
    BASE64 = 2


class Formatter:
    """A utility for normalizing and formatting user data.

    Methods fall into two categories:
        1. Convenience methods named "process_..." that handle all formatting,
           hashing and encoding of a specific type of data in one method call.
           Each of these methods is overloaded with a signature that also
           accepts an "Encrypter" instance that encrypts the data after
           formatting and hashing.
        2. Fine-grained methods such as "format_...", encoding, and hashing
           methods that perform a specific data processing step.

    Using the convenience methods is easier, less error-prone, and more
    concise. For example, compare the two approaches to format, hash, and
    encode an email address:

        # Uses a convenience method.
        result_1 = formatter.process_email_address(email_address, Encoding.HEX)

        # Uses a chain of fine-grained method calls.
        result_2 = formatter.hex_encode(
            formatter.hash_string(formatter.format_email_address(email_address))
        )

    Methods raise "ValueError" when passed invalid input. Since arguments to
    these methods contain user data, exception messages do not include the
    argument values.
    """

    def format_email_address(self, email: str) -> str:
        """Returns the normalized and formatted email address as a string.

        Args:
          email: the email address.
        Raises:
          ValueError: If the provided email address is invalid. Examples of an
            invalid email address include a blank or empty string, a string
            containing intermediate whitespace, or a string that's not of the
            form 'username@domain'.
        """
        if email is None:
            raise ValueError("Email address is None")
        email = email.strip()
        if len(email) == 0:
            raise ValueError("Email address is blank or empty")
        if re.search(r"\s", email):
            raise ValueError("Email address contains intermediate whitespace")
        # Converts to lowercase.
        email = email.lower()
        parts = email.split("@")
        if len(parts) != 2:
            raise ValueError("Email is not of the form user@domain")
        (user, domain) = (parts[0], parts[1])
        if len(user) == 0:
            raise ValueError("Email address without the domain is empty")
        if len(domain) == 0:
            raise ValueError("Domain of email address is empty")
        if domain == "gmail.com" or domain == "googlemail.com":
            # Handles variations of Gmail addresses. See:
            # https://gmail.googleblog.com/2008/03/2-hidden-ways-to-get-more-from-your.html
            # "Create variations of your email address" at:
            # https://support.google.com/a/users/answer/9282734

            # Removes all periods (.).
            user = re.sub("\\.", "", user)
            if len(user) == 0:
                raise ValueError(
                    "Email address without the domain is empty after normalization"
                )
        return f"{user}@{domain}"

    def format_phone_number(self, phone: str) -> str:
        """Returns the normalized and formatted phone number as a string.

        Args:
          phone: the phone number.
        Raises:
          ValueError: If the provided phone number is invalid. Examples of an
            invalid phone number include a blank or empty string, or a string
            containing no digits.
        """
        if phone is None:
            raise ValueError("Phone number is None")
        # Removes all whitespace.
        phone = "".join(phone.split())
        if len(phone) == 0:
            raise ValueError("Phone number is blank or empty")
        phone = re.sub(r"\D", "", phone)
        if len(phone) == 0:
            raise ValueError("Phone number contains no digits")
        return f"+{phone}"

    def format_given_name(self, given_name: str) -> str:
        """Returns the normalized and formatted given name as a string.

        Args:
          given_name: the given name.
        Raises:
          ValueError: If the provided given name is invalid.
        """
        if given_name is None:
            raise ValueError("Given name is None")
        given_name = given_name.strip().lower()
        if not given_name:
            raise ValueError("Given name is blank or empty")
        return given_name

    def format_family_name(self, family_name: str) -> str:
        """Returns the normalized and formatted family name as a string.

        Args:
          family_name: the family name.
        Raises:
          ValueError: If the provided family name is invalid.
        """
        if family_name is None:
            raise ValueError("Family name is None")
        family_name = family_name.strip().lower()
        if not family_name:
            raise ValueError("Family name is blank or empty")
        return family_name

    def format_postal_code(self, postal_code: str) -> str:
        """Returns the normalized and formatted postal code as a string.

        Args:
          postal_code: the postal code.
        Raises:
          ValueError: If the provided postal code is invalid.
        """
        if postal_code is None:
            raise ValueError("Postal code is None")
        postal_code = postal_code.strip()
        if not postal_code:
            raise ValueError("Postal code is blank or empty")
        return postal_code

    def format_region_code(self, region_code: str) -> str:
        """Returns the normalized and formatted region code as a string.

        Args:
          region_code: the region code.
        Raises:
          ValueError: If the provided region code is invalid.
        """
        if region_code is None:
            raise ValueError("Region code is None")
        region_code = region_code.strip().upper()
        if not region_code:
            raise ValueError("Region code is blank or empty")
        if len(region_code) != 2:
            raise ValueError("Region code must be two characters")
        return region_code

    def hash_string(self, s: str) -> bytes:
        """Returns bytes containing the hash of the string.

        Args:
          s: the string to hash.

        Raises:
          ValueError: If the string is None, blank, or empty.
        """
        if s is None:
            raise ValueError("String is None")
        s = "".join(s.split())
        if len(s) == 0:
            raise ValueError("String is blank or empty")
        return hashlib.sha256(s.encode()).digest()

    def hex_encode(self, b: bytes) -> str:
        """Returns the bytes as a hex-encoded string.

        Args:
          b: the bytes to encode.

        Raises:
          ValueError: If the bytes to encode are None or empty.
        """
        if b is None or len(b) == 0:
            raise ValueError("Bytes None or empty")
        return b.hex()

    def base64_encode(self, b: bytes) -> str:
        """Returns the bytes as a Base64-encoded string.

        Args:
          b: the bytes to encode.

        Raises:
          ValueError: If the bytes to encode are None or empty.
        """
        if b is None or len(b) == 0:
            raise ValueError("Bytes None or empty")
        return standard_b64encode(b).decode()

    def process_email_address(
        self,
        email: str,
        encoding: Encoding,
        encrypter: Optional[Encrypter] = None,
    ) -> str:
        """Formats, hashes, and encodes an email address.

        This is a convenience method that combines format_email_address,
        hash_string, and either hex_encode or base64_encode into a single call.

        Args:
            email: The email address to process.
            encoding: The encoding to use.
            encrypter: An optional Encrypter to use for encryption.

        Returns:
            The processed email address.
        """
        formatted_email = self.format_email_address(email)
        if encrypter:
            return self._hash_encode_and_encrypt(
                formatted_email, encoding, encrypter
            )
        return self._hash_and_encode(formatted_email, encoding)

    def process_phone_number(
        self,
        phone_number: str,
        encoding: Encoding,
        encrypter: Optional[Encrypter] = None,
    ) -> str:
        """Formats, hashes, and encodes a phone number.

        This is a convenience method that combines format_phone_number,
        hash_string, and either hex_encode or base64_encode into a single call.

        Args:
            phone_number: The phone number to process.
            encoding: The encoding to use.
            encrypter: An optional Encrypter to use for encryption.

        Returns:
            The processed phone number.
        """
        formatted_phone_number = self.format_phone_number(phone_number)
        if encrypter:
            return self._hash_encode_and_encrypt(
                formatted_phone_number, encoding, encrypter
            )
        return self._hash_and_encode(formatted_phone_number, encoding)

    def process_given_name(
        self,
        given_name: str,
        encoding: Encoding,
        encrypter: Optional[Encrypter] = None,
    ) -> str:
        """Formats, hashes, and encodes a given name.

        Args:
            given_name: The given name to process.
            encoding: The encoding to use.
            encrypter: An optional Encrypter to use for encryption.

        Returns:
            The processed given name.
        """
        formatted_given_name = self.format_given_name(given_name)
        if encrypter:
            return self._hash_encode_and_encrypt(
                formatted_given_name, encoding, encrypter
            )
        return self._hash_and_encode(formatted_given_name, encoding)

    def process_family_name(
        self,
        family_name: str,
        encoding: Encoding,
        encrypter: Optional[Encrypter] = None,
    ) -> str:
        """Formats, hashes, and encodes a family name.

        Args:
            family_name: The family name to process.
            encoding: The encoding to use.
            encrypter: An optional Encrypter to use for encryption.

        Returns:
            The processed family name.
        """
        formatted_family_name = self.format_family_name(family_name)
        if encrypter:
            return self._hash_encode_and_encrypt(
                formatted_family_name, encoding, encrypter
            )
        return self._hash_and_encode(formatted_family_name, encoding)

    def process_region_code(self, region_code: str) -> str:
        """Processes a region code.

        This is a convenience method that simply calls format_region_code.

        Args:
            region_code: The region code to process.

        Returns:
            The processed region code.
        """
        return self.format_region_code(region_code)

    def process_postal_code(self, postal_code: str) -> str:
        """Processes a postal code.

        This is a convenience method that simply calls format_postal_code.

        Args:
            postal_code: The postal code to process.

        Returns:
            The processed postal code.
        """
        return self.format_postal_code(postal_code)

    def _hash_and_encode(
        self, normalized_string: str, encoding: Encoding
    ) -> str:
        """Hashes and encodes a string."""
        hashed_bytes = self.hash_string(normalized_string)
        return self._encode(hashed_bytes, encoding)

    def _hash_encode_and_encrypt(
        self, normalized_string: str, encoding: Encoding, encrypter: Encrypter
    ) -> str:
        """Hashes, encodes, and encrypts a string."""
        hash_base64 = self._hash_and_encode(normalized_string, Encoding.BASE64)
        encrypted_hash = encrypter.encrypt(hash_base64)
        return self._encode(encrypted_hash, encoding)

    def _encode(self, b: bytes, encoding: Encoding) -> str:
        """Encodes bytes using the specified encoding."""
        if encoding == Encoding.HEX:
            return self.hex_encode(b)
        elif encoding == Encoding.BASE64:
            return self.base64_encode(b)
        else:
            raise ValueError(f"Invalid encoding: {encoding}")
