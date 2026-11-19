import json
from pathlib import Path
import sqlite3
import unittest

from pantry import initialize, intake, pickup


class PantryTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        initialize(self.connection)
        self.records = json.loads(Path(__file__).with_name("fixtures.json").read_text())

    def test_replaying_batch_does_not_double_count(self):
        self.assertEqual(intake(self.connection, self.records), 2)
        self.assertEqual(intake(self.connection, self.records), 0)

    def test_conflict_rolls_back_batch(self):
        original, new = self.records
        intake(self.connection, [original])
        with self.assertRaisesRegex(ValueError, "Conflicting donation ID"):
            intake(self.connection, [new, dict(original, boxes=99)])
        self.assertEqual(intake(self.connection, [new]), 1)

    def test_pickup_cannot_be_claimed_by_another_volunteer(self):
        intake(self.connection, self.records)
        pickup(self.connection, "DEMO-001", "volunteer-a")
        pickup(self.connection, "DEMO-001", "volunteer-a")
        with self.assertRaisesRegex(ValueError, "already assigned"):
            pickup(self.connection, "DEMO-001", "volunteer-b")
