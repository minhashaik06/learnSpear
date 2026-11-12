"""Generate deterministic LearnSphere sample data and load it into MySQL."""

from __future__ import annotations

import argparse
import os
import random
from datetime import date, datetime, time, timedelta
from typing import Any

import pandas as pd


COUNTRIES = ["United States", "India", "United Kingdom", "Canada", "Australia", "Singapore"]
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science"]
FIRST_NAMES = [
    "Aarav", "Aisha", "Amelia", "Arjun", "Daniel", "Ethan", "Fatima", "Hana",
    "Ibrahim", "Isabella", "Jia", "Liam", "Maya", "Noah", "Olivia", "Ravi",
    "Sophia", "Wei", "Zara", "Mila",
]
LAST_NAMES = [
    "Adams", "Bennett", "Brown", "Chen", "Clark", "Davis", "Gupta", "Hughes",
    "Johnson", "Khan", "Kim", "Lee", "Martin", "Patel", "Singh", "Taylor",
    "Thomas", "Walker", "Wilson", "Wong",
]


def build_dataset(seed: int = 42, today: date | None = None) -> dict[str, pd.DataFrame]:
    """Return all six target-size tables with stable, documented anomaly fixtures."""
    rng = random.Random(seed)
    today = today or date.today()
    now = datetime.combine(today, time(hour=12))

    def person_name() -> str:
        return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"

    students = []
    for student_id in range(1, 501):
        students.append(
            {
                "student_id": student_id,
                "name": person_name(),
                "email": f"student{student_id:04d}@example.com",
                "registration_date": today - timedelta(days=rng.randint(1, 900)),
                "country": rng.choice(COUNTRIES + [None]),
                "status": rng.choices(
                    ["Active", "Inactive", "Suspended"], weights=[88, 9, 3], k=1
                )[0],
            }
        )

    teachers = []
    for teacher_id in range(1, 51):
        teachers.append(
            {
                "teacher_id": teacher_id,
                "name": person_name(),
                "subject": rng.choice(SUBJECTS),
                "experience_years": rng.randint(1, 30),
                "status": rng.choices(["Active", "Inactive"], weights=[92, 8], k=1)[0],
            }
        )

    subscriptions = []
    for subscription_id in range(1, 501):
        start = today - timedelta(days=rng.randint(0, 400))
        end = start + timedelta(days=rng.randint(30, 180))
        if end < today:
            status = "Expired"
        elif start <= today <= end:
            status = "Active"
        else:
            status = "Inactive"
        subscriptions.append(
            {
                "subscription_id": subscription_id,
                "student_id": subscription_id,
                "start_date": start,
                "end_date": end,
                "status": status,
            }
        )

    # Payment/subscription mismatches and date/status inconsistencies for investigation.
    subscriptions[0].update(start_date=today - timedelta(days=120),
                             end_date=today - timedelta(days=30), status="Inactive")
    subscriptions[1].update(start_date=today - timedelta(days=20),
                             end_date=today + timedelta(days=70), status="Active")
    subscriptions[4].update(start_date=today - timedelta(days=180),
                             end_date=today - timedelta(days=60), status="Expired")
    subscriptions[5].update(start_date=today - timedelta(days=10),
                             end_date=today + timedelta(days=80), status="Active")
    subscriptions[6].update(start_date=today - timedelta(days=120),
                             end_date=today - timedelta(days=5), status="Active")
    subscriptions[7].update(start_date=today - timedelta(days=10),
                             end_date=today + timedelta(days=90), status="Expired")
    subscriptions[8].update(start_date=today - timedelta(days=10),
                             end_date=today + timedelta(days=90), status="Inactive")

    payments = []
    for payment_id in range(1, 1001):
        payment_date = now - timedelta(
            days=rng.randint(0, 365), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
        )
        payments.append(
            {
                "payment_id": payment_id,
                "student_id": rng.randint(1, 500),
                "amount": round(rng.choice([29.99, 49.99, 79.99, 99.99, 149.99]), 2),
                "payment_date": payment_date,
                "payment_status": rng.choices(
                    ["Successful", "Failed", "Pending"], weights=[78, 17, 5], k=1
                )[0],
                "transaction_reference": f"TXN-{payment_id:06d}",
            }
        )

    payments[0].update(student_id=1, payment_status="Successful",
                       payment_date=now - timedelta(days=2),
                       transaction_reference="TXN-DUPLICATE-001")
    payments[1].update(student_id=2, payment_status="Failed",
                       transaction_reference="TXN-DUPLICATE-001")
    payments[2].update(student_id=3, payment_status="Failed")
    payments[3].update(student_id=3, payment_status="Failed")
    payments[4].update(student_id=5, payment_status="Successful",
                       payment_date=now - timedelta(days=2))

    classes = []
    class_statuses = ["Completed", "Absent", "Cancelled", "Rescheduled"]
    for class_id in range(1, 2001):
        class_date = now - timedelta(
            days=rng.randint(0, 180), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
        )
        classes.append(
            {
                "class_id": class_id,
                "student_id": rng.randint(1, 500),
                "teacher_id": rng.randint(1, 50),
                "class_date": class_date,
                "status": rng.choices(class_statuses, weights=[70, 12, 10, 8], k=1)[0],
            }
        )

    # Six absences for student 4, five for active subscriber 6.
    for index in range(6):
        classes[index].update(student_id=4, teacher_id=2, status="Absent")
    for index in range(6, 11):
        classes[index].update(student_id=6, teacher_id=2, status="Absent")
    # A 60% cancellation rate across 40 classes assigned to teacher 1.
    for offset in range(40):
        classes[11 + offset].update(
            teacher_id=1,
            status="Cancelled" if offset < 24 else "Completed",
        )

    tickets = []
    for ticket_id in range(1, 301):
        created_at = now - timedelta(days=rng.randint(0, 90), hours=rng.randint(0, 23))
        status = rng.choices(
            ["Open", "In Progress", "Resolved"], weights=[30, 25, 45], k=1
        )[0]
        resolved_at = None
        if status == "Resolved":
            resolved_at = created_at + timedelta(
                hours=rng.randint(1, 96), minutes=rng.randint(0, 59)
            )
        tickets.append(
            {
                "ticket_id": ticket_id,
                "student_id": rng.randint(1, 500),
                "issue_type": rng.choice(
                    ["Billing", "Login", "Class access", "Scheduling", "Subscription"]
                ),
                "description": (
                    None if rng.random() < 0.08
                    else f"Student reports an issue with {rng.choice(['account access', 'a recent payment', 'class scheduling'])}."
                ),
                "priority": rng.choices(
                    ["Low", "Medium", "High", "Critical"], weights=[20, 45, 28, 7], k=1
                )[0],
                "status": status,
                "created_at": created_at,
                "resolved_at": resolved_at,
            }
        )

    tickets[0].update(student_id=1, issue_type="Subscription", priority="High",
                      status="Open", created_at=now - timedelta(days=20), resolved_at=None)
    tickets[1].update(student_id=5, issue_type="Billing", priority="High",
                      status="Resolved", created_at=now - timedelta(days=60),
                      resolved_at=now - timedelta(days=20))
    tickets[2].update(student_id=6, issue_type="Class access", priority="Critical",
                      status="In Progress", created_at=now - timedelta(days=10),
                      resolved_at=None)

    return {
        "Students": pd.DataFrame(students),
        "Teachers": pd.DataFrame(teachers),
        "Classes": pd.DataFrame(classes),
        "Payments": pd.DataFrame(payments),
        "Subscriptions": pd.DataFrame(subscriptions),
        "Support_Tickets": pd.DataFrame(tickets),
    }


def connect() -> mysql.connector.MySQLConnection:
    import mysql.connector

    required = ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.getenv("MYSQL_DATABASE", "learnsphere"),
        charset="utf8mb4",
    )


def load_dataset(connection: mysql.connector.MySQLConnection,
                 dataset: dict[str, pd.DataFrame], replace: bool = False) -> None:
    delete_order = [
        "Classes", "Payments", "Subscriptions", "Support_Tickets", "Students", "Teachers"
    ]
    cursor = connection.cursor()
    try:
        if replace:
            for table in delete_order:
                cursor.execute(f"DELETE FROM `{table}`")

        # Parents are inserted before dependent rows to satisfy foreign keys.
        insert_order = ["Students", "Teachers", "Classes", "Payments", "Subscriptions", "Support_Tickets"]
        for table in insert_order:
            frame = dataset[table]
            columns = list(frame.columns)
            column_sql = ", ".join(f"`{column}`" for column in columns)
            placeholders = ", ".join(["%s"] * len(columns))
            statement = f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders})"
            rows: list[tuple[Any, ...]] = list(frame.itertuples(index=False, name=None))
            cursor.executemany(statement, rows)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--replace", action="store_true",
        help="Delete existing records from all six tables before loading the generated data",
    )
    args = parser.parse_args()

    if args.replace:
        confirmation = input(
            "This will delete all existing rows in the six LearnSphere tables. Type DELETE to continue: "
        )
        if confirmation != "DELETE":
            raise SystemExit("Data replacement cancelled.")

    dataset = build_dataset(seed=args.seed)
    connection = connect()
    try:
        load_dataset(connection, dataset, replace=args.replace)
    finally:
        connection.close()

    for table, frame in dataset.items():
        print(f"Loaded {len(frame):,} rows into {table}")


if __name__ == "__main__":
    main()
