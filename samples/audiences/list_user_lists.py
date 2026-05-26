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
"""Sample of retrieving all user lists from an operating account."""


import argparse
import logging
from typing import Dict, List, Optional

from google.ads import datamanager_v1

_logger = logging.getLogger(__name__)


# [START list-user-lists]
def main(
    operating_account_type: datamanager_v1.ProductAccount.AccountType,
    operating_account_id: str,
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
     login_account_type: the account type of the login account.
     login_account_id: the ID of the login account.
     linked_account_type: the account type of the linked account.
     linked_account_id: the ID of the linked account.
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

    # Creates a dictionary to pass header metadata.
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

    # Creates a client for UserListService.
    user_list_client = datamanager_v1.UserListServiceClient()

    # Sends the request. The client library returns an iterator that automatically fetches all
    # response pages.
    response_pager: iter = user_list_client.list_user_lists(
        parent=f"accountTypes/{operating_account_type}/accounts/{operating_account_id}",
        metadata=headers,
    )

    user_list_num = 0
    for user_list in response_pager:
        user_list_num += 1
        _logger.info("User list #%d:\n%s\n", user_list_num, user_list)

    _logger.info("Total count of user list resources: %d", user_list_num)
    # [END list-user-lists]


if __name__ == "__main__":
    # Configures logging.
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=("Retrieves all users lists from an operating account."),
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
    args = parser.parse_args()

    main(
        args.operating_account_type,
        args.operating_account_id,
        args.login_account_type,
        args.login_account_id,
        args.linked_account_type,
        args.linked_account_id,
    )
