-- Create database if not exists
CREATE DATABASE IF NOT EXISTS worker_tracker;
USE worker_tracker;

-- Insert sample workers
INSERT INTO workers (name, role, status, performance_score, created_at, tasks_completed, tasks_to_complete) VALUES
    ('John Smith', 'Senior Developer', 'active', 9.2, DATE_SUB(NOW(), INTERVAL 7 DAY), 12, 15),
    ('Sarah Johnson', 'Project Manager', 'active', 8.8, DATE_SUB(NOW(), INTERVAL 7 DAY), 10, 12),
    ('Michael Chen', 'Data Scientist', 'active', 9.5, DATE_SUB(NOW(), INTERVAL 7 DAY), 15, 18),
    ('Emily Davis', 'UX Designer', 'active', 8.5, DATE_SUB(NOW(), INTERVAL 7 DAY), 8, 10),
    ('Robert Wilson', 'DevOps Engineer', 'active', 9.0, DATE_SUB(NOW(), INTERVAL 7 DAY), 11, 14),
    ('Lisa Anderson', 'QA Engineer', 'active', 8.7, DATE_SUB(NOW(), INTERVAL 7 DAY), 9, 11),
    ('David Kim', 'Frontend Developer', 'active', 8.9, DATE_SUB(NOW(), INTERVAL 7 DAY), 10, 13),
    ('Maria Garcia', 'Backend Developer', 'active', 9.1, DATE_SUB(NOW(), INTERVAL 7 DAY), 13, 16),
    ('James Taylor', 'System Architect', 'active', 9.3, DATE_SUB(NOW(), INTERVAL 7 DAY), 14, 17),
    ('Sophie Brown', 'Product Manager', 'active', 8.6, DATE_SUB(NOW(), INTERVAL 7 DAY), 9, 12),
    ('Alex Thompson', 'Mobile Developer', 'on_leave', 8.4, DATE_SUB(NOW(), INTERVAL 7 DAY), 7, 10),
    ('Emma White', 'Data Analyst', 'inactive', 7.8, DATE_SUB(NOW(), INTERVAL 7 DAY), 6, 8);

-- Insert sample activities
INSERT INTO activities (worker_id, activity_type, description, created_at) VALUES
    (1, 'task_completion', 'Completed major feature implementation', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (1, 'bug_fix', 'Fixed critical bug in production', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (2, 'milestone', 'Successfully delivered project milestone', DATE_SUB(NOW(), INTERVAL 3 DAY)),
    (2, 'training', 'Conducted team training session', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (3, 'task_completion', 'Implemented new ML model', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (3, 'optimization', 'Optimized data processing pipeline', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (4, 'task_completion', 'Completed UI redesign', DATE_SUB(NOW(), INTERVAL 4 DAY)),
    (4, 'research', 'Conducted user research', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (5, 'deployment', 'Deployed new infrastructure', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (5, 'automation', 'Automated deployment process', DATE_SUB(NOW(), INTERVAL 3 DAY)),
    (6, 'testing', 'Completed test suite', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (6, 'security', 'Fixed critical security issue', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (7, 'task_completion', 'Implemented responsive design', DATE_SUB(NOW(), INTERVAL 3 DAY)),
    (7, 'optimization', 'Optimized frontend performance', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (8, 'task_completion', 'Scaled backend services', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (8, 'optimization', 'Implemented caching layer', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (9, 'design', 'Designed system architecture', DATE_SUB(NOW(), INTERVAL 4 DAY)),
    (9, 'review', 'Conducted architecture review', DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (10, 'launch', 'Launched new product feature', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (10, 'feedback', 'Gathered user feedback', DATE_SUB(NOW(), INTERVAL 3 DAY));

-- Insert sample performance predictions
INSERT INTO performance_predictions (worker_id, hours_worked, tasks_completed, efficiency_rate, predicted_score, confidence_score, created_at) VALUES
    (1, 160, 12, 0.92, 9.2, 0.85, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (2, 155, 10, 0.88, 8.8, 0.82, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (3, 165, 15, 0.95, 9.5, 0.90, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (4, 150, 8, 0.85, 8.5, 0.80, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (5, 158, 11, 0.90, 9.0, 0.87, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (6, 152, 9, 0.87, 8.7, 0.83, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (7, 156, 10, 0.89, 8.9, 0.85, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (8, 162, 13, 0.91, 9.1, 0.88, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (9, 164, 14, 0.93, 9.3, 0.89, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (10, 151, 9, 0.86, 8.6, 0.81, DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Insert sample tasks
INSERT INTO tasks (worker_id, task_description, is_completed, created_at) VALUES
    (1, 'Feature Implementation', 1, DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (1, 'Bug Fixing', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (2, 'Project Planning', 1, DATE_SUB(NOW(), INTERVAL 3 DAY)),
    (2, 'Team Training', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (3, 'ML Model Development', 1, DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (3, 'Pipeline Optimization', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (4, 'UI Design', 1, DATE_SUB(NOW(), INTERVAL 4 DAY)),
    (4, 'User Research', 1, DATE_SUB(NOW(), INTERVAL 2 DAY)),
    (5, 'Infrastructure Setup', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
    (5, 'Automation Script', 1, DATE_SUB(NOW(), INTERVAL 3 DAY));

-- Drop existing indexes if they exist (commented out to avoid errors with foreign key constraints)
-- DROP INDEX idx_worker_status ON workers;
-- DROP INDEX idx_worker_performance ON workers;
-- DROP INDEX idx_activity_worker ON activities;
-- DROP INDEX idx_activity_timestamp ON activities;
-- DROP INDEX idx_prediction_worker ON performance_predictions;
-- DROP INDEX idx_prediction_created ON performance_predictions;
-- DROP INDEX idx_task_worker ON tasks;
-- DROP INDEX idx_task_created ON tasks;

-- Create indexes for better performance (commented out to avoid duplicate key errors)
-- CREATE INDEX idx_worker_status ON workers(status);
-- CREATE INDEX idx_worker_performance ON workers(performance_score);
-- CREATE INDEX idx_activity_worker ON activities(worker_id);
-- CREATE INDEX idx_activity_timestamp ON activities(created_at);
-- CREATE INDEX idx_prediction_worker ON performance_predictions(worker_id);
-- CREATE INDEX idx_prediction_created ON performance_predictions(created_at);
-- CREATE INDEX idx_task_worker ON tasks(worker_id);
-- CREATE INDEX idx_task_created ON tasks(created_at); 