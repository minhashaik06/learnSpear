USE learnsphere;

-- Scalar subquery: payments above the platform-wide average
SELECT payment_id, student_id, amount
FROM Payments
WHERE amount > (SELECT AVG(amount) FROM Payments)
ORDER BY amount DESC;

-- Correlated subquery: each student's latest payment
SELECT p.payment_id, p.student_id, p.amount, p.payment_date
FROM Payments AS p
WHERE p.payment_date = (
    SELECT MAX(p2.payment_date)
    FROM Payments AS p2
    WHERE p2.student_id = p.student_id
);

-- CASE WHEN
SELECT payment_id, amount,
       CASE
           WHEN amount >= 100 THEN 'High value'
           WHEN amount >= 50 THEN 'Standard'
           ELSE 'Low value'
       END AS payment_band
FROM Payments;

-- CTE and window functions: rank teachers by cancellation rate
WITH teacher_rates AS (
    SELECT t.teacher_id, t.name, t.subject,
           COUNT(c.class_id) AS class_count,
           AVG(c.status = 'Cancelled') AS cancellation_rate
    FROM Teachers AS t
    LEFT JOIN Classes AS c ON c.teacher_id = t.teacher_id
    GROUP BY t.teacher_id, t.name, t.subject
)
SELECT teacher_id, name, subject, class_count,
       ROUND(100 * cancellation_rate, 1) AS cancellation_rate_pct,
       ROW_NUMBER() OVER (ORDER BY cancellation_rate DESC) AS row_num,
       RANK() OVER (ORDER BY cancellation_rate DESC) AS rate_rank,
       DENSE_RANK() OVER (ORDER BY cancellation_rate DESC) AS dense_rate_rank
FROM teacher_rates
ORDER BY rate_rank, teacher_id;

-- LAG and LEAD: compare each payment to the student's adjacent payment
SELECT student_id, payment_id, payment_date, amount,
       LAG(amount) OVER (PARTITION BY student_id ORDER BY payment_date) AS prior_amount,
       LEAD(amount) OVER (PARTITION BY student_id ORDER BY payment_date) AS next_amount
FROM Payments
ORDER BY student_id, payment_date;
