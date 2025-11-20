
### Running the weather and crud restful api`

Overwrite your current file with this content:

````markdown
# Weather App & Capstone CRUD API

This repository contains two distinct applications built with Flask:
1.  **Weather App (`app_weather_v2.py`):** A user-friendly web interface that displays real-time weather, air quality, and AI-generated summaries.
2.  **Company API (`capstone_crud_rest.py`):** A RESTful API for managing Employees, Departments, and Projects in a MySQL database.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.x**
* **MySQL Server** (Running locally)
* **Git**

---

## 🚀 Installation & Setup

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone [https://github.com/cfbautistaofficial01/weather_app_with_capstone_crud.git](https://github.com/cfbautistaofficial01/weather_app_with_capstone_crud.git)
cd weather_app_with_capstone_crud
````

### 2\. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

  * **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
  * **Mac/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Configuration (.env)

Create a file named `.env` in the root directory. This file is **ignored by Git** for security. Paste the following configuration into it and fill in your details:

```ini
# --- SECURITY TOKENS ---
API_SECRET_TOKEN=secret-token-123
GROQ_API_KEY=your_actual_groq_api_key_here

# --- DATABASE CONFIGURATION ---
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=company_db

# --- EXTERNAL API URLS ---
GEOCODING_API_URL=[https://geocoding-api.open-meteo.com/v1/search](https://geocoding-api.open-meteo.com/v1/search)
WEATHER_API_URL=[https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast)
AIR_QUALITY_API_URL=[https://air-quality-api.open-meteo.com/v1/air-quality](https://air-quality-api.open-meteo.com/v1/air-quality)
GROQ_PROXY_URL=[https://eacomm.com/support/groq.php](https://eacomm.com/support/groq.php)
```

-----

## 🖥️ Application 1: The Weather App

This is the visual front-end application.

**To Run:**

```bash
python app_weather_v2.py
```

  * **Access in Browser:** Open `http://127.0.0.1:5001`
  * **Features:**
      * Real-time temperature and weather description.
      * Air Quality Index (AQI) monitoring.
      * AI-generated witty weather summaries (powered by Groq).

-----

## ⚙️ Application 2: Company CRUD API

This is the backend REST API for database management.

**To Run:**

```bash
python capstone_crud_rest.py
```

  * **Server Address:** `http://127.0.0.1:5000`
  * **Authentication:** All requests must include the token defined in your `.env`.
      * **Header:** `Authorization: Bearer secret-token-123`
      * **OR Query Param:** `?token=secret-token-123`

### 📖 API Documentation

#### **1. Employees**

| Method | Endpoint | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api?endpoint=employees` | Get all employees | `id` (optional) |
| `POST` | `/api?endpoint=employees` | Create new employee | `id`, `name`, `email`, `department_id`, `salary` |
| `DELETE` | `/api?endpoint=employees` | Delete an employee | `id` |

#### **2. Departments**

| Method | Endpoint | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api?endpoint=departments` | Get all departments | - |
| `POST` | `/api?endpoint=departments` | Create new department | `id`, `name`, `location` |

#### **3. Projects**

| Method | Endpoint | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api?endpoint=projects` | Get all projects | - |
| `PUT` | `/api?endpoint=projects` | Update project name | `id`, `name` |

-----

## 📂 Project Structure

```text
weather_app_with_capstone_crud/
│
├── app_weather_v2.py                  # Weather App Entry Point (Port 5001)
├── capstone_crud_rest.py   # API Entry Point (Port 5000)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (Not uploaded to Git)
├── .gitignore              # Specifies files to ignore
└── README.md               # Project Documentation
```
 
