import argparse
from datetime import date
import json
from pathlib import Path
import sqlite3


def initialize(connection):
    connection.execute(
        "CREATE TABLE IF NOT EXISTS donations ("
        "id TEXT PRIMARY KEY, item TEXT NOT NULL, boxes INTEGER NOT NULL, "
        "expires TEXT NOT NULL, volunteer TEXT)"
    )


def intake(connection, records):
    if not isinstance(records, list):
        raise ValueError("Expected a list of donations")
    added = 0
    with connection:
        for record in records:
            donation_id, item, boxes, expires = (
                record[key] for key in ("id", "item", "boxes", "expires")
            )
            if not all(isinstance(value, str) and value.strip()
                       for value in (donation_id, item)):
                raise ValueError("Donation ID and item must be nonempty text")
            if type(boxes) is not int or boxes < 1:
                raise ValueError("Boxes must be a positive integer")
            expires = date.fromisoformat(expires).isoformat()
            inserted = connection.execute(
                "INSERT INTO donations (id, item, boxes, expires) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(id) DO NOTHING",
                (donation_id, item, boxes, expires),
            ).rowcount
            if not inserted:
                previous = connection.execute(
                    "SELECT item, boxes, expires FROM donations WHERE id = ?",
                    (donation_id,),
                ).fetchone()
                if previous != (item, boxes, expires):
                    raise ValueError(f"Conflicting donation ID: {donation_id}")
            added += inserted
    return added


def pickup(connection, donation_id, volunteer):
    if not volunteer.strip():
        raise ValueError("Volunteer ID must be nonempty")
    with connection:
        updated = connection.execute(
            "UPDATE donations SET volunteer = ? WHERE id = ? "
            "AND (volunteer IS NULL OR volunteer = ?)",
            (volunteer, donation_id, volunteer),
        ).rowcount
        if not updated:
            raise ValueError("Donation is missing or already assigned")


def main():
    parser = argparse.ArgumentParser(description="Pantry donation workflow demo")
    parser.add_argument("database")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("intake").add_argument("batch", type=Path)
    claim = commands.add_parser("pickup")
    claim.add_argument("donation_id")
    claim.add_argument("volunteer")
    args = parser.parse_args()

    connection = sqlite3.connect(args.database)
    try:
        initialize(connection)
        if args.command == "intake":
            count = intake(connection, json.loads(args.batch.read_text(encoding="utf-8")))
            print(f"New donations: {count}")
        else:
            pickup(connection, args.donation_id, args.volunteer)
            print(f"Pickup assigned: {args.donation_id}")
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
