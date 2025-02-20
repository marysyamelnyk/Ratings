Review Tracker

Review Tracker is a web application for collecting, analyzing, and tracking user feedback. The project is developed using Flask and utilizes SQLite for database management. The app supports user registration, authentication, and error logging, and it is deployed on AWS EC2.

Features
- User registration and authentication
- Collection and storage of feedback in the database
- Feedback filtering and sorting
- Event and error logging
- Deployment on AWS EC2
- Technologies Used

- Backend: Python, Flask
- Database: SQLite (sqlite3)
- Frontend: HTML, CSS, Bootstrap
- Deployment: AWS EC2

Installation and Setup

1. Clone the repository
```bash
git clone https://github.com/marysyamelnyk/Ratings 
cd review-tracker  
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv  
source venv/bin/activate  # For Linux/Mac  
venv\Scripts\activate  # For Windows  
pip install -r requirements.txt  
```

3. Set up the database
Rename .env.example to .env and specify your database settings:
```ini

DATABASE_URL=sqlite:///review_tracker.db  
SECRET_KEY=your_secret_key
```

4. Create the database:
```bash
flask db init  
flask db migrate -m "Initial migration."  
flask db upgrade  
```

5. Run the application
```bash
flask run  
```

The application will be available at the following URL:
http://3.82.226.65/

Contact
If you have any questions or suggestions, feel free to reach out via GitHub or email: marynka555@gmail.com.