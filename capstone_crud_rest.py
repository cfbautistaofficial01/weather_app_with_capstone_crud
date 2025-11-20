from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

 
API_TOKEN = os.getenv('API_SECRET_TOKEN')

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),  
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'company_db')
}

# helpers for DB connection
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def check_auth():
    """Checks if the correct token is provided in headers or query params."""
    # Check query param ?token=... OR Header 'Authorization: Bearer ...'
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    # Security check: Ensure token exists and matches
    if not API_TOKEN or token != API_TOKEN:
        return False
    return True

def execute_read_query(query, params=None):
    """Executes a SELECT query and returns a list of dictionaries."""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def execute_write_query(query, params):
    """Executes INSERT, UPDATE, DELETE queries."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Database Error: {e}")
        conn.close()
        return False

# endpoint handlers

def handle_employees(action):
    # Get parameters from either Query String (GET) or JSON Body (POST/PUT)
    # request.values combines args and form data
    data = request.values 
    json_data = request.get_json(silent=True) or {} # Handle raw JSON body too
    
    if action == 'read':
        Filter by ID if provided
        emp_id = data.get('id')
        if emp_id:
            result = execute_read_query("SELECT * FROM tbemployees WHERE employee_id = %s", (emp_id,))
        else:
            result = execute_read_query("SELECT * FROM tbemployees")
        return jsonify(result), 200

    elif action == 'create':
        # Expecting: id, name, email, dept_id, salary
        sql = "INSERT INTO tbemployees (employee_id, name, email, department_id, salary) VALUES (%s, %s, %s, %s, %s)"
        params = (data.get('id') or json_data.get('id'), 
                  data.get('name') or json_data.get('name'), 
                  data.get('email') or json_data.get('email'), 
                  data.get('department_id') or json_data.get('department_id'), 
                  data.get('salary') or json_data.get('salary'))
        if execute_write_query(sql, params):
            return jsonify({"message": "Employee created successfully"}), 201
        return jsonify({"error": "Failed to create employee"}), 500

    elif action == 'delete':
        emp_id = data.get('id')
        if execute_write_query("DELETE FROM tbemployees WHERE employee_id = %s", (emp_id,)):
            return jsonify({"message": "Employee deleted"}), 200
        return jsonify({"error": "Failed to delete employee"}), 500
    
    
    return jsonify({"error": "Invalid action for employees"}), 400

def handle_departments(action):
    data = request.values
    json_data = request.get_json(silent=True) or {}

    if action == 'read':
        result = execute_read_query("SELECT * FROM tbdepartments")
        return jsonify(result), 200
    
    elif action == 'create':
        sql = "INSERT INTO tbdepartments (department_id, name, location) VALUES (%s, %s, %s)"
        params = (data.get('id') or json_data.get('id'), 
                  data.get('name') or json_data.get('name'), 
                  data.get('location') or json_data.get('location'))
        if execute_write_query(sql, params):
            return jsonify({"message": "Department created"}), 201
        return jsonify({"error": "Failed to create department"}), 500

    return jsonify({"error": "Invalid action for departments"}), 400

def handle_projects(action):
    data = request.values
    
    if action == 'read':
        result = execute_read_query("SELECT * FROM tbprojects")
        return jsonify(result), 200
  
    elif action == 'update':
        proj_id = data.get('id')
        new_name = data.get('name')  
        
        if not proj_id or not new_name:
             return jsonify({"error": "Missing ID or Name for update"}), 400

        sql = "UPDATE tbprojects SET project_name = %s WHERE project_id = %s"
        if execute_write_query(sql, (new_name, proj_id)):
            return jsonify({"message": "Project updated"}), 200
        return jsonify({"error": "Update failed"}), 500

    return jsonify({"error": "Invalid action for projects"}), 400

# --- MAIN ROUTER ---

@app.route('/api', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_router():
    # 1. Security Check
    if not check_auth():
        return jsonify({"error": "Unauthorized. Invalid or missing token."}), 401

    # 2. Retrieve Router Parameters
    endpoint = request.args.get('endpoint')
    action = request.args.get('action')

    # function parameters in url param
    if not action:
        if request.method == 'GET': action = 'read'
        elif request.method == 'POST': action = 'create'
        elif request.method == 'PUT': action = 'update'
        elif request.method == 'DELETE': action = 'delete'

    # 3. Validation
    if not endpoint or not action:
        return jsonify({"error": "Missing 'endpoint' or 'action' parameter"}), 400

    # 4. route handler
    endpoint = endpoint.lower()
    action = action.lower()

    if endpoint in ['employees', 'employess']: # accept variable single/plural
        return handle_employees(action)
    elif endpoint == 'departments':
        return handle_departments(action)
    elif endpoint in ['projects', 'project']: # accept variable single/plural
        return handle_projects(action)
    else:
        return jsonify({"error": f"Endpoint '{endpoint}' not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)