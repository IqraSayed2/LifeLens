# LifeLens

LifeLens is a web application built with Flask that allows users to track and manage their daily life aspects including activities, habits, mood, nutrition, and more. It provides a dashboard for analytics and personalized recommendations to help users maintain a healthy lifestyle.

## Features

- **User Authentication**: Secure login and registration system
- **Activity Tracking**: Log and monitor daily activities
- **Habit Management**: Create and track habits with logging
- **Mood Tracking**: Record and analyze mood patterns
- **Nutrition Logging**: Track meals and nutritional intake
- **Analytics Dashboard**: Visualize data with charts and insights
- **Personalized Recommendations**: Get suggestions based on tracked data

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Migrate
- **Database**: MySQL (via PyMySQL)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS
- **Deployment**: Ready for deployment with virtual environment

## Setup

### Prerequisites

- Python 3.x
- MySQL Server

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd LifeLens
   ```

2. Create a virtual environment:

   ```bash
   python -m venv env
   ```

3. Activate the virtual environment:

   - On Windows: `env\Scripts\activate`
   - On macOS/Linux: `source env/bin/activate`

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

1. Install and start MySQL Server.

2. Create a database named `lifelens`:

   ```sql
   CREATE DATABASE lifelens;
   ```

3. Update the database URI in `LifeLens/app/__init__.py` if necessary (default is `mysql+pymysql://root:root@localhost/lifelens`).

4. Initialize Flask-Migrate (if not already done):

   ```bash
   flask db init
   ```

5. Create and apply database migrations:

   ```bash
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

   Note: If migrations are already included in the repository, you can skip `flask db init` and `flask db migrate`, and just run `flask db upgrade`.

### Running the Application

```bash
python LifeLens/run.py
```

The application will be available at `http://localhost:5000`.
