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
    upload_key_type: datamanager_v1.IngestedUserListInfo.UploadKeyType = (
        datamanager_v1.IngestedUserListInfo.UploadKeyType.CONTACT_ID
    ),
    login_account_type: Optional[
        datamanager_v1.ProductAccount.AccountType
    ] = None,
    login_account_id: Optional[str] = None,
    linked_account_type: Optional[
        datamanager_v1.ProductAccount.AccountType
    ] = None,
    linked_account_id: Optional[str] = None,
    key_space: Optional[datamanager_v1.MobileIdInfo.KeySpace] = None,
    app_id: Optional[str] = None,
) -> None:
    """Runs the sample.

    Args:
     operating_account_type: the account type of the operating account.
     operating_account_id: the ID of the operating account.
     validate_only: whether to enable validate_only on the request.
     upload_key_type: the upload key type of the user list.
     login_account_type: the account type of the login account.
     login_account_id: the ID of the login account.
     linked_account_type: the account type of the linked account.
     linked_account_id: the ID of the linked account.
     key_space: the key space of mobile IDs. Required when upload_key_type is
       MOBILE_ID.
     app_id: the mobile application ID. Required when upload_key_type is
       MOBILE_ID.
    """

    # Validates parameters.
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
    if (
        upload_key_type
        == datamanager_v1.IngestedUserListInfo.UploadKeyType.MOBILE_ID
    ):
        if not key_space or not app_id:
            raise ValueError(
                "Must specify both key_space and app_id when upload_key_type "
                "is MOBILE_ID"
            )
    elif key_space or app_id:
        raise ValueError(
            "key_space and app_id are only supported when upload_key_type is "
            "MOBILE_ID"
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
                f"accountTypes/{login_account_type.name}/accounts/{login_account_id}",
            )
        )

    if linked_account_id:
        headers.append(
            (
                "linked-account",
                f"accountTypes/{linked_account_type.name}/accounts/{linked_account_id}",
            )
        )

    # Configures the Customer Match user list.
    # For more details on constructing a UserList, see:
    # https://developers.google.com/data-manager/api/devguides/audiences/google-ads/customer-match/create-audience
    ingested_user_list_info = datamanager_v1.IngestedUserListInfo(
        # Sets to a list containing a single UploadKeyType.
        upload_key_types=[upload_key_type],
    )

    if (
        upload_key_type
        == datamanager_v1.IngestedUserListInfo.UploadKeyType.CONTACT_ID
    ):
        # Use CONTACT_ID for hashed email addresses, phone numbers, or physical
        # addresses.
        ingested_user_list_info.contact_id_info = datamanager_v1.ContactIdInfo(
            data_source_type=(
                datamanager_v1.DataSourceType.DATA_SOURCE_TYPE_FIRST_PARTY
            )
        )
    elif (
        upload_key_type
        == datamanager_v1.IngestedUserListInfo.UploadKeyType.USER_ID
    ):
        # Use USER_ID for first-party user IDs assigned to logged-in users.
        ingested_user_list_info.user_id_info = datamanager_v1.UserIdInfo(
            data_source_type=(
                datamanager_v1.DataSourceType.DATA_SOURCE_TYPE_FIRST_PARTY
            )
        )
    elif (
        upload_key_type
        == datamanager_v1.IngestedUserListInfo.UploadKeyType.MOBILE_ID
    ):
        # Use MOBILE_ID for mobile advertising IDs.
        ingested_user_list_info.mobile_id_info = datamanager_v1.MobileIdInfo(
            data_source_type=(
                datamanager_v1.DataSourceType.DATA_SOURCE_TYPE_FIRST_PARTY
            ),
            key_space=key_space,
            app_id=app_id,
        )
    else:
        raise ValueError(f"Unsupported upload key type: {upload_key_type}")

    user_list = datamanager_v1.UserList(
        # Required. The display name must be unique among all lists owned by the
        # account.
        display_name=(
            f"Customer Match ({upload_key_type.name}) - "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        description=f"Customer Match audience for {upload_key_type.name}",
        # Optional. The duration an audience member remains in the list after
        # being added. Must correspond to whole days (defaults to maximum if
        # not set).
        membership_duration=datetime.timedelta(days=30),
        # Required for a Customer Match audience.
        ingested_user_list_info=ingested_user_list_info,
    )

    # Creates a client for UserListService.
    user_list_client = datamanager_v1.UserListServiceClient()

    # Builds the request targeting the parent operating account.
    request = datamanager_v1.CreateUserListRequest(
        parent=f"accountTypes/{operating_account_type.name}/accounts/{operating_account_id}",
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
        "--upload_key_type",
        choices=["CONTACT_ID", "USER_ID", "MOBILE_ID"],
        default="CONTACT_ID",
        help="The upload key type of the user list. Defaults to 'CONTACT_ID'.",
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
        "--key_space",
        choices=["ANDROID", "IOS"],
        required=False,
        help="The key space of mobile IDs ('ANDROID' or 'IOS'). Required when "
        "--upload_key_type is 'MOBILE_ID'.",
    )
    parser.add_argument(
        "--app_id",
        type=str,
        required=False,
        help="A string that uniquely identifies a mobile application from "
        "which the data was collected (for example, 'com.labpixies.flood' for "
        "Android or '476943146' for iOS). Required when --upload_key_type is "
        "'MOBILE_ID'.",
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
        datamanager_v1.ProductAccount.AccountType[args.operating_account_type],
        args.operating_account_id,
        args.validate_only == "true",
        datamanager_v1.IngestedUserListInfo.UploadKeyType[args.upload_key_type],
        (
            datamanager_v1.ProductAccount.AccountType[args.login_account_type]
            if args.login_account_type
            else None
        ),
        args.login_account_id,
        (
            datamanager_v1.ProductAccount.AccountType[args.linked_account_type]
            if args.linked_account_type
            else None
        ),
        args.linked_account_id,
        (
            datamanager_v1.MobileIdInfo.KeySpace[args.key_space]
            if args.key_space
            else None
        ),
        args.app_id,
    )
