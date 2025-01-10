# Railway Ticket Booking System API 🚆
This project provides a RESTful API for managing railway ticket booking operations, including passengers, trains, schedules, bookings, and payments. Built using Python and MySQL, the API supports CRUD operations and ensures secure and efficient data handling.

# 📋 Features
CRUD Operations: Manage entities like passengers, trains, schedules, bookings, and payments.
Dynamic Endpoints: Fetch specific records or entire tables.
Database Integration: MySQL-backed data storage with seamless connection handling.
Error Handling: Robust logging and error messages for debugging and reliability.
Scalable Design: Easily extendable to add new features or tables.
# 🛠️ Technologies Used
Python: Backend server logic.
MySQL: Database storage.
HTTPServer: For handling API requests.
JSON: Data exchange format.
Postman: For testing the API.

# 🚀 Getting Started
#1️⃣ Prerequisites
Python 3.x
MySQL Server
Postman or similar API testing tool
#2️⃣ Installation Steps
Clone the repository


Copy code
git clone https://github.com/yourusername/railway-ticket-booking-system.git
cd railway-ticket-booking-system


#Install dependencies

    Copy code
    pip install mysql-connector-python
    Set up the database

    
  Create a MySQL database named train_system :


    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=yourpassword
    DB_NAME=train_system
    
#3️⃣ Running the API Server
  Start the server:
python server.py
Open Postman and test the API endpoints.

#📖 API Endpoints
📌 Passengers
GET /passengers/ - Retrieve all passengers.
GET /passengers/{id} - Retrieve a passenger by ID.
POST /passengers/ - Create a new passenger.
PUT /passengers/{id} - Update a passenger's details.
DELETE /passengers/{id} - Delete a passenger.

📌 Trains
GET /trains/ - Retrieve all trains.
GET /trains/{id} - Retrieve a train by ID.
POST /trains/ - Add a new train.
PUT /trains/{id} - Update train details.
DELETE /trains/{id} - Delete a train.
(Continue this for bookings, schedules, and payments.)

#🧪 Testing with Postman
Open Postman and set the base URL to http://localhost:8000/.
Use the following HTTP methods for testing:
GET: To fetch data.
POST: To create a new record (include JSON in the body).
PUT: To update an existing record.
DELETE: To delete a record.

#🐛 Troubleshooting
Database errors?
Ensure MySQL is running and .env credentials are correct.
Port already in use?
Change the port in the run() function to an available one.
