CREATE DATABASE IF NOT EXISTS learnsphere
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE learnsphere;

CREATE TABLE IF NOT EXISTS Students (
    student_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    registration_date DATE NOT NULL,
    country VARCHAR(80) NULL,
    status ENUM('Active', 'Inactive', 'Suspended') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (student_id),
    UNIQUE KEY uq_students_email (email),
    KEY idx_students_status_country (status, country)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Teachers (
    teacher_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    subject VARCHAR(80) NOT NULL,
    experience_years TINYINT UNSIGNED NOT NULL,
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (teacher_id),
    KEY idx_teachers_subject_status (subject, status),
    CONSTRAINT chk_teachers_experience CHECK (experience_years <= 60)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Classes (
    class_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_id INT UNSIGNED NOT NULL,
    teacher_id INT UNSIGNED NOT NULL,
    class_date DATETIME NOT NULL,
    status ENUM('Completed', 'Absent', 'Cancelled', 'Rescheduled') NOT NULL,
    PRIMARY KEY (class_id),
    KEY idx_classes_student_date (student_id, class_date),
    KEY idx_classes_teacher_status_date (teacher_id, status, class_date),
    CONSTRAINT fk_classes_student FOREIGN KEY (student_id)
        REFERENCES Students (student_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_classes_teacher FOREIGN KEY (teacher_id)
        REFERENCES Teachers (teacher_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Payments (
    payment_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_id INT UNSIGNED NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATETIME NOT NULL,
    payment_status ENUM('Successful', 'Failed', 'Pending') NOT NULL,
    transaction_reference VARCHAR(100) NULL,
    PRIMARY KEY (payment_id),
    KEY idx_payments_student_date (student_id, payment_date),
    KEY idx_payments_status_date (payment_status, payment_date),
    KEY idx_payments_transaction_reference (transaction_reference),
    CONSTRAINT fk_payments_student FOREIGN KEY (student_id)
        REFERENCES Students (student_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_payments_amount CHECK (amount > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Subscriptions (
    subscription_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_id INT UNSIGNED NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Active', 'Inactive', 'Expired') NOT NULL,
    PRIMARY KEY (subscription_id),
    KEY idx_subscriptions_student_status (student_id, status),
    KEY idx_subscriptions_status_end_date (status, end_date),
    CONSTRAINT fk_subscriptions_student FOREIGN KEY (student_id)
        REFERENCES Students (student_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_subscriptions_dates CHECK (end_date >= start_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Support_Tickets (
    ticket_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_id INT UNSIGNED NOT NULL,
    issue_type VARCHAR(80) NOT NULL,
    description TEXT NULL,
    priority ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    status ENUM('Open', 'In Progress', 'Resolved') NOT NULL DEFAULT 'Open',
    created_at DATETIME NOT NULL,
    resolved_at DATETIME NULL,
    PRIMARY KEY (ticket_id),
    KEY idx_tickets_status_priority_created (status, priority, created_at),
    KEY idx_tickets_student_created (student_id, created_at),
    CONSTRAINT fk_tickets_student FOREIGN KEY (student_id)
        REFERENCES Students (student_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_tickets_resolution_time CHECK (
        resolved_at IS NULL OR resolved_at >= created_at
    ),
    CONSTRAINT chk_tickets_status_resolution CHECK (
        (status = 'Resolved' AND resolved_at IS NOT NULL)
        OR (status <> 'Resolved' AND resolved_at IS NULL)
    )
) ENGINE=InnoDB;
