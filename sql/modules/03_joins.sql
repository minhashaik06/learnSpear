USE learnsphere;

-- INNER JOIN
SELECT s.student_id, s.name, p.payment_id, p.amount, p.payment_status
FROM Students AS s
INNER JOIN Payments AS p ON p.student_id = s.student_id
ORDER BY p.payment_date DESC
LIMIT 25;

-- LEFT JOIN: include students with no subscriptions
SELECT s.student_id, s.name, sub.status AS subscription_status
FROM Students AS s
LEFT JOIN Subscriptions AS sub ON sub.student_id = s.student_id
WHERE sub.subscription_id IS NULL;

-- RIGHT JOIN: include all teachers, even those without classes
SELECT t.teacher_id, t.name, c.class_id, c.status
FROM Classes AS c
RIGHT JOIN Teachers AS t ON t.teacher_id = c.teacher_id
ORDER BY t.teacher_id;

-- CROSS JOIN: representative student/subject combinations
SELECT s.student_id, t.subject
FROM (SELECT student_id FROM Students ORDER BY student_id LIMIT 5) AS s
CROSS JOIN (SELECT DISTINCT subject FROM Teachers) AS t
ORDER BY s.student_id, t.subject;

-- Self join: students registered in the same country
SELECT a.student_id, a.name, b.student_id AS peer_id, b.name AS peer_name, a.country
FROM Students AS a
INNER JOIN Students AS b
    ON a.country = b.country
   AND a.student_id < b.student_id
WHERE a.country IS NOT NULL
ORDER BY a.country, a.student_id
LIMIT 30;

-- Multi-table join
SELECT s.student_id, s.name, p.payment_id, sub.subscription_id,
       p.payment_status, sub.status AS subscription_status
FROM Students AS s
INNER JOIN Payments AS p ON p.student_id = s.student_id
LEFT JOIN Subscriptions AS sub ON sub.student_id = s.student_id
ORDER BY p.payment_date DESC
LIMIT 30;
