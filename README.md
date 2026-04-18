

## 📌 Overview
This project is a Python-based console application developed for the **Applied Databases module**.  
It integrates both **MySQL (relational database)** and **Neo4j (graph database)** to manage a conference system.

The application allows users to:
- View speakers and sessions
- View attendees by company
- Add new attendees
- View and manage attendee connections (Neo4j)
- View rooms

---

## 🧱 Technologies Used
- Python 3
- MySQL
- Neo4j
- mysql-connector-python
- neo4j Python driver

---

## 📁 Project Structure

applied-databases-project/
│
├── main.py            # Main application (menu + features)
├── db_mysql.py        # MySQL connection
├── db_neo4j.py        # Neo4j connection
├── config.py          # Database credentials
├── GitLink.txt        # GitHub repository link
├── innovation.pdf     # Description of additional features
└── README.md          # Project documentation

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

pip install mysql-connector-python neo4j

---

### 2. MySQL Setup

1. Open MySQL Workbench or CLI  
2. Run the provided SQL file:

SOURCE appdbproj.sql;

3. Confirm database exists:

USE appdbproj;
SHOW TABLES;

---

### 3. Neo4j Setup

1. Open Neo4j Desktop  
2. Create a new database (e.g. appdbprojNeo4j)  
3. Start the database  
4. Open Neo4j Browser  
5. Copy and paste the contents of the Neo4j script file and run it  

---

### 4. Configure Credentials

Edit config.py:

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DB = "appdbproj"

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "yourpassword"

---

## ▶️ Running the Application

python main.py

---

## 📋 Features

### 1. View Speakers & Sessions
- Search by speaker name (partial match supported)
- Displays:
  - Speaker name
  - Session title
  - Room name

### 2. View Attendees by Company
- Input a company ID
- Displays:
  - Attendee name
  - Date of birth
  - Session attended
  - Speaker name
  - Room name

### 3. Add New Attendee
- Input:
  - ID
  - Name
  - DOB
  - Gender
  - Company ID

### 4. View Connected Attendees (Neo4j)
- Shows all attendees connected via CONNECTED_TO

### 5. Add Attendee Connection (Neo4j)
- Connect two attendees

### 6. View Rooms
- Displays room ID, name, and capacity

---

## 💡 Innovation

See innovation.pdf for additional features.

---

## 🧪 Testing

Includes validation of inputs and database error handling.

---

## 🔗 GitHub Repository

See GitLink.txt for the repository link.
"""

