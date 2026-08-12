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
"""Encryption utilities for the Data Manager API."""

import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import tink
import tink.aead
from tink.integration import gcpkms


class Encrypter:
    """Encryption helper object."""

    @classmethod
    def create_for_gcp_kms(
        cls, kek_uri: str, credentials_path: str = None
    ) -> Self:
        """Factory method for use with a Google Cloud KMS.

        Args:
          kek_uri: the URI of the Google Cloud KMS key to use as the key encryption key (KEK).
          credentials_path: the path to the credentials file. If omitted, uses Application Default Credentials.
        """
        tink.aead.register()
        client = gcpkms.GcpKmsClient(kek_uri, credentials_path)
        dek_template = tink.aead.aead_key_templates.XCHACHA20_POLY1305
        dek_keyset_handle = tink.new_keyset_handle(dek_template)

        return cls._create(client, kek_uri, dek_keyset_handle)

    @classmethod
    def _create(
        cls,
        kms_client: tink.KmsClient,
        kek_uri: str,
        dek_keyset_handle: tink.KeysetHandle,
    ) -> Self:
        """Factory method to create a new instance.

        Args:
          kms_client: the Tink KmsClient for the key.
          kek_uri: the URI of the key to use as the key encryption key (KEK).
          dek_keyset_handle: the Tink KeysetHandle for the data encryption key (DEK).
        """
        tink.aead.register()
        # Creates an aead for the DEK.
        dek_aead = dek_keyset_handle.primitive(tink.aead.Aead)
        kek_aead = kms_client.get_aead(kek_uri)
        encrypted_dek_bytes = tink.proto_keyset_format.serialize_encrypted(
            dek_keyset_handle, kek_aead, b""
        )
        return cls(dek_aead, encrypted_dek_bytes)

    def __init__(self, dek_aead: tink.aead.Aead, encrypted_dek_bytes: bytes):
        """Initializer for the Encrypter."""
        self.dek_aead = dek_aead
        self.encrypted_dek_bytes = encrypted_dek_bytes

    def encrypt(self, s: str) -> bytes:
        """Encrypts the provided data.

        Args:
          s: the string to encrypt.
        """
        return self.dek_aead.encrypt(s.encode(), b"")
