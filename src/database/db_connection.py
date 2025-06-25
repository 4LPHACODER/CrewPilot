import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import logging

class MockConnection:
    """Mock database connection for development"""
    def __init__(self):
        self.mock_data = {
            'workers': [
                {
                    'id': 1,
                    'name': 'John Doe',
                    'role': 'Developer',
                    'status': 'active',
                    'performance_score': 8.5,
                    'created_at': '2025-06-09 10:00:00'
                },
                {
                    'id': 2,
                    'name': 'Jane Smith',
                    'role': 'Designer',
                    'status': 'active',
                    'performance_score': 9.0,
                    'created_at': '2025-06-09 11:00:00'
                }
            ],
            'activities': [
                {
                    'id': 1,
                    'worker_id': 1,
                    'activity_type': 'task_completion',
                    'description': 'Completed project milestone',
                    'created_at': '2025-06-09 10:30:00'
                },
                {
                    'id': 2,
                    'worker_id': 2,
                    'activity_type': 'bug_fix',
                    'description': 'Fixed critical bug',
                    'created_at': '2025-06-09 11:30:00'
                }
            ],
            'performance_predictions': [
                {
                    'id': 1,
                    'worker_id': 1,
                    'hours_worked': 8.0,
                    'tasks_completed': 5,
                    'efficiency_rate': 0.85,
                    'predicted_score': 8.5,
                    'confidence_score': 0.8,
                    'created_at': '2025-06-09 10:00:00'
                },
                {
                    'id': 2,
                    'worker_id': 2,
                    'hours_worked': 7.5,
                    'tasks_completed': 4,
                    'efficiency_rate': 0.90,
                    'predicted_score': 9.0,
                    'confidence_score': 0.85,
                    'created_at': '2025-06-09 11:00:00'
                },
                {
                    'id': 3,
                    'worker_id': 1,
                    'hours_worked': 8.5,
                    'tasks_completed': 6,
                    'efficiency_rate': 0.88,
                    'predicted_score': 8.8,
                    'confidence_score': 0.82,
                    'created_at': '2025-06-09 12:00:00'
                },
                {
                    'id': 4,
                    'worker_id': 2,
                    'hours_worked': 8.2,
                    'tasks_completed': 5,
                    'efficiency_rate': 0.92,
                    'predicted_score': 9.2,
                    'confidence_score': 0.88,
                    'created_at': '2025-06-09 13:00:00'
                }
            ]
        }

    def cursor(self, dictionary=False):
        return MockCursor(self.mock_data, dictionary)

    def commit(self):
        pass

class MockCursor:
    """Mock cursor for development"""
    def __init__(self, mock_data, dictionary=False):
        self.mock_data = mock_data
        self.dictionary = dictionary
        self.last_query = None
        self.last_params = None
        self.results = []

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        
        # Simple query parsing
        query = query.lower()
        if 'select' in query:
            if 'count(*)' in query:
                if 'workers' in query:
                    if 'status =' in query and "'active'" in query:
                        self.results = [{'count': len([w for w in self.mock_data['workers'] if w['status'] == 'active'])}]
                    elif 'performance_score >=' in query:
                        self.results = [{'count': len([w for w in self.mock_data['workers'] if w['performance_score'] >= 8.0])}]
                    else:
                        self.results = [{'count': len(self.mock_data['workers'])}]
                elif 'activities' in query:
                    self.results = [{'count': len(self.mock_data['activities'])}]
                elif 'performance_predictions' in query:
                    self.results = [{'count': len(self.mock_data['performance_predictions'])}]
            elif 'performance_predictions' in query:
                # Handle JOIN query for performance predictions
                joined_results = []
                for pred in self.mock_data['performance_predictions']:
                    worker = next((w for w in self.mock_data['workers'] if w['id'] == pred['worker_id']), None)
                    if worker:
                        joined_results.append({
                            'id': pred['id'],
                            'worker_id': pred['worker_id'],
                            'worker_name': worker['name'],
                            'hours_worked': pred['hours_worked'],
                            'tasks_completed': pred['tasks_completed'],
                            'efficiency_rate': pred['efficiency_rate'],
                            'predicted_score': pred['predicted_score'],
                            'confidence_score': pred['confidence_score'],
                            'created_at': pred['created_at']
                        })
                self.results = joined_results
            elif 'workers' in query:
                self.results = self.mock_data['workers']
            elif 'activities' in query:
                self.results = self.mock_data['activities']
        elif 'insert' in query:
            if 'workers' in query:
                new_id = len(self.mock_data['workers']) + 1
                self.mock_data['workers'].append({
                    'id': new_id,
                    'name': params[0],
                    'role': params[1],
                    'status': params[2],
                    'performance_score': params[3] if len(params) > 3 else 0.0,
                    'created_at': '2025-06-09 12:00:00'
                })
            elif 'activities' in query:
                new_id = len(self.mock_data['activities']) + 1
                self.mock_data['activities'].append({
                    'id': new_id,
                    'worker_id': params[0],
                    'activity_type': params[1],
                    'description': params[2],
                    'created_at': '2025-06-09 12:00:00'
                })
            elif 'performance_predictions' in query:
                new_id = len(self.mock_data['performance_predictions']) + 1
                worker = next((w for w in self.mock_data['workers'] if w['id'] == params[0]), None)
                self.mock_data['performance_predictions'].append({
                    'id': new_id,
                    'worker_id': params[0],
                    'hours_worked': params[1],
                    'tasks_completed': params[2],
                    'efficiency_rate': params[3],
                    'predicted_score': params[4],
                    'confidence_score': params[5],
                    'created_at': '2025-06-09 12:00:00'
                })

    def fetchone(self):
        return self.results[0] if self.results else None

    def fetchall(self):
        return self.results

    def close(self):
        pass

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="H4ckm3!_",
                database="worker_tracker"
            )
            if self.connection.is_connected():
                logging.info("Successfully connected to MySQL database")
                self.create_tables()
        except Error as e:
            logging.error(f"Error connecting to MySQL database: {str(e)}")
            logging.info("Using mock database connection for development")
            self.use_mock = True
        else:
            self.use_mock = False

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create workers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    performance_score FLOAT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tasks_completed INT DEFAULT 0,
                    tasks_to_complete INT DEFAULT 0
                )
            """)
            
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    worker_id INT,
                    task_description TEXT,
                    is_completed TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (worker_id) REFERENCES workers(id)
                )
            """)
            
            # Create performance_predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    worker_id INT,
                    hours_worked FLOAT,
                    tasks_completed INT,
                    efficiency_rate FLOAT,
                    predicted_score FLOAT,
                    confidence_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (worker_id) REFERENCES workers(id)
                )
            """)
            
            # Create activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    worker_id INT,
                    activity_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    task_id INT,
                    FOREIGN KEY (worker_id) REFERENCES workers(id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            """)
            
            self.connection.commit()
            logging.info("Database tables created successfully")
            
        except Error as e:
            logging.error(f"Error creating tables: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query, params=None):
        """Execute a query and return the result"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            logging.error(f"Error executing query: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()

    def fetch_one(self, query, params=None):
        """Fetch a single row from the database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            logging.error(f"Error fetching one: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()

    def fetch_all(self, query, params=None):
        """Fetch all rows from the database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Error fetching all: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed")

    # Worker Management Methods
    def get_all_workers(self) -> List[Dict[str, Any]]:
        """Get all workers with their details"""
        query = """
            SELECT id, name, role, status, performance_score, created_at
            FROM workers
            ORDER BY created_at DESC
        """
        workers = self.fetch_all(query)
        return [
            {
                'id': worker['id'],
                'name': worker['name'],
                'role': worker['role'],
                'status': worker['status'],
                'performance_score': float(worker['performance_score']),
                'created_at': worker['created_at']
            }
            for worker in workers
        ]
        
    def get_worker_by_id(self, worker_id: int) -> Optional[Dict[str, Any]]:
        """Get a worker by their ID"""
        query = """
            SELECT id, name, role, status, performance_score, created_at
            FROM workers
            WHERE id = %s
        """
        worker = self.fetch_one(query, (worker_id,))
        if worker:
            return {
                'id': worker['id'],
                'name': worker['name'],
                'role': worker['role'],
                'status': worker['status'],
                'performance_score': float(worker['performance_score']),
                'created_at': worker['created_at']
            }
        return None
        
    def add_worker(self, worker_data: Dict[str, Any]) -> Optional[int]:
        """Add a new worker"""
        query = """
            INSERT INTO workers (name, role, status, performance_score, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            worker_data['name'],
            worker_data['role'],
            worker_data['status'],
            worker_data['performance_score'],
            datetime.now()
        )
        
        self.execute_query(query, params)
        return self.fetch_one("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()']
        
    def update_worker(self, worker_id: int, worker_data: Dict[str, Any]) -> bool:
        """Update an existing worker"""
        query = """
            UPDATE workers 
            SET name = %s, role = %s, status = %s, performance_score = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            worker_data['name'],
            worker_data['role'],
            worker_data['status'],
            worker_data['performance_score'],
            datetime.now(),
            worker_id
        )
        
        self.execute_query(query, params)
        return self.fetch_one("SELECT ROW_COUNT()")['ROW_COUNT()'] > 0
        
    def delete_worker(self, worker_id: int) -> bool:
        """Delete a worker"""
        query = "DELETE FROM workers WHERE id = %s"
        self.execute_query(query, (worker_id,))
        return self.fetch_one("SELECT ROW_COUNT()")['ROW_COUNT()'] > 0
        
    def get_worker_stats(self) -> Dict[str, int]:
        """Get worker statistics"""
        stats = {
            'total': 0,
            'active': 0,
            'inactive': 0,
            'on_leave': 0
        }
        
        # Get total workers
        total = self.fetch_one("SELECT COUNT(*) FROM workers")
        if total:
            stats['total'] = total[0]
            
        # Get workers by status
        status_counts = self.fetch_all("""
            SELECT status, COUNT(*) 
            FROM workers 
            GROUP BY status
        """)
        for status, count in status_counts:
            stats[status] = count
            
        return stats
        
    def log_activity(self, description: str, activity_type: str) -> bool:
        """Log an activity"""
        query = """
            INSERT INTO activities (worker_id, activity_type, description, created_at)
            VALUES (%s, %s, %s, %s)
        """
        self.execute_query(query, (None, activity_type, description, datetime.now()))
        return self.fetch_one("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()'] is not None
        
    def get_recent_activities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent activities"""
        query = """
            SELECT id, worker_id, activity_type, description, created_at
            FROM activities
            ORDER BY created_at DESC
            LIMIT %s
        """
        activities = self.fetch_all(query, (limit,))
        return [
            {
                'id': activity['id'],
                'worker_id': activity['worker_id'],
                'activity_type': activity['activity_type'],
                'description': activity['description'],
                'created_at': activity['created_at']
            }
            for activity in activities
        ] 