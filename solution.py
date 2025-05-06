import argparse
import bisect
import datetime
import sys

from collections import Counter
from typing import Tuple

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def parse_file(filename: str, date: datetime.date) -> Counter:
    """
    Parses a Quantcast cookie log file and counts the number of cookies
    seen on a specific date.
    Args:
        filename (str): Path to the Quantcast cookie log file.
        date (datetime.date): Date to scan for.
    Returns:
        Counter: A Counter object containing the count of cookies seen on the date.
    """
    seen = Counter()
    with open(filename, "r") as fp:
        # Skip the first line because we are going to try to read the file
        # directly instead of using the csv library
        next(fp)
        lines = fp.readlines()
        # I debated reimplenting bisect here since it doesn't support
        # descending lists but it's probably eaiser to just reverse the list.
        index = bisect.bisect_left(
            lines[::-1],
            date,
            key=lambda x: datetime.datetime.strptime(
                x.split(",")[1].strip(), TIMESTAMP_FORMAT
            ).date(),
        )
        for i in range(len(lines) - index - 1, -1, -1):
            cookie, timestamp = lines[i].strip().split(",")
            timestamp = datetime.datetime.strptime(timestamp, TIMESTAMP_FORMAT).date()
            if date != timestamp:
                break
            seen[cookie] += 1
    
    return seen


def parse_args() -> Tuple[str, datetime.date]:
    """
    Parses command line arguments.
    Returns:
        tuple: A tuple containing the filename and date.
    """
    parser = argparse.ArgumentParser(
        description="Processes a Quantcast cookie log file"
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="filename",
        required=True,
        type=str,
        help="Path to the Quantcast cookie log file",
    )
    parser.add_argument(
        "-d", "--date", dest="date", required=True, type=str, help="Date to scan for"
    )
    args = parser.parse_args()

    try:
        date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print(
            f"Error: Invalid date format '{args.date}'. Expected a YYYY-MM-DD.",
            file=sys.stderr,
        )
        sys.exit(1)

    return args.filename, date


if __name__ == "__main__":
    filename, date = parse_args()
    counts = parse_file(filename, date)
    high = counts.most_common(1)[0][1]
    for cookie in counts:
        if counts[cookie] == high:
            print(cookie)
        else:
            break
