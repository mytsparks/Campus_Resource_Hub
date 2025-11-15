-- =====================================================
-- Database Population Script for Campus Resource Hub
-- Run this script in Supabase SQL Editor
-- =====================================================

-- Password hash for "12341234" (bcrypt)
-- All users will use this password for testing

-- =====================================================
-- 1. CREATE USERS
-- =====================================================

-- Insert 2 Students
INSERT INTO users (name, email, password_hash, role, created_at)
VALUES 
    ('Student One', 'student1@mail.edu', '$2b$12$BWtSLV5JMqD92kl.q9HZeuqGLoaqtiIIbY3TzOhW1ModR/fSYl3Be', 'student', NOW()),
    ('Student Two', 'student2@mail.edu', '$2b$12$BWtSLV5JMqD92kl.q9HZeuqGLoaqtiIIbY3TzOhW1ModR/fSYl3Be', 'student', NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert 2 Staff
INSERT INTO users (name, email, password_hash, role, created_at)
VALUES 
    ('Staff One', 'staff1@mail.edu', '$2b$12$BWtSLV5JMqD92kl.q9HZeuqGLoaqtiIIbY3TzOhW1ModR/fSYl3Be', 'staff', NOW()),
    ('Staff Two', 'staff2@mail.edu', '$2b$12$BWtSLV5JMqD92kl.q9HZeuqGLoaqtiIIbY3TzOhW1ModR/fSYl3Be', 'staff', NOW())
ON CONFLICT (email) DO NOTHING;

-- Get user IDs for reference (assuming they're created in order)
-- Staff One should be user_id 3, Staff Two should be user_id 4
-- Student One should be user_id 1, Student Two should be user_id 2

-- =====================================================
-- 2. CREATE RESOURCES (12 total: 3 of each type)
-- =====================================================

-- Desktop PC Resources (3) - owned by Staff One
INSERT INTO resources (owner_id, title, description, category, location, capacity, images, status, booking_type, created_at)
VALUES 
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Desktop PC - Lab A1',
        'High-performance desktop computer with dual monitors, perfect for software development and data analysis. Includes full Adobe Creative Suite and development tools.',
        'Desktop PC',
        'Computer Lab A, Room 101',
        1,
        'https://storage.googleapis.com/crh-images/uploads/computer.jpg',
        'published',
        'open',
        NOW() - INTERVAL '5 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Desktop PC - Lab A2',
        'Gaming-grade desktop with RTX graphics card, ideal for 3D modeling, video editing, and high-end computing tasks. Includes VR headset compatibility.',
        'Desktop PC',
        'Computer Lab A, Room 102',
        1,
        'https://storage.googleapis.com/crh-images/uploads/computer2.jpg',
        'published',
        'open',
        NOW() - INTERVAL '4 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Desktop PC - Lab B1',
        'Standard office desktop with multiple software suites installed. Suitable for general computing, research, and coursework.',
        'Desktop PC',
        'Computer Lab B, Room 201',
        1,
        'https://storage.googleapis.com/crh-images/uploads/computer3.jpg',
        'published',
        'restricted',
        NOW() - INTERVAL '3 days'
    );

-- Desk Space Resources (3) - owned by Staff One
INSERT INTO resources (owner_id, title, description, category, location, capacity, images, status, booking_type, created_at)
VALUES 
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Study Desk - Library Floor 2',
        'Quiet study desk with power outlets, USB charging ports, and adjustable lighting. Perfect for individual study sessions.',
        'Desk Space',
        'Main Library, Floor 2, Desk 15',
        1,
        'https://storage.googleapis.com/crh-images/uploads/desk.jpg',
        'published',
        'open',
        NOW() - INTERVAL '6 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Study Desk - Library Floor 3',
        'Spacious desk with privacy screen, ideal for focused studying. Includes ergonomic chair and storage cubby.',
        'Desk Space',
        'Main Library, Floor 3, Desk 22',
        1,
        'https://storage.googleapis.com/crh-images/uploads/desk2.jpg',
        'published',
        'open',
        NOW() - INTERVAL '5 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff1@mail.edu'),
        'Study Desk - Student Center',
        'Collaborative desk space that can accommodate small group work. Features whiteboard wall and multiple power outlets.',
        'Desk Space',
        'Student Center, Room 305',
        4,
        'https://storage.googleapis.com/crh-images/uploads/desk3.jpg',
        'published',
        'restricted',
        NOW() - INTERVAL '4 days'
    );

-- Conference Room Resources (3) - owned by Staff Two
INSERT INTO resources (owner_id, title, description, category, location, capacity, images, status, booking_type, created_at)
VALUES 
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Conference Room - Business Hall',
        'Professional meeting room with video conferencing equipment, smart board, and seating for up to 12 people. Perfect for team meetings and presentations.',
        'Conference Room',
        'Business Hall, Room 301',
        12,
        'https://storage.googleapis.com/crh-images/uploads/room.jpg',
        'published',
        'restricted',
        NOW() - INTERVAL '7 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Conference Room - Science Building',
        'Modern conference room with AV equipment, projector, and whiteboard. Accommodates up to 8 people comfortably.',
        'Conference Room',
        'Science Building, Room 205',
        8,
        'https://storage.googleapis.com/crh-images/uploads/room2.jpg',
        'published',
        'open',
        NOW() - INTERVAL '6 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Conference Room - Library',
        'Small meeting room ideal for study groups or small team meetings. Includes whiteboard and presentation screen.',
        'Conference Room',
        'Main Library, Room 401',
        6,
        'https://storage.googleapis.com/crh-images/uploads/room3.jpg',
        'published',
        'open',
        NOW() - INTERVAL '5 days'
    );

-- Whiteboard Resources (3) - owned by Staff Two
INSERT INTO resources (owner_id, title, description, category, location, capacity, images, status, booking_type, created_at)
VALUES 
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Mobile Whiteboard - Hallway A',
        'Large mobile whiteboard on wheels, perfect for brainstorming sessions and group work. Includes markers and eraser.',
        'Whiteboard',
        'Academic Hall, Hallway A',
        10,
        'https://storage.googleapis.com/crh-images/uploads/whiteboard.jpg',
        'published',
        'open',
        NOW() - INTERVAL '4 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Smart Whiteboard - Tech Lab',
        'Interactive smart whiteboard with touch screen capabilities and digital note-taking. Connects to laptops and tablets.',
        'Whiteboard',
        'Technology Lab, Room 150',
        8,
        'https://storage.googleapis.com/crh-images/uploads/whiteboard2.jpg',
        'published',
        'restricted',
        NOW() - INTERVAL '3 days'
    ),
    (
        (SELECT user_id FROM users WHERE email = 'staff2@mail.edu'),
        'Wall Whiteboard - Study Room',
        'Fixed wall-mounted whiteboard in dedicated study room. Perfect for tutoring sessions and collaborative problem-solving.',
        'Whiteboard',
        'Study Commons, Room 12',
        6,
        'https://storage.googleapis.com/crh-images/uploads/whiteboard3.jpg',
        'published',
        'open',
        NOW() - INTERVAL '2 days'
    );

-- =====================================================
-- 3. CREATE EQUIPMENT (optional, for some resources)
-- =====================================================

-- Add equipment to some resources
INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Dual Monitors'
FROM resources WHERE title = 'Desktop PC - Lab A1';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'RTX Graphics Card'
FROM resources WHERE title = 'Desktop PC - Lab A2';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'VR Headset Compatible'
FROM resources WHERE title = 'Desktop PC - Lab A2';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Video Conferencing System'
FROM resources WHERE title = 'Conference Room - Business Hall';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Smart Board'
FROM resources WHERE title = 'Conference Room - Business Hall';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Projector'
FROM resources WHERE title = 'Conference Room - Science Building';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Touch Screen'
FROM resources WHERE title = 'Smart Whiteboard - Tech Lab';

INSERT INTO equipment (resource_id, name)
SELECT resource_id, 'Digital Note-Taking'
FROM resources WHERE title = 'Smart Whiteboard - Tech Lab';

-- =====================================================
-- 4. CREATE PAST BOOKINGS (for review demonstration)
-- =====================================================

-- Past bookings for Student One (completed, can leave reviews)
INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    NOW() - INTERVAL '10 days' + (ROW_NUMBER() OVER () * INTERVAL '1 day'),
    NOW() - INTERVAL '10 days' + (ROW_NUMBER() OVER () * INTERVAL '1 day') + INTERVAL '2 hours',
    'approved',
    NOW() - INTERVAL '12 days',
    NOW() - INTERVAL '8 days'
FROM resources r
WHERE r.category = 'Desktop PC' AND r.title = 'Desktop PC - Lab A1'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '8 days' + INTERVAL '3 hours',
    'approved',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '6 days'
FROM resources r
WHERE r.category = 'Desk Space' AND r.title = 'Study Desk - Library Floor 2'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    NOW() - INTERVAL '6 days',
    NOW() - INTERVAL '6 days' + INTERVAL '4 hours',
    'approved',
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '4 days'
FROM resources r
WHERE r.category = 'Conference Room' AND r.title = 'Conference Room - Science Building'
LIMIT 1;

-- Past bookings for Student Two (completed, can leave reviews)
INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    NOW() - INTERVAL '9 days',
    NOW() - INTERVAL '9 days' + INTERVAL '2 hours',
    'approved',
    NOW() - INTERVAL '11 days',
    NOW() - INTERVAL '7 days'
FROM resources r
WHERE r.category = 'Desktop PC' AND r.title = 'Desktop PC - Lab A2'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '7 days' + INTERVAL '3 hours',
    'approved',
    NOW() - INTERVAL '9 days',
    NOW() - INTERVAL '5 days'
FROM resources r
WHERE r.category = 'Desk Space' AND r.title = 'Study Desk - Library Floor 3'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '5 hours',
    'approved',
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '3 days'
FROM resources r
WHERE r.category = 'Whiteboard' AND r.title = 'Mobile Whiteboard - Hallway A'
LIMIT 1;

-- =====================================================
-- 5. CREATE FUTURE BOOKINGS (for conflict demonstration)
-- =====================================================

-- Future bookings for conflict testing
INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    NOW() + INTERVAL '2 days' + INTERVAL '10 hours',
    NOW() + INTERVAL '2 days' + INTERVAL '12 hours',
    'approved',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day'
FROM resources r
WHERE r.title = 'Desktop PC - Lab A1'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    NOW() + INTERVAL '3 days' + INTERVAL '14 hours',
    NOW() + INTERVAL '3 days' + INTERVAL '16 hours',
    'approved',
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days'
FROM resources r
WHERE r.title = 'Conference Room - Science Building'
LIMIT 1;

INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, created_at, updated_at)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    NOW() + INTERVAL '5 days' + INTERVAL '9 hours',
    NOW() + INTERVAL '5 days' + INTERVAL '11 hours',
    'pending',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days'
FROM resources r
WHERE r.title = 'Smart Whiteboard - Tech Lab'
LIMIT 1;

-- =====================================================
-- 6. CREATE REVIEWS (for aggregate rating demonstration)
-- =====================================================

-- Reviews for Desktop PC - Lab A1 (high ratings)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    5,
    'Excellent computer with all the software I needed. Fast and reliable!',
    NOW() - INTERVAL '8 days'
FROM resources r
WHERE r.title = 'Desktop PC - Lab A1'
LIMIT 1;

-- Reviews for Desktop PC - Lab A2 (mixed ratings)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    4,
    'Great for gaming and video editing. The graphics card is amazing!',
    NOW() - INTERVAL '7 days'
FROM resources r
WHERE r.title = 'Desktop PC - Lab A2'
LIMIT 1;

-- Reviews for Study Desk - Library Floor 2 (good ratings)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    5,
    'Perfect quiet space for studying. The lighting is great and the desk is spacious.',
    NOW() - INTERVAL '6 days'
FROM resources r
WHERE r.title = 'Study Desk - Library Floor 2'
LIMIT 1;

-- Reviews for Study Desk - Library Floor 3 (excellent ratings - top rated)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    5,
    'Best study desk on campus! The privacy screen really helps me focus.',
    NOW() - INTERVAL '5 days'
FROM resources r
WHERE r.title = 'Study Desk - Library Floor 3'
LIMIT 1;

-- Add another review to make it clearly top-rated
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    5,
    'Amazing desk! Very comfortable and well-maintained.',
    NOW() - INTERVAL '4 days'
FROM resources r
WHERE r.title = 'Study Desk - Library Floor 3'
LIMIT 1;

-- Reviews for Conference Room - Science Building
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    4,
    'Good meeting space with all necessary equipment. The projector works well.',
    NOW() - INTERVAL '4 days'
FROM resources r
WHERE r.title = 'Conference Room - Science Building'
LIMIT 1;

-- Reviews for Mobile Whiteboard - Hallway A
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    4,
    'Very useful for group brainstorming sessions. Easy to move around.',
    NOW() - INTERVAL '3 days'
FROM resources r
WHERE r.title = 'Mobile Whiteboard - Hallway A'
LIMIT 1;

-- Reviews for Conference Room - Business Hall (lower ratings for variety)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student1@mail.edu'),
    3,
    'Nice room but the video conferencing system was a bit complicated to set up.',
    NOW() - INTERVAL '2 days'
FROM resources r
WHERE r.title = 'Conference Room - Business Hall'
LIMIT 1;

-- Reviews for Desktop PC - Lab B1 (lower rating)
INSERT INTO reviews (resource_id, reviewer_id, rating, comment, timestamp)
SELECT 
    r.resource_id,
    (SELECT user_id FROM users WHERE email = 'student2@mail.edu'),
    3,
    'Decent computer but some software was outdated. Still functional for basic tasks.',
    NOW() - INTERVAL '1 day'
FROM resources r
WHERE r.title = 'Desktop PC - Lab B1'
LIMIT 1;

-- =====================================================
-- VERIFICATION QUERIES (optional - run to check data)
-- =====================================================

-- Uncomment to verify the data:

-- SELECT 'Users' as table_name, COUNT(*) as count FROM users
-- UNION ALL
-- SELECT 'Resources', COUNT(*) FROM resources
-- UNION ALL
-- SELECT 'Bookings', COUNT(*) FROM bookings
-- UNION ALL
-- SELECT 'Reviews', COUNT(*) FROM reviews
-- UNION ALL
-- SELECT 'Equipment', COUNT(*) FROM equipment;

-- SELECT r.title, r.category, u.name as owner, 
--        COUNT(DISTINCT b.booking_id) as booking_count,
--        COUNT(DISTINCT rev.review_id) as review_count,
--        AVG(rev.rating) as avg_rating
-- FROM resources r
-- LEFT JOIN users u ON r.owner_id = u.user_id
-- LEFT JOIN bookings b ON r.resource_id = b.resource_id
-- LEFT JOIN reviews rev ON r.resource_id = rev.resource_id
-- GROUP BY r.resource_id, r.title, r.category, u.name
-- ORDER BY r.category, r.title;

