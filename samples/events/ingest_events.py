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
"""Sample of sending an IngestEventsRequest without encryption."""


import argparse
import json
import logging
from typing import Any, Dict, List, Optional

from google.ads import datamanager_v1
from google.ads.datamanager_util import Formatter
from google.ads.datamanager_util.format import Encoding
from google.protobuf.timestamp_pb2 import Timestamp

_logger = logging.getLogger(__name__)

# The maximum number of events allowed per request.
_MAX_EVENTS_PER_REQUEST = 10_000


def main(
    operating_account_type: datamanager_v1.ProductAccount.AccountType,
    operating_account_id: str,
    conversion_action_id: str,
    json_file: str,
    validate_only: bool,
    login_account_type: Optional[
        datamanager_v1.ProductAccount.AccountType
    ] = None,
    login_account_id: Optional[str] = None,
    linked_account_type: Optional[
        datamanager_v1.ProductAccount.AccountType
    ] = None,
    linked_account_id: Optional[str] = None,
) -> None:
    """Runs the sample.
    Args:
     operating_account_type: the account type of the operating account.
     operating_account_id: the ID of the operating account.
     json_file: the JSON file containing event data.
     validate_only: whether to enable validate_only on the request.
     login_account_type: the account type of the login account.
     login_account_id: the ID of the login account.
     linked_account_type: the account type of the linked account.
     linked_account_id: the ID of the linked account.
    """

    # Gets an instance of the formatter.
    formatter: Formatter = Formatter()

    # Reads the input file.
    event_rows: List[Dict[str, Any]] = read_event_data_file(json_file)
    events: List[datamanager_v1.Event] = []
    for event_row in event_rows:
        event = datamanager_v1.Event()
        try:
            event_timestamp = Timestamp()
            event_timestamp.FromJsonString(str(event_row["timestamp"]))
            event.event_timestamp = event_timestamp
        except ValueError:
            _logger.warning(
                "Invalid timestamp format: %s. Skipping row.",
                event_row["timestamp"],
            )
            continue

        if "transactionId" not in event_row:
            _logger.warning("Skipping event with no transaction ID")
            continue
        event.transaction_id = event_row["transactionId"]

        if "eventSource" in event_row:
            event.event_source = event_row["eventSource"]

        if "gclid" in event_row:
            event.ad_identifiers = datamanager_v1.AdIdentifiers(
                gclid=event_row["gclid"]
            )

        if "currency" in event_row:
            event.currency = event_row["currency"]

        if "value" in event_row:
            event.conversion_value = event_row["value"]

        user_data = datamanager_v1.UserData()
        # Adds a UserIdentifier for each valid email address for the event row.
        if "emails" in event_row:
            for email in event_row["emails"]:
                try:
                    processed_email: str = formatter.process_email_address(
                        email, Encoding.HEX
                    )
                    user_data.user_identifiers.append(
                        datamanager_v1.UserIdentifier(
                            email_address=processed_email
                        )
                    )
                except ValueError:
                    # Skips invalid input.
                    _logger.warning(
                        "Invalid email address: %s. Skipping.",
                        event_row["email_address"],
                    )

        # Adds a UserIdentifier for each valid phone number for the event row.
        if "phoneNumbers" in event_row:
            for phone_number in event_row["phoneNumbers"]:
                try:
                    processed_phone: str = formatter.process_phone_number(
                        phone_number, Encoding.HEX
                    )
                    user_data.user_identifiers.append(
                        datamanager_v1.UserIdentifier(
                            phone_number=processed_phone
                        )
                    )
                except ValueError:
                    # Skips invalid input.
                    _logger.warning(
                        "Invalid phone: %s. Skipping.",
                        event_row["phone_number"],
                    )

        if user_data.user_identifiers:
            event.user_data = user_data

        # Adds the event to the list of events to send in the request.
        events.append(event)

    # Configures the destination.
    destination: datamanager_v1.Destination = datamanager_v1.Destination()
    destination.operating_account.account_type = operating_account_type
    destination.operating_account.account_id = operating_account_id
    destination.product_destination_id = str(conversion_action_id)
    if login_account_type or login_account_id:
        if bool(login_account_type) != bool(login_account_id):
            raise ValueError(
                "Must specify either both or neither of login "
                + "account type and login account ID"
            )
        destination.login_account.account_type = login_account_type
        destination.login_account.account_id = login_account_id
    if linked_account_type or linked_account_id:
        if bool(linked_account_type) != bool(linked_account_id):
            raise ValueError(
                "Must specify either both or neither of linked account "
                + "type and linked account ID"
            )
        destination.linked_account.account_type = linked_account_type
        destination.linked_account.account_id = linked_account_id

    # Creates a client for the ingestion service.
    client: datamanager_v1.IngestionServiceClient = (
        datamanager_v1.IngestionServiceClient()
    )

    # Batches requests to send up to the maximum number of events per
    # request.
    request_count = 0
    for i in range(0, len(events), _MAX_EVENTS_PER_REQUEST):
        request_count += 1
        events_batch = events[i : i + _MAX_EVENTS_PER_REQUEST]
        # Sends the request.
        request: datamanager_v1.IngestEventsRequest = (
            datamanager_v1.IngestEventsRequest(
                destinations=[destination],
                # Adds events from the current batch.
                events=events_batch,
                consent=datamanager_v1.Consent(
                    ad_user_data=datamanager_v1.ConsentStatus.CONSENT_GRANTED,
                    ad_personalization=datamanager_v1.ConsentStatus.CONSENT_GRANTED,
                ),
                # Sets encoding to match the encoding used.
                encoding=datamanager_v1.Encoding.HEX,
                # Sets validate_only. If true, then the Data Manager API only
                # validates the request but doesn't apply changes.
                validate_only=validate_only,
            )
        )

        # Sends the request.
        response: datamanager_v1.IngestEventsResponse = client.ingest_events(
            request=request
        )

        # Logs the response.
        _logger.info("Response for request #%d:\n%s", request_count, response)

    _logger.info("# of requests sent: %d", request_count)


def read_event_data_file(json_file: str) -> List[Dict[str, Any]]:
    """Reads the JSON-formatted event data file.
    Args:
      json_file: the event data file.
    """
    with open(json_file, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    # Configures logging.
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=("Sends events from a JSON file to a destination."),
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
        "--conversion_action_id",
        type=int,
        required=True,
        help="The ID of the conversion action",
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
        "--json_file",
        type=str,
        required=True,
        help="JSON file containing user data to ingest.",
    )
    parser.add_argument(
        "--validate_only",
        choices=["true", "false"],
        default="true",
        help="""Whether to enable validate_only on the request. Must be
        'true' or 'false'. Defaults to 'true'.""",
    )
    args = parser.parse_args()

    main(
        args.operating_account_type,
        args.operating_account_id,
        args.conversion_action_id,
        args.json_file,
        args.validate_only == "true",
        args.login_account_type,
        args.login_account_id,
        args.linked_account_type,
        args.linked_account_id,
    )
