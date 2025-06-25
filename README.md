# CrewPilot - Developer Tracker Management System

A comprehensive system for tracking and managing developers, built with Flet, MySQL, and Machine Learning capabilities.

## Features

- Interactive Dashboard
- Worker Management
- Machine Learning Predictions
- Database Integration
- Utility Functions

## Project Structure

```
CTMS/
├── src/
│   ├── dashboard/
│   ├── worker_management/
│   ├── ml_prediction/
│   ├── database/
│   └── utils/
├── config/
├── tests/
├── requirements.txt
└── README.md
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update database credentials and other configurations

4. Run the application:
```bash
python src/main.py
```

## Development

- `src/dashboard/`: Dashboard UI components and logic
- `src/worker_management/`: Worker management features
- `src/ml_prediction/`: Machine learning models and predictions
- `src/database/`: Database connection and operations
- `src/utils/`: Utility functions and helpers

## License

MIT License 
