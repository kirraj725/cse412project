--  Drop Existing Tables
DROP TABLE IF EXISTS ledger CASCADE;
DROP TABLE IF EXISTS rewards CASCADE;
DROP TABLE IF EXISTS user_transactions CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS users CASCADE;

--  Create Tables

CREATE TABLE users (
    u_userid SERIAL PRIMARY KEY,
    u_name VARCHAR(25) NOT NULL,
    u_email VARCHAR(255) UNIQUE NOT NULL,
    u_phone VARCHAR(15) NOT NULL,
    u_password VARCHAR(128) NOT NULL,
    u_totalpoints INTEGER NOT NULL DEFAULT 0,
    u_isadmin BOOLEAN DEFAULT FALSE,
    -- required for Django auth:
    last_login TIMESTAMP WITH TIME ZONE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE vendors (
    v_vendorid SERIAL PRIMARY KEY,
    v_name VARCHAR(35) NOT NULL,
    v_category VARCHAR(15) NOT NULL
);

CREATE TABLE user_transactions (
    t_transid SERIAL PRIMARY KEY,
    t_userid INTEGER NOT NULL REFERENCES users(u_userid) ON DELETE CASCADE,
    t_vendorid INTEGER NOT NULL REFERENCES vendors(v_vendorid),
    t_type VARCHAR(10) NOT NULL,
    t_amount DECIMAL(15,2) NOT NULL,
    t_location VARCHAR(50) NOT NULL,
    t_date DATE NOT NULL
);

CREATE TABLE rewards (
    r_rewardid SERIAL PRIMARY KEY,
    r_userid INTEGER NOT NULL REFERENCES users(u_userid) ON DELETE CASCADE,
    r_vendorid INTEGER NOT NULL REFERENCES vendors(v_vendorid),
    r_balance DECIMAL(8,2) NOT NULL,
    r_expiration DATE NOT NULL
);

CREATE TABLE ledger (
    l_ledgerid SERIAL PRIMARY KEY,
    l_userid INTEGER NOT NULL REFERENCES users(u_userid) ON DELETE CASCADE,
    l_transid INTEGER REFERENCES user_transactions(t_transid),
    l_changeamt INTEGER NOT NULL,
    l_reason VARCHAR(50) NOT NULL,
    l_date DATE NOT NULL,
    l_expiration DATE
);


--  Populate Sample Data
INSERT INTO users (u_userid, u_name, u_email, u_phone, u_password, u_totalpoints, u_isadmin) VALUES
(1, 'Alice Johnson', 'alice@gmail.com', '4801234567', 'pbkdf2_sha256$1000000$xoAtRKJppPayHRgo8gDTJ0$gwhLURWOLxG8xIq3pXBzSTTKsOy9C/5Or33haCU0Hok=', 10934, TRUE),
(2, 'Bob Smith', 'bob@gmail.com', '4809876543', 'pbkdf2_sha256$1000000$qw68henmEsqeoKsP2uLnF0$Zl4cmEwsz1o+3gkBYCBYQ3oHaaHI/R1O5prsqUH2TM4=', 8850, FALSE),
(3, 'Catherine Lee', 'catherine@gmail.com', '6021237788', 'pbkdf2_sha256$1000000$ijrJlLeMKiCkuHdN1o8puc$2tFsgA+poxrFf7K0BB/ki/SU6wzWW3tOMGfjy6+U9bY=', 16624, FALSE),
(4, 'David Kim', 'davidk@gmail.com', '6029871111', 'pbkdf2_sha256$1000000$sKvXqjLebvRKB1075JpRgm$/D/b9eJPYpcElx9FNSe1Wt/uBWEHz29aRaCTE30DQMM=', 6420, FALSE),
(5, 'Ella Martinez', 'ella@gmail.com', '5202229999', 'pbkdf2_sha256$1000000$oTeB3rUYUXUYQCYtrDNX25$3PToLOGRt39/GdntbXt9U/uxKJIOkFvwvH+CsIFLHMQ=', 19999, FALSE),
(6, 'Frank Wu', 'frankwu@gmail.com', '4806662323', 'pbkdf2_sha256$1000000$P28yHfy6FLdR5ooF1HwQ3J$WxyNrCBENlajjLiaYijQ7MZnxrYWdl/VYMrx+2zwC6M=', 12275, FALSE),
(7, 'Grace Chen', 'gracec@gmail.com', '6235558899', 'pbkdf2_sha256$1000000$eRGiDZUlY5zC9Zd6UH1yZe$RQG7YhSICBOhqFcPXpkuKygLgjS04mzx553hS/4ZyRE=', 3497, FALSE),
(8, 'Henry Lopez', 'henrylopez@gmail.com', '9281114477', 'pbkdf2_sha256$1000000$bKOWwHCquMYHrpNZcsGpQY$dXpvg5AVyba60ql5CBkxPmflpAxq/ZkPP8/d7N0IOrQ=', 21550, FALSE),
(9, 'Isabella Patel', 'isabella@gmail.com', '4803142000', 'pbkdf2_sha256$1000000$bYnnITmzhFGki6QYgOVR3B$FUuwKz7HJHTgBY8TIlOOFMDZgPVTy9weXFihj1VcQMs=', 4750, FALSE),
(10, 'Jack Wilson', 'jackw@gmail.com', '6025551212', 'pbkdf2_sha256$1000000$cqaGijB298fGN5lrWfQtKU$1euIH+AqpvUmgk9mmhFnngKaPmmTLVxtSKhxjNKsp1M=', 30865, FALSE);

INSERT INTO vendors VALUES
(1, 'Starbucks', 'Restaurant'),
(2, 'Target', 'Retail'),
(3, 'Shell Gas', 'Other'),
(4, 'Amazon', 'Online'),
(5, 'Best Buy', 'Retail'),
(6, 'Walmart', 'Retail'),
(7, 'Urban Outfitters', 'Retail'),
(8, 'Wingstop', 'Restaurant'),
(9, 'Chipotle', 'Restaurant'),
(10, 'Sephora', 'Retail');

INSERT INTO user_transactions VALUES
(1, 1, 1, 'Purchase', 5.75, 'Tempe, AZ', '2025-09-10'),
(2, 1, 2, 'Purchase', 42.10, 'Tempe, AZ', '2025-09-10'),
(3, 2, 2, 'Purchase', 63.50, 'Chandler, AZ', '2025-09-12'),
(4, 3, 4, 'Purchase', 120.99, 'Online', '2025-09-15'),
(5, 4, 3, 'Purchase', 55.45, 'Phoenix, AZ', '2025-09-18'),
(6, 2, 4, 'Purchase', 25.00, 'Online', '2025-09-20'),
(7, 5, 5, 'Purchase', 229.99, 'Scottsdale, AZ', '2025-09-20'),
(8, 6, 1, 'Purchase', 8.25, 'Tempe, AZ', '2025-09-21'),
(9, 3, 5, 'Purchase', 45.25, 'Scottsdale, AZ', '2025-09-22'),
(10, 7, 2, 'Purchase', 60.00, 'Goodyear, AZ', '2025-09-25'),
(11, 4, 1, 'Purchase', 8.75, 'Tempe, AZ', '2025-09-25'),
(12, 7, 2, 'Return', -25.03, 'Goodyear, AZ', '2025-09-27'),
(13, 6, 4, 'Purchase', 89.50, 'Online', '2025-09-28'),
(14, 5, 5, 'Return', -30.00, 'Scottsdale, AZ', '2025-09-29'),
(15, 8, 5, 'Purchase', 150.00, 'Phoenix, AZ', '2025-09-30'),
(16, 8, 3, 'Purchase', 65.50, 'Glendale, AZ', '2025-10-02'),
(17, 9, 1, 'Purchase', 7.50, 'Buckeye, AZ', '2025-10-03'),
(18, 10, 5, 'Purchase', 299.99, 'Phoenix, AZ', '2025-10-05'),
(19, 9, 4, 'Purchase', 40.00, 'Online', '2025-10-06'),
(20, 10, 2, 'Purchase', 159.99, 'Mesa, AZ', '2025-10-09'),
(21, 1, 3, 'Purchase', 36.49, 'Avondale, AZ', '2025-10-11'),
(22, 10, 5, 'Purchase', 598.67, 'Phoenix, AZ', '2025-10-15');

INSERT INTO rewards VALUES
(1, 1, 2, 5.00, '2026-01-01'),
(2, 6, 5, 10.00, '2026-02-08'),
(3, 2, 4, 5.00, '2026-02-14'),
(4, 5, 1, 15.00, '2026-04-04'),
(5, 9, 7, 5.00, '2026-05-13'),
(6, 4, 10, 5.00, '2026-06-08'),
(7, 7, 9, 10.00, '2026-08-19'),
(8, 3, 6, 5.00, '2026-09-25'),
(9, 8, 8, 5.00, '2026-09-12'),
(10, 10, 4, 10.00, '2026-10-17');

INSERT INTO ledger VALUES
(1, 1, 1, 575, 'Purchase Points', '2025-09-10', '2026-09-10'),
(2, 1, 2, 4210, 'Purchase Points', '2025-09-10', '2026-09-10'),
(3, 6, NULL, 2500, 'Referral Bonus', '2025-09-11', '2026-09-11'),
(4, 2, 3, 6350, 'Purchase Points', '2025-09-12', '2026-09-12'),
(5, 3, 4, 12099, 'Purchase Points', '2025-09-15', '2026-09-15'),
(6, 4, 5, 5545, 'Purchase Points', '2025-09-18', '2026-09-18'),
(7, 2, 6, 2500, 'Purchase Points', '2025-09-20', '2026-09-20'),
(8, 5, 7, 22999, 'Purchase Points', '2025-09-20', '2026-09-20'),
(9, 6, 8, 825, 'Purchase Points', '2025-09-21', '2026-09-21'),
(10, 1, NULL, 2500, 'Referral Bonus', '2025-09-21', '2026-09-21'),
(11, 3, 9, 4525, 'Purchase Points', '2025-09-22', '2026-09-22'),
(12, 7, 10, 6000, 'Purchase Points', '2025-09-25', '2026-09-25'),
(13, 4, 11, 875, 'Purchase Points', '2025-09-25', '2026-09-25'),
(14, 7, 12, -2503, 'Refund', '2025-09-27', NULL),
(15, 6, 13, 8950, 'Purchase Points', '2025-09-28', '2026-09-28'),
(16, 5, 14, -3000, 'Refund', '2025-09-29', NULL),
(17, 8, 15, 15000, 'Purchase Points', '2025-09-30', '2026-09-30'),
(18, 8, 16, 6550, 'Purchase Points', '2025-10-02', '2026-10-02'),
(19, 9, 17, 750, 'Purchase Points', '2025-10-03', '2026-10-03'),
(20, 10, 18, 29999, 'Purchase Points', '2025-10-05', '2026-10-05'),
(21, 9, 19, 4000, 'Purchase Points', '2025-10-06', '2026-10-06'),
(22, 10, 20, 15999, 'Purchase Points', '2025-10-09', '2026-10-09'),
(23, 1, 21, 3649, 'Purchase Points', '2025-10-11', '2026-10-11'),
(24, 10, 22, 59867, 'Purchase Points', '2025-10-15', '2026-10-15'),
(25, 10, NULL, -75000, 'Credit Redemption', '2025-10-17', NULL);
