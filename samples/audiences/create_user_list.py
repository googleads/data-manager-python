#!/usr/bin/env python
# Copyright 2026 Google LLC
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
"""Sample of creating a user list in an operating account."""

import argparse
import datetime
import logging
from typing import Optional

from google.ads import datamanager_v1

_logger = logging.getLogger(__name__)


# [START create-user-list]
def main(
    operating_account_type: datamanager_v1.ProductAccount.AccountType,
    operating_account_id: str,
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
     validate_only: whether to enable validate_only on the request.
     login_account_type: the account type of the login account.
     login_account_id: the ID of the login account.
     linked_account_type: the account type of the linked account.
     linked_account_id: the ID of the linked account.
    """

    # Validates parameter pairs.
    if bool(login_account_type) != bool(login_account_id):
        raise ValueError(
            "Must specify either both or neither of login account type and "
            "login account ID"
        )
    if bool(linked_account_type) != bool(linked_account_id):
        raise ValueError(
            "Must specify either both or neither of linked account type and "
            "linked account ID"
        )

    # Optional: Sets headers to specify the login-account and linked-account if
    # your credentials aren't for a user in the operating account (for example,
    # when authenticating through a Google Ads manager account or Data Partner
    # account).
    headers = []

    if login_account_id:
        headers.append(
            (
                "login-account",
                f"accountTypes/{login_account_type}/accounts/{login_account_id}",
            )
        )

    if linked_account_id:
        headers.append(
            (
                "linked-account",
                f"accountTypes/{linked_account_type}/accounts/{linked_account_id}",
            )
        )

    # Configures the Customer Match user list for contact information.
    # For more details on constructing a UserList, see:
    # https://developers.google.com/data-manager/api/devguides/audiences/google-ads/customer-match/create-audience
    user_list = datamanager_v1.UserList(
        # Required. The display name must be unique among all lists owned by the
        # account.
        display_name=(
            "Contact info audience - "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        description="Customer Match for contact info",
        # Optional. The duration an audience member remains in the list after
        # being added. Must correspond to whole days (defaults to maximum if
        # not set).
        membership_duration=datetime.timedelta(days=30),
        # Required for a Customer Match audience.
        ingested_user_list_info=datamanager_v1.IngestedUserListInfo(
            # Sets to a list containing a single UploadKeyType. Use CONTACT_ID
            # for hashed email addresses, phone numbers, or physical addresses.
            upload_key_types=[
                datamanager_v1.IngestedUserListInfo.UploadKeyType.CONTACT_ID
            ],
            # Additional metadata required when CONTACT_ID is specified.
            contact_id_info=datamanager_v1.ContactIdInfo(
                data_source_type=(
                    datamanager_v1.DataSourceType.DATA_SOURCE_TYPE_FIRST_PARTY
                )
            ),
        ),
    )

    # Creates a client for UserListService.
    user_list_client = datamanager_v1.UserListServiceClient()

    # Builds the request targeting the parent operating account.
    request = datamanager_v1.CreateUserListRequest(
        parent=f"accountTypes/{operating_account_type}/accounts/{operating_account_id}",
        user_list=user_list,
        # Sets validate_only. If true, then the Data Manager API only
        # validates the request but doesn't apply changes.
        validate_only=validate_only,
    )

    # Sends the request with any configured header metadata.
    response: datamanager_v1.UserList = user_list_client.create_user_list(
        request=request,
        metadata=headers,
    )

    # Logs the created user list. When validate_only is false, response.id
    # contains the created user list ID, which you pass as the
    # product_destination_id in subsequent ingest or remove requests.
    _logger.info("Response:\n%s", response)
    # [END create-user-list]


if __name__ == "__main__":
    # Configures logging.
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Creates a user list in an operating account.",
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
        "--validate_only",
        choices=["true", "false"],
        default="true",
        help="Whether to enable validate_only on the request. Must be 'true' "
        "or 'false'. Defaults to 'true'.",
    )
    args = parser.parse_args()

    main(
        args.operating_account_type,
        args.operating_account_id,
        args.validate_only == "true",
        args.login_account_type,
        args.login_account_id,
        args.linked_account_type,
        args.linked_account_id,
    )
