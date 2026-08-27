#!/usr/bin/env python
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
"""Sample of sending an IngestAudienceMembersRequest with the option to use encryption."""

import argparse
import json
import logging
from typing import Any, Dict, List, Optional

from google.ads import datamanager_v1
from google.ads.datamanager_util import Encrypter
from google.ads.datamanager_util import Formatter
from google.ads.datamanager_util.format import Encoding
from google.protobuf.timestamp_pb2 import Timestamp

_logger = logging.getLogger(__name__)

# The maximum number of audience members allowed per request.
_MAX_MEMBERS_PER_REQUEST = 10_000


def main(
    operating_account_type: str,
    operating_account_id: str,
    audience_id: str,
    json_file: str,
    validate_only: bool,
    login_account_type: Optional[str] = None,
    login_account_id: Optional[str] = None,
    linked_account_type: Optional[str] = None,
    linked_account_id: Optional[str] = None,
    key_uri: str = None,
    wip_provider: str = None,
) -> None:
    """Runs the sample.

    Args:
     operating_account_type: the account type of the operating account.
     operating_account_id: the ID of the operating account.
     audience_id: the ID of the destination audience.
     json_file: the JSON file containing member data.
     validate_only: whether to enable validate_only on the request.
     login_account_type: the account type of the login account.
     login_account_id: the ID of the login account.
     linked_account_type: the account type of the linked account.
     linked_account_id: the ID of the linked account.
     key_uri: the URI of the Google Cloud KMS key.
     wip_provider: the Workload Identity Pool provider name. Must follow the pattern:
       projects/PROJECT_ID/locations/global/workloadIdentityPools/WIP_ID/providers/PROVIDER_ID
    """

    # Validates parameter pairs.
    if bool(login_account_type) != bool(login_account_id):
        raise ValueError(
            "Must specify either both or neither of login account type and login account ID"
        )
    if bool(linked_account_type) != bool(linked_account_id):
        raise ValueError(
            "Must specify either both or neither of linked account type and linked account ID"
        )
    if bool(key_uri) != bool(wip_provider):
        raise ValueError(
            "Must specify either both or neither of key URI and WIP provider"
        )

    # Gets an instance of the formatter.
    formatter: Formatter = Formatter()

    # Determines if encryption parameters are set.
    use_encryption: bool = key_uri and wip_provider

    encrypter: Encrypter = None
    if use_encryption:
        # Creates an instance of the encryption utility.
        encrypter = Encrypter.create_for_gcp_kms(key_uri)

    # Reads the input file.
    member_rows: List[Dict[str, Any]] = read_member_data(json_file)
    audience_members: List[datamanager_v1.AudienceMember] = []
    member_row: Dict[str, Any]
    for member_row in member_rows:
        composite_data = datamanager_v1.CompositeData()
        user_data = datamanager_v1.UserData()
        email: str
        for email in member_row.get("emails", []):
            try:
                processed_email: str = formatter.process_email_address(
                    email, Encoding.HEX, encrypter
                )
                user_data.user_identifiers.append(
                    datamanager_v1.UserIdentifier(email_address=processed_email)
                )
            except ValueError:
                # Skips invalid input.
                continue
        phone: str
        for phone in member_row.get("phoneNumbers", []):
            try:
                processed_phone: str = formatter.process_phone_number(
                    phone, Encoding.HEX, encrypter
                )
                user_data.user_identifiers.append(
                    datamanager_v1.UserIdentifier(phone_number=processed_phone)
                )
            except ValueError:
                # Skips invalid input.
                continue

        for ip_info in member_row.get("ipInfos", []):
            if (
                operating_account_type
                != datamanager_v1.ProductAccount.AccountType.GOOGLE_ADS.name
            ):
                _logger.info(
                    "Skipping IP address information for operating account type %s. "
                    "Sending IP address is only supported for operating account type GOOGLE_ADS.",
                    operating_account_type,
                )
                continue

            ip_address = ip_info.get("ipAddress", "").strip()
            if not ip_address:
                _logger.info(
                    "Skipping IP address information with no IP address"
                )
                continue

            ip_data = datamanager_v1.IpData(ip_address=ip_address)

            start_time_str = ip_info.get("observeStartTime", "").strip()
            if start_time_str:
                try:
                    start_time = Timestamp()
                    start_time.FromJsonString(start_time_str)
                    ip_data.observe_start_time = start_time
                except ValueError:
                    _logger.info(
                        "Ignoring observe start time '%s' since it can't be parsed",
                        start_time_str,
                    )

            end_time_str = ip_info.get("observeEndTime", "").strip()
            if end_time_str:
                try:
                    end_time = Timestamp()
                    end_time.FromJsonString(end_time_str)
                    ip_data.observe_end_time = end_time
                except ValueError:
                    _logger.info(
                        "Ignoring observe end time '%s' since it can't be parsed",
                        end_time_str,
                    )

            composite_data.ip_data.append(ip_data)

        if user_data.user_identifiers or composite_data.ip_data:
            if user_data.user_identifiers:
                composite_data.user_data = user_data
            audience_member = datamanager_v1.AudienceMember(
                composite_data=composite_data
            )
            audience_members.append(audience_member)

    # Configures the destination.
    destination: datamanager_v1.Destination = datamanager_v1.Destination()
    destination.operating_account.account_type = operating_account_type
    destination.operating_account.account_id = operating_account_id
    if login_account_type or login_account_id:
        destination.login_account.account_type = login_account_type
        destination.login_account.account_id = login_account_id
    if linked_account_type or linked_account_id:
        destination.linked_account.account_type = linked_account_type
        destination.linked_account.account_id = linked_account_id

    destination.product_destination_id = audience_id

    # Configures the EncryptionInfo for the request if encryption parameters provided.
    if use_encryption:
        encryption_info: datamanager_v1.EncryptionInfo = (
            datamanager_v1.EncryptionInfo(
                gcp_wrapped_key_info=datamanager_v1.GcpWrappedKeyInfo(
                    kek_uri=key_uri,
                    wip_provider=wip_provider,
                    key_type=datamanager_v1.GcpWrappedKeyInfo.KeyType.XCHACHA20_POLY1305,
                    # Sets the encrypted_dek field to the Base64-encoded encrypted DEK.
                    encrypted_dek=formatter.base64_encode(
                        encrypter.encrypted_dek_bytes
                    ),
                )
            )
        )

    # Creates a client for the ingestion service.
    client: datamanager_v1.IngestionServiceClient = (
        datamanager_v1.IngestionServiceClient()
    )

    # Batches requests to send up to the maximum number of audience members per
    # request.
    request_count = 0
    for i in range(0, len(audience_members), _MAX_MEMBERS_PER_REQUEST):
        request_count += 1
        audience_members_batch = audience_members[
            i : i + _MAX_MEMBERS_PER_REQUEST
        ]
        # Sends the request.
        request: datamanager_v1.IngestAudienceMembersRequest = (
            datamanager_v1.IngestAudienceMembersRequest(
                destinations=[destination],
                # Adds members from the current batch.
                audience_members=audience_members_batch,
                consent=datamanager_v1.Consent(
                    ad_user_data=datamanager_v1.ConsentStatus.CONSENT_GRANTED,
                    ad_personalization=datamanager_v1.ConsentStatus.CONSENT_GRANTED,
                ),
                terms_of_service=datamanager_v1.TermsOfService(
                    customer_match_terms_of_service_status=datamanager_v1.TermsOfServiceStatus.ACCEPTED,
                ),
                # Sets encoding to match the encoding used.
                encoding=datamanager_v1.Encoding.HEX,
                # Sets validate_only. If true, then the Data Manager API only
                # validates the request but doesn't apply changes.
                validate_only=validate_only,
            )
        )

        if use_encryption:
            # Sets encryption info on the request.
            request.encryption_info = encryption_info

        # Logs the request.
        _logger.info("Request #%d:\n%s", request_count, request)

        # Sends the request.
        response: datamanager_v1.IngestAudienceMembersResponse = (
            client.ingest_audience_members(request=request)
        )

        # Logs the response.
        _logger.info("Response for request #%d:\n%s", request_count, response)

        if response.field_warnings:
            _logger.warning(
                "Request ingested successfully, but field warnings were returned. "
                "Review warning details and update your implementation as needed."
            )

    _logger.info("# of requests sent: %d", request_count)


def read_member_data(json_file: str) -> List[Dict[str, Any]]:
    """Reads the JSON member data file.

    Args:
      json_file: the member data file. Expected format is a JSON array of
        objects, where each object can contain "emails" and "phoneNumbers"
        arrays.
    """
    with open(json_file, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    # Configures logging.
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=(
            "Sends audience members from a CSV file to a destination."
        ),
        fromfile_prefix_chars="@",
    )
    # The following argument(s) should be provided to run the example.
    parser.add_argument(
        "--operating_account_type",
        type=str,
        required=True,
        help="The account type of the operating account.",
    )
    parser.add_argument(
        "--operating_account_id",
        type=str,
        required=True,
        help="The ID of the operating account.",
    )
    parser.add_argument(
        "--login_account_type",
        type=str,
        required=False,
        help="The account type of the login account.",
    )
    parser.add_argument(
        "--login_account_id",
        type=str,
        required=False,
        help="The ID of the login account.",
    )
    parser.add_argument(
        "--linked_account_type",
        type=str,
        required=False,
        help="The account type of the linked account.",
    )
    parser.add_argument(
        "--linked_account_id",
        type=str,
        required=False,
        help="The ID of the linked account.",
    )
    parser.add_argument(
        "--audience_id",
        type=str,
        required=True,
        help="The ID of the destination audience.",
    )
    parser.add_argument(
        "--json_file",
        type=str,
        required=True,
        help="JSON file containing user data to ingest.",
    )
    parser.add_argument(
        "--key_uri",
        type=str,
        required=False,
        help="URI of the Google Cloud KMS key for encrypting data. If this parameter is set, you "
        + "must also set the --wip_provider parameter.",
    )
    parser.add_argument(
        "--wip_provider",
        type=str,
        required=False,
        help="Workload Identity Pool provider name for encrypting data. If this parameter is set, "
        + "you must also set the --key_uri parameter. The argument for this parameter must follow "
        + "the pattern: "
        + "projects/PROJECT_ID/locations/global/workloadIdentityPools/WIP_ID/providers/PROVIDER_ID",
    )
    parser.add_argument(
        "--validate_only",
        choices=["true", "false"],
        default="true",
        help="Whether to enable validate_only on the request. Must be 'true' or 'false'. "
        + "Defaults to 'true'.",
    )
    args = parser.parse_args()

    main(
        args.operating_account_type,
        args.operating_account_id,
        args.audience_id,
        args.json_file,
        args.validate_only == "true",
        args.login_account_type,
        args.login_account_id,
        args.linked_account_type,
        args.linked_account_id,
        args.key_uri,
        args.wip_provider,
    )
