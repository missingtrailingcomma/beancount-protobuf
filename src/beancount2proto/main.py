"""A script to convert a Beancount ledger file into a protobuf format"""

import argparse
from datetime import datetime, time, timezone

from beancount import loader
from beancount.core.data import Close, Open
from google.protobuf.timestamp_pb2 import Timestamp

from protos import account_pb2, user_pb2


def analyze_ledger(input_filename):
    """Analyze a Beancount ledger file."""

    print(f"Parsing {input_filename}...")

    directives, errors, options_map = loader.load_file(input_filename)

    if errors:
        raise ValueError(f"Parsing errors: {errors}")

    print(f"Successfully parsed {len(directives)} total entries.\n")

    print(f"options_map: {options_map}\n")

    user = user_pb2.User()

    # Gather accounts.
    opens = [directive for directive in directives if isinstance(directive, Open)]
    id_to_account = {directive.account: account_pb2.Account() for directive in opens}

    for directive in opens:
        account = id_to_account[directive.account]
        account.id = directive.account
        account.display_name = directive.account
        account.open_timestamp.FromDatetime(datetime.combine(
            directive.date, time.min, tzinfo=timezone.utc))
        if directive.currencies:
            account.currencies.extend([str(currency)
                                       for currency in directive.currencies])

        # TODO: Add custom fields

        user.accounts.append(account)

    closes = [directive for directive in directives if isinstance(directive, Close)]
    for close in closes:
        account = id_to_account.get(close.account)
        if not account:
            raise ValueError(
                f"Close directive found for account that was not opened: {close.account}")

        account.close_timestamp.FromDatetime(datetime.combine(
            close.date, time.min, tzinfo=timezone.utc))

        if "product_switch_to" in close.meta:
            account.account_switch_to = close.meta["product_switch_to"]

    print(f"User protobuf: {user}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a Beancount file.")
    parser.add_argument("input", help="Path to the Beancount file (.beancount)")
    # parser.add_argument("output", help="Path to the shell script output")
    args = parser.parse_args()

    analyze_ledger(args.input)
    analyze_ledger(args.input)
    analyze_ledger(args.input)
