from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# Helper function to fetch the complete formatted user list
def get_all_users_list(cursor):
    cursor.execute("SELECT user_id, user_name, user_email FROM tbl_user")
    rows = cursor.fetchall()
    
    user_list = []
    for row in rows:
        user_list.append({
            "user_id": row[0],
            "user_name": row[1],
            "user_email": row[2]
        })
    return user_list

# 1. LIST ALL USERS FROM DATABASE
@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        cur = mysql.connection.cursor()
        user_list = get_all_users_list(cur)
        cur.close()
        
        # Append target operational instruction line to the end of the JSON array
        user_list.append({
            "instruction": "To add a user, go to /userc?name=abc&email=abc.com. To delete a user, go to /userd?name=abc"
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. ADD USER VIA URL QUERY PARAMETERS
@app.route('/userc', methods=['GET'])
def add_user_via_url():
    name = request.args.get('name')
    email = request.args.get('email')

    if not name or not email:
        return jsonify({
            "error": "Missing query parameters.",
            "instruction": "Please build your URL target exactly like this: /userc?name=abc&email=abc.com"
        }), 400

    try:
        cur = mysql.connection.cursor()
        # Insert target data records
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        
        # Grab updated user records array listing
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": "User added successfully! Modify your parameters to add more users: /userc?name=abc&email=abc.com"
        })
        return jsonify(user_list), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. DELETE USER BY URL QUERY PARAMETER (BY NAME)
@app.route('/userd', methods=['GET'])
def delete_user_via_url():
    name = request.args.get('name')

    if not name:
        return jsonify({
            "error": "Missing target query parameter.",
            "instruction": "Please pass the user name to remove like this: /userd?name=abc"
        }), 400

    try:
        cur = mysql.connection.cursor()
        
        # Check if the user profile exists before attempting drop
        cur.execute("SELECT user_id FROM tbl_user WHERE user_name = %s", (name,))
        if not cur.fetchone():
            user_list = get_all_users_list(cur)
            cur.close()
            user_list.append({
                "error": f"User '{name}' not found.",
                "instruction": "Verify spelling or review active profiles at /users"
            })
            return jsonify(user_list), 404
            
        # Execute query statement removal operation mapping
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        # Pull fresh repository layout records state mapping
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return jsonify({
        "message": "Welcome to Flask CRUD Engine!",
        "endpoints": {
            "list": "/users",
            "create": "/userc?name=abc&email=abc.com",
            "delete": "/userd?name=abc"
        }
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
