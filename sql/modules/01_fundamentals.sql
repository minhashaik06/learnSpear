USE learnsphere;

-- SELECT, DISTINCT, ORDER BY, and LIMIT
SELECT student_id, name, country, status
FROM Students
ORDER BY registration_date DESC
LIMIT 20;

SELECT DISTINCT country
FROM Students
WHERE country IS NOT NULL
ORDER BY country;

-- WHERE, LIKE, IN, BETWEEN, and IS NULL
SELECT student_id, name, email
FROM Students
WHERE name LIKE 'A%'
  AND status IN ('Active', 'Inactive')
  AND registration_date BETWEEN '2025-01-01' AND '2026-12-31'
ORDER BY name;

SELECT ticket_id, student_id, issue_type
FROM Support_Tickets
WHERE description IS NULL;
