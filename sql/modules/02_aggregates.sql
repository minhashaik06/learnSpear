USE learnsphere;

SELECT payment_status,
       COUNT(*) AS payment_count,
       SUM(amount) AS total_amount,
       AVG(amount) AS average_amount,
       MIN(amount) AS smallest_payment,
       MAX(amount) AS largest_payment
FROM Payments
GROUP BY payment_status
HAVING COUNT(*) >= 1
ORDER BY total_amount DESC;

SELECT country, COUNT(*) AS student_count
FROM Students
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY student_count DESC;

SELECT teacher_id,
       COUNT(*) AS class_count,
       SUM(status = 'Cancelled') AS cancelled_count,
       ROUND(100 * AVG(status = 'Cancelled'), 1) AS cancellation_rate_pct
FROM Classes
GROUP BY teacher_id
HAVING COUNT(*) >= 10
ORDER BY cancellation_rate_pct DESC;
