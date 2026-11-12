USE learnsphere;

-- 1. Successful payment but no Active subscription.
SELECT s.student_id, s.name, p.payment_id, p.amount, p.payment_date,
       sub.subscription_id, sub.status AS subscription_status
FROM Students AS s
JOIN Payments AS p ON p.student_id = s.student_id
WHERE p.payment_status = 'Successful'
  AND NOT EXISTS (
      SELECT 1
      FROM Subscriptions AS sub
      WHERE sub.student_id = s.student_id
        AND sub.status = 'Active'
  )
ORDER BY p.payment_date DESC;

-- 2. Failed payment associated with an Active subscription.
SELECT s.student_id, s.name, p.payment_id, p.payment_date, p.amount,
       sub.subscription_id, sub.status AS subscription_status
FROM Payments AS p
JOIN Students AS s ON s.student_id = p.student_id
JOIN Subscriptions AS sub ON sub.student_id = p.student_id
WHERE p.payment_status = 'Failed'
  AND sub.status = 'Active'
ORDER BY p.payment_date DESC;

-- 3. Duplicate transaction references; NULL references are excluded.
SELECT transaction_reference, COUNT(*) AS occurrence_count,
       GROUP_CONCAT(payment_id ORDER BY payment_id) AS payment_ids,
       GROUP_CONCAT(student_id ORDER BY payment_id) AS student_ids
FROM Payments
WHERE transaction_reference IS NOT NULL
GROUP BY transaction_reference
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;

-- 4. Students with multiple failed payment attempts.
SELECT s.student_id, s.name, COUNT(*) AS failed_attempts,
       MIN(p.payment_date) AS first_attempt, MAX(p.payment_date) AS last_attempt
FROM Students AS s
JOIN Payments AS p ON p.student_id = s.student_id
WHERE p.payment_status = 'Failed'
GROUP BY s.student_id, s.name
HAVING COUNT(*) > 1
ORDER BY failed_attempts DESC, last_attempt DESC;

-- 5. Students with more than three absences.
SELECT s.student_id, s.name, COUNT(*) AS absences,
       MIN(c.class_date) AS first_absence, MAX(c.class_date) AS most_recent_absence
FROM Students AS s
JOIN Classes AS c ON c.student_id = s.student_id
WHERE c.status = 'Absent'
GROUP BY s.student_id, s.name
HAVING COUNT(*) > 3
ORDER BY absences DESC;

-- 6. Teachers with high cancellation rates (at least 10 scheduled records, >= 30%).
SELECT t.teacher_id, t.name, t.subject, COUNT(*) AS scheduled_classes,
       SUM(c.status = 'Cancelled') AS cancellations,
       ROUND(100 * AVG(c.status = 'Cancelled'), 1) AS cancellation_rate_pct
FROM Teachers AS t
JOIN Classes AS c ON c.teacher_id = t.teacher_id
GROUP BY t.teacher_id, t.name, t.subject
HAVING COUNT(*) >= 10
   AND AVG(c.status = 'Cancelled') >= 0.30
ORDER BY cancellation_rate_pct DESC, cancellations DESC;

-- 7. High-priority unresolved tickets: critical/high tickets not yet resolved.
SELECT ticket_id, student_id, issue_type, priority, status, created_at,
       TIMESTAMPDIFF(HOUR, created_at, NOW()) AS open_hours
FROM Support_Tickets
WHERE priority IN ('High', 'Critical')
  AND status <> 'Resolved'
ORDER BY FIELD(priority, 'Critical', 'High'), created_at;

-- 8. Tickets taking unusually long to resolve (more than 48 hours).
SELECT ticket_id, student_id, issue_type, priority, created_at, resolved_at,
       ROUND(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60, 1) AS resolution_hours
FROM Support_Tickets
WHERE status = 'Resolved'
  AND resolved_at IS NOT NULL
  AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) > 48
ORDER BY resolution_hours DESC;

-- 9. Expired subscriptions with a successful payment in the last 30 days.
SELECT s.student_id, s.name, sub.subscription_id, sub.end_date,
       p.payment_id, p.amount, p.payment_date
FROM Subscriptions AS sub
JOIN Students AS s ON s.student_id = sub.student_id
JOIN Payments AS p ON p.student_id = sub.student_id
WHERE sub.status = 'Expired'
  AND p.payment_status = 'Successful'
  AND p.payment_date >= NOW() - INTERVAL 30 DAY
ORDER BY p.payment_date DESC;

-- 10. Active subscribers who missed more than three classes.
SELECT s.student_id, s.name, COUNT(c.class_id) AS missed_classes,
       MAX(c.class_date) AS most_recent_missed_class
FROM Students AS s
JOIN Classes AS c ON c.student_id = s.student_id
WHERE c.status = 'Absent'
  AND EXISTS (
      SELECT 1
      FROM Subscriptions AS sub
      WHERE sub.student_id = s.student_id
        AND sub.status = 'Active'
  )
GROUP BY s.student_id, s.name
HAVING COUNT(c.class_id) > 3
ORDER BY missed_classes DESC, most_recent_missed_class DESC;
