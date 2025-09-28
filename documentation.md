# Project Documentation: Skill Exchange Network

## 1. Project Overview

The Skill Exchange Network is a web application designed to facilitate skill sharing among students. It allows users to create profiles, list skills they can teach and skills they want to learn, and connect with other students for knowledge exchange.

## 2. File-by-File Documentation

### `app.py`

This is the main Flask application file. It defines the application's routes and handles the core logic of the web service.

**Key Components:**

*   **Flask App Initialization:** Initializes the Flask app and sets a secret key for session management.
*   **Database Connection:** Includes a helper function to get a database connection from the `db_manager`.
*   **Password Hashing:** Uses `hashlib` to hash user passwords for security.
*   **Routes:**
    *   `/`: The home page.
    *   `/login`: Handles user login.
    *   `/register`: Handles user registration.
    *   `/profile`: Displays the user's profile, including skills and exchanges.
    *   `/browse`: Allows users to browse available skills.
    *   `/skill/<int:skill_id>`: Shows teachers for a specific skill.
    *   `/request_exchange`: Handles requests for skill exchanges.
    *   `/accept_exchange/<int:exchange_id>`: Allows users to accept exchange requests.
    *   `/sessions`: Displays scheduled sessions.
    *   `/logout`: Logs the user out.
    *   `/api/stats`: An API endpoint to get statistics about the platform.
*   **Error Handlers:** Custom error handlers for 404 and 500 errors.

### `database.py`

This file manages the SQLite database for the application.

**Key Components:**

*   **DatabaseManager Class:**
    *   `__init__`: Initializes the database and creates the necessary tables if they don't exist.
    *   `get_connection`: Returns a connection to the SQLite database.
    *   `init_database`: Creates the database schema, including tables for users, skills, user-teaches, user-learns, and exchanges. It also populates the `skills` table with some sample data.
    *   `verify_schema`: A helper function to verify that the `users` table has all the required columns.
*   **db\_manager:** An instance of the `DatabaseManager` class that is used by the main application.

### `check_templates.py`

A utility script to check for balanced blocks in the Jinja2 templates. It iterates through the HTML files in the `templates` directory and counts the occurrences of `{% block %}` and `{% endblock %}` to ensure they match.

### `requirements.txt`

This file lists the Python packages required to run the project.

*   `Flask==2.3.3`
*   `Werkzeug==2.3.7`

### `static/css/style.css`

This file contains the custom CSS for the web application. It defines the color scheme, typography, layout, and animations for the user interface.

### `static/js/script.js`

This file contains the JavaScript code for the application's frontend. It handles dynamic features such as:

*   Animations on scroll.
*   Form validation.
*   Interactive skill tags.
*   Parallax effects.
*   Live counters for statistics.
*   Scheduling functionality for exchange sessions.

### `templates/`

This directory contains the HTML templates for the application.

*   **`base.html`**: The base template that all other templates extend. It includes the common HTML structure, navigation bar, and footer.
*   **`index.html`**: The home page of the application. It displays a welcome message and provides links to register, login, or browse skills.
*   **`login.html`**: The user login page with a form to enter email and password.
*   **`register.html`**: The user registration page with a form to create a new account and specify skills to teach and learn.
*   **`profile.html`**: The user profile page, which displays user information, skills, and exchange requests.
*   **`browse.html`**: A page to browse and search for available skills.
*   **`match.html`**: A page that lists the teachers for a specific skill and allows users to request an exchange.
*   **`sessions.html`**: A page where users can view their scheduled sessions and schedule new ones.

## 3. Database Schema

The application uses a SQLite database with the following tables:

*   **`users`**: Stores user information.
    *   `id`: Primary Key
    *   `name`: User's full name
    *   `email`: User's email (unique)
    *   `password`: Hashed password
    *   `division`: User's division or class
    *   `created_at`: Timestamp of account creation
*   **`skills`**: Stores the skills available on the platform.
    *   `id`: Primary Key
    *   `name`: Name of the skill (unique)
    *   `category`: Category of the skill
*   **`user_teaches`**: Links users to the skills they can teach.
    *   `id`: Primary Key
    *   `user_id`: Foreign Key to `users.id`
    *   `skill_id`: Foreign Key to `skills.id`
    *   `available_time`: When the user is available to teach
*   **`user_learns`**: Links users to the skills they want to learn.
    *   `id`: Primary Key
    *   `user_id`: Foreign Key to `users.id`
    *   `skill_id`: Foreign Key to `skills.id`
*   **`exchanges`**: Stores information about skill exchange requests.
    *   `id`: Primary Key
    *   `teacher_id`: Foreign Key to `users.id`
    *   `learner_id`: Foreign Key to `users.id`
    *   `skill_id`: Foreign Key to `skills.id`
    *   `status`: Status of the exchange (e.g., 'pending', 'accepted')
    *   `session_time`: Scheduled time for the session
    *   `created_at`: Timestamp of the exchange request

## 4. How to Run the Application

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Application:**
    ```bash
    python app.py
    ```
3.  **Access the Application:**
    Open a web browser and go to `http://127.0.0.1:5000`.
