USE learnsphere;

-- Safe practice transaction: INSERT, UPDATE, DELETE, then ROLLBACK.
-- The sample row is removed and the status change is undone.
START TRANSACTION;

INSERT INTO Payments
    (student_id, amount, payment_date, payment_status, transaction_reference)
VALUES
    (1, 1.00, NOW(), 'Pending', 'TRAINING-ROLLBACK-001');

UPDATE Students
SET status = 'Inactive'
WHERE student_id = 1;

DELETE FROM Payments
WHERE transaction_reference = 'TRAINING-ROLLBACK-001';

ROLLBACK;

-- COMMIT example: a no-op update demonstrates committing a transaction safely.
START TRANSACTION;
UPDATE Students
SET status = status
WHERE student_id = 1;
COMMIT;

-- For real operational corrections, first run a SELECT with the same WHERE clause,
-- then use START TRANSACTION, make the smallest verified change, and COMMIT.
