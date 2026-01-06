
# IRCTC Mini Backend System

A simplified IRCTC-style backend system developed as part of a Backend Intern assignment.  
The project demonstrates clean API design, proper database modeling, JWT-based authentication, transactional booking logic, and analytics using MongoDB.



## 📌 Objective

To build a backend system that supports:
- User registration and authentication
- Train search
- Date-based seat availability
- Booking with seat validation
- Analytics logging using MongoDB


## 🛠 Tech Stack

### Backend
- Django
- Django REST Framework (DRF)

### Authentication
- JWT (SimpleJWT)

### Databases
- **MySQL** – transactional data (users, trains, bookings)
- **MongoDB** – API logs and analytics

### Frontend (for demonstration)
- HTML
- Bootstrap
- JavaScript



## 📂 Project Structure

```

IRCTC/
├── frontend/
│   ├── login.html              
│   ├── register.html          
│   ├── index.html            
│   └── booking.html           
│
├── IRCTC/                      
│   ├── __init__.py
│   ├── asgi.py                 
│   ├── settings.py             
│   ├── urls.py                
│   └── wsgi.py                 
│
├── miniSystem/                 
│   ├── __init__.py
│   ├── admin.py                
│   ├── apps.py                 
│   ├── models.py               
│   ├── serializers.py          
│   ├── views.py                
│   ├── urls.py                
│   ├── mongo.py               
│   ├── tests.py                
│   └── migrations/             
│
├── .env                       
├── .env.example                
├── .gitignore                  
├── db.sqlite3                  
├── manage.py                  
├── requirements.txt            
└── README.md                  

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository / Extract ZIP

```bash
git clone <repository-url>
cd IRCTC
````

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv env
```

Activate:

```bash
# Windows
env\Scripts\activate

# Linux / macOS
source env/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Environment Configuration

Create a `.env` file using `.env.example` as reference.

Example `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=irctc_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306

MONGO_URI=mongodb://localhost:27017/
```

---

### 5️⃣ Database Setup

#### MySQL

Create database:

```sql
CREATE DATABASE irctc_db;
```

Run migrations:

```bash
python manage.py migrate
```

---

#### MongoDB

Ensure MongoDB is running at:

```
mongodb://localhost:27017/
```

Logs are stored in:

```
Database: irctc_logs
Collection: search_logs
```

---

### 6️⃣ Create Admin User

```bash
python manage.py createsuperuser
```

(Admin access is required for analytics API)

---

### 7️⃣ Run Server

```bash
python manage.py runserver
```

---

## 🔐 Authentication APIs

### Register User

```
POST /api/register/
```

---

### Login (JWT)

```
POST /api/login/
```

Response:

```json
{
  "refresh": "xxxxx",
  "access": "xxxxx"
}
```

Use access token in headers:

```
Authorization: Bearer <access_token>
```

---

## 🚆 Train APIs

### Search Trains (By Route)

```
GET /api/trains/search/?source=Patna&destination=Delhi&date=2026-01-10
```

### Search Trains (By Train Number)

```
GET /api/trains/search/?train_number=12577&date=2026-01-10
```

* Case-insensitive
* Partial matching supported
* Date-based availability

---

## 🎟 Booking APIs

### Book Seats

```
POST /api/bookings/
```

Request Body:

```json
{
  "train": 1,
  "journey_date": "2026-01-10",
  "seat_type": "SL",
  "seats_booked": 2
}
```

* Seat validation performed
* Transaction-safe (prevents overbooking)
* Seat classes supported: SL, 3A, 2A, 1A

---

### My Bookings

```
GET /api/bookings/my/
```

Returns bookings of the logged-in user with train details.

---

## 📊 Analytics API (MongoDB)

### Top Searched Routes (Admin Only)

```
GET /api/analytics/top-routes/
```

Headers:

```
Authorization: Bearer <admin_access_token>
```

Sample Response:

```json
[
    {
        "source": "Del",
        "destination": "Bpl",
        "search_count": 5
    },
    {
        "source": "Patna",
        "destination": "Bengaluru",
        "search_count": 3
    },
    {
        "source": "Patna",
        "destination": "Bengalur",
        "search_count": 3
    },
    {
        "source": "Patna Junction ",
        "destination": "Bengaluru Cantt",
        "search_count": 2
    },
    {
        "source": "Patna ",
        "destination": "Bengaluru",
        "search_count": 2
    }
```

---

## 🧠 Design Decisions

* MySQL is used for transactional consistency.
* MongoDB is used for analytics to avoid impacting booking performance.
* Seat availability is tracked per train per date.
* Booking operations use database transactions and row locking.
* Analytics APIs are restricted to admin users.

---

## 📌 MongoDB Log Sample (Optional)

Example document in `search_logs`:

```json
{
  "endpoint": "/api/trains/search/",
  "params": {
    "source": "Patna",
    "destination": "Delhi"
  },
  "execution_time": 0.0123
}
```





