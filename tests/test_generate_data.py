import unittest
from datetime import date

from scripts.generate_data import build_dataset


class GenerateDataTests(unittest.TestCase):
    def setUp(self):
        self.data = build_dataset(seed=42, today=date(2026, 11, 12))

    def test_target_row_counts(self):
        self.assertEqual(
            {name: len(frame) for name, frame in self.data.items()},
            {
                "Students": 500,
                "Teachers": 50,
                "Classes": 2000,
                "Payments": 1000,
                "Subscriptions": 500,
                "Support_Tickets": 300,
            },
        )

    def test_payment_and_subscription_anomalies(self):
        payments = self.data["Payments"].set_index("payment_id")
        subscriptions = self.data["Subscriptions"].set_index("student_id")

        self.assertEqual(payments.loc[1, "payment_status"], "Successful")
        self.assertEqual(subscriptions.loc[1, "status"], "Inactive")
        self.assertEqual(payments.loc[2, "payment_status"], "Failed")
        self.assertEqual(subscriptions.loc[2, "status"], "Active")
        self.assertEqual(
            payments.loc[1, "transaction_reference"],
            payments.loc[2, "transaction_reference"],
        )
        self.assertEqual(
            len(payments[(payments["student_id"] == 3) & (payments["payment_status"] == "Failed")]),
            2,
        )
        self.assertEqual(subscriptions.loc[5, "status"], "Expired")
        self.assertEqual(payments.loc[5, "payment_status"], "Successful")

    def test_attendance_ticket_and_teacher_fixtures(self):
        classes = self.data["Classes"]
        tickets = self.data["Support_Tickets"].set_index("ticket_id")
        teacher_one = classes[classes["teacher_id"] == 1]

        self.assertGreater(
            len(classes[(classes["student_id"] == 4) & (classes["status"] == "Absent")]),
            3,
        )
        self.assertGreater(
            len(classes[(classes["student_id"] == 6) & (classes["status"] == "Absent")]),
            3,
        )
        self.assertGreaterEqual(
            len(teacher_one[teacher_one["status"] == "Cancelled"]) / len(teacher_one),
            0.30,
        )
        self.assertEqual(tickets.loc[1, "priority"], "High")
        self.assertNotEqual(tickets.loc[1, "status"], "Resolved")
        self.assertGreater(
            (tickets.loc[2, "resolved_at"] - tickets.loc[2, "created_at"]).total_seconds(),
            48 * 60 * 60,
        )

    def test_seed_reproduces_data(self):
        second_run = build_dataset(seed=42, today=date(2026, 11, 12))
        for table in self.data:
            self.assertTrue(self.data[table].equals(second_run[table]))

    def test_optional_fields_and_status_date_inconsistencies(self):
        subscriptions = self.data["Subscriptions"].set_index("student_id")
        students = self.data["Students"]
        tickets = self.data["Support_Tickets"]

        self.assertTrue(subscriptions.loc[7, "end_date"] < date(2026, 11, 12))
        self.assertEqual(subscriptions.loc[7, "status"], "Active")
        self.assertTrue(subscriptions.loc[8, "end_date"] > date(2026, 11, 12))
        self.assertEqual(subscriptions.loc[8, "status"], "Expired")
        self.assertEqual(subscriptions.loc[9, "status"], "Inactive")
        self.assertTrue(students["country"].isna().any())
        self.assertTrue(tickets["description"].isna().any())


if __name__ == "__main__":
    unittest.main()
