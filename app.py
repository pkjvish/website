from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL Connection Map
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# Helper function to fetch the complete formatted user list
def get_all_users_list(cursor):
    cursor.execute("SELECT user_id, user_name, user_age, user_email FROM tbl_user")
    rows = cursor.fetchall()
    
    user_list = []
    for row in rows:
        user_list.append({
            "user_id": row[0],
            "user_name": row[1],
            "user_age": row[2],
            "user_email": row[3]
        })
    return user_list

# Multi-Column Inverted Card-Based SPA Layout via Cloudflare cdnjs
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Floating Mini Card Dashboard</title>
    
    <!-- Stable Cloudflare cdnjs replacements for Bootstrap 5 and Icons Framework -->
    <link href="cloudflare.com" rel="stylesheet">
    <link href="cloudflare.com" rel="stylesheet">
    
    <style>
        body { 
            background-color: #f1f5f9;
            background-image: radial-gradient(#cbd5e1 1.5px, transparent 1.5px);
            background-size: 24px 24px;
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            padding-bottom: 180px;
        }
        .mini-card {
            border: none;
            border-radius: 12px;
            padding: 16px;
            width: 240px;
            min-height: 125px;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .mini-card:nth-child(even) { transform: rotate(1deg); }
        .mini-card:nth-child(odd) { transform: rotate(-1deg); }
        .mini-card:hover {
            transform: scale(1.06) rotate(0deg) translateY(-4px) !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            z-index: 50;
        }
        .cross-delete-btn {
            position: absolute;
            top: 8px;
            right: 8px;
            border: none;
            background: rgba(0, 0, 0, 0.05);
            color: rgba(0, 0, 0, 0.4);
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            cursor: pointer;
            padding: 0;
        }
        .cross-delete-btn:hover {
            background: #ef4444;
            color: #ffffff;
            transform: scale(1.1);
        }
        .user-title {
            font-size: 1rem;
            font-weight: 700;
            color: #1e293b;
            padding-right: 18px;
            word-break: break-word;
        }
        .user-detail {
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(30, 41, 59, 0.7);
            word-break: break-word;
        }
        .bottom-dock {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-top: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.06);
            z-index: 1000;
        }
        .form-control-custom {
            border-radius: 10px;
            border: 1.5px solid #cbd5e1;
            padding: 10px 14px;
            font-size: 0.9rem;
            transition: all 0.2s;
            width: 100%;
        }
        .form-control-custom:focus {
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
            border-color: #4f46e5;
            outline: none;
        }
        .btn-dock-submit {
            border-radius: 10px;
            padding: 11px 20px;
            font-weight: 600;
            background: #4f46e5;
            border: none;
            width: 100%;
            transition: all 0.2s;
            color: #ffffff;
        }
        .btn-dock-submit:hover { background: #4338ca; }
        .btn-dock-cancel {
            border-radius: 10px;
            padding: 11px 20px;
            font-weight: 600;
            background: #64748b;
            border: none;
            width: 100%;
            transition: all 0.2s;
            color: #ffffff;
        }
        .btn-dock-cancel:hover { background: #475569; }
        .btn-toggle-main {
            border-radius: 50px;
            font-weight: 600;
            padding: 12px 32px;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
            transition: all 0.2s;
        }
        .btn-toggle-main:hover { transform: translateY(-1px); }
        #toastContainer {
            position: fixed;
            bottom: 130px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1060;
            width: auto;
            min-width: 320px;
            max-width: 90%;
        }
        .hidden-fields-tray {
            max-height: 0;
            opacity: 0;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .hidden-fields-tray.show {
            max-height: 250px;
            opacity: 1;
            padding: 10px 0;
        }
    </style>
</head>
<body>

    <div class="container-fluid px-4 pt-4">
        <header class="mb-4 pb-2">
            <h3 class="fw-bold text-slate-800 m-0"><i class="bi bi-pin-angle-fill text-danger me-2"></i>Pinboard Board</h3>
        </header>
        <div id="cardsBoard" class="d-flex flex-wrap gap-3 align-items-start justify-content-start"></div>
    </div>

    <div id="toastContainer">
        <div id="statusAlert" class="alert d-none shadow-lg border p-3 rounded-3 text-sm font-medium transition text-center" role="alert"></div>
    </div>

    <div class="bottom-dock py-3">
        <div class="container-fluid px-4 px-md-5">
            <!-- Renamed button target to "Create User" -->
            <div id="triggerButtonContainer" class="text-center">
                <button onclick="toggleFormTray(true)" id="mainToggleBtn" class="btn btn-primary btn-toggle-main">
                    <i class="bi bi-person-plus-fill me-1"></i> Create User
                </button>
            </div>
            <div id="formFieldsTray" class="hidden-fields-tray">
                <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
                    <h6 class="fw-bold text-slate-700 m-0"><i class="bi bi-file-earmark-person text-success me-1"></i> Input Profile Parameters</h6>
                </div>
                <form id="customerForm" class="row gx-3 gy-2 align-items-center">
                    <div class="col-12 col-md-3">
                        <input type="text" id="custName" required placeholder="Customer Full Name" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-12 col-md-2">
                        <input type="number" id="custAge" required min="1" max="120" placeholder="Age" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-12 col-md-3">
                        <input type="email" id="custEmail" required placeholder="Email Address" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-6 col-md-2">
                        <button type="submit" class="btn btn-primary btn-dock-submit shadow-sm">
                            <i class="bi bi-check-circle-fill me-1"></i> Submit
                        </button>
                    </div>
                    <div class="col-6 col-md-2">
                        <button type="button" onclick="toggleFormTray(false)" class="btn btn-secondary btn-dock-cancel shadow-sm">
                            <i class="bi bi-x-circle-fill me-1"></i> Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        const API_BASE_URL = window.location.origin;
        const dashboardHeaders = { 
            'X-Requested-From': 'Dashboard',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Bypass-Tunnel-Reminder': 'true'
        };
        const pastelColors = ['#fef08a', '#fbcfe8', '#bbf7d0', '#bfdbfe', '#e9d5ff', '#fed7aa', '#ccfbf1'];

        // Updated visibility layout engine logic to correctly show/hide action structures
        function toggleFormTray(shouldOpen) {
            const tray = document.getElementById('formFieldsTray');
            const btnContainer = document.getElementById('triggerButtonContainer');
            if (shouldOpen) {
                tray.classList.add('show');
                btnContainer.classList.add('d-none'); // Completely hides Create User Button
            } else {
                tray.classList.remove('show');
                btnContainer.classList.remove('d-none'); // Restores Create User Button
                document.getElementById('customerForm').reset();
            }
        }

        function showNotification(message, isSuccess = true) {
            const el = document.getElementById('statusAlert');
            el.className = `alert shadow-lg border p-3 rounded-3 text-center ${isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle'}`;
            el.textContent = message;
            el.classList.remove('d-none');
            setTimeout(() => el.classList.add('d-none'), 4000);
        }

        async function fetchAndRenderUsers() {
            try {
                const res = await fetch(`${API_BASE_URL}/users`, { headers: dashboardHeaders });
                const users = await res.json();
                const board = document.getElementById('cardsBoard');
                board.innerHTML = '';
                
                if(!users || users.length === 0) {
                    board.innerHTML = '<div class="text-secondary fs-6 py-4 mx-auto"><i class="bi bi-inbox me-2"></i>No profiles pinned yet.</div>';
                    return;
                }

                users.forEach((user, index) => {
                    const randomColor = pastelColors[index % pastelColors.length];
                    const card = document.createElement('div');
                    card.className = 'mini-card';
                    card.style.backgroundColor = randomColor;
                    card.innerHTML = `
                        <button class="cross-delete-btn" onclick="deleteUser(${user.user_id})" title="Remove Pin">
                            <i class="bi bi-x-lg" style="font-size: 0.7rem; -webkit-text-stroke: 0.5px;"></i>
                        </button>
                        <div class="user-title">${user.user_name}</div>
                        <div class="mt-2">
                            <div class="user-detail mb-1"><i class="bi bi-calendar3 me-1"></i>${user.user_age} Years Old</div>
                            <div class="user-detail text-truncate" title="${user.user_email}"><i class="bi bi-envelope me-1"></i>${user.user_email}</div>
                        </div>
                    `;
                    board.appendChild(card);
                });
            } catch (err) {
                showNotification('Could not update user board display.', false);
            }
        }

        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('custName').value.trim(),
                age: parseInt(document.getElementById('custAge').value),
                email: document.getElementById('custEmail').value.trim()
            };

            try {
                const res = await fetch(`${API_BASE_URL}/users`, {
                    method: 'POST',
                    headers: dashboardHeaders,
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                
                if (res.ok) {
                    showNotification(result.message || 'User profile updated successfully!');
                    toggleFormTray(false); // Closes form layout inputs and completely shows Create User button again
                    fetchAndRenderUsers(); // Triggers automated dashboard asynchronous refresh
                } else {
                    showNotification(result.error || 'Failed to submit profile metrics.', false);
                }
            } catch (err) {
                showNotification('Network connection profile synchronization failed.', false);
            }
        });

        async function deleteUser(userId) {
            if (!confirm('Permanently purge this pinned registration?')) return;
            try {
                const res = await fetch(`${API_BASE_URL}/users/${userId}`, {
                    method: 'DELETE',
                    headers: dashboardHeaders
                });
                const result = await res.json();
                
                if (res.ok) {
                    showNotification(result.message || 'User successfully dropped.');
                    fetchAndRenderUsers();
                } else {
                    showNotification(result.error || 'Failed to remove requested card.', false);
                }
            } catch (err) {
                showNotification('Execution drop process failed.', false);
            }
        }

        document.addEventListener('DOMContentLoaded', fetchAndRenderUsers);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

# 1) List all users GET /users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        cursor = mysql.connection.cursor()
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2) Create user POST /users
@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        email = data.get('email')

        if not name or not age or not email:
            return jsonify({"error": "Missing parameters name, age, or email"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO tbl_user (user_name, user_age, user_email) VALUES (%s, %s, %s)",
            (name, age, email)
        )
        mysql.connection.commit()
        
        # Fetch and return updated user list
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify({"message": "User card initialized successfully", "users": users}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2b) Create user via GET /userc?name=mani&age=56&email=mani@gmail.com (legacy)
@app.route('/userc', methods=['GET'])
def add_user_legacy():
    try:
        name = request.args.get('name')
        age = request.args.get('age')
        email = request.args.get('email')

        if not name or not age or not email:
            return jsonify({"error": "Missing parameters. Use /userc?name=mani&age=56&email=mani@gmail.com"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO tbl_user (user_name, user_age, user_email) VALUES (%s, %s, %s)",
            (name, age, email)
        )
        mysql.connection.commit()
        
        # Fetch and return updated user list
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify({"message": "User card initialized successfully", "users": users}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3) Delete user DELETE /users/<user_id>
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        
        # Fetch and return updated user list
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify({"message": "User profile successfully removed", "users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4) Delete user via api /userd?name=pkj (legacy)
@app.route('/userd', methods=['GET'])
def delete_user():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Missing parameter name"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        # Fetch and return updated user list
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify({"message": f"User '{name}' safely scrubbed from database", "users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5) Update user via api /useru?name=pkj
@app.route('/useru', methods=['GET'])
def update_user():
    try:
        name = request.args.get('name')
        age = request.args.get('age')
        email = request.args.get('email')

        if not name:
            return jsonify({"error": "Missing target matching identifier parameter: name"}), 400

        cursor = mysql.connection.cursor()
        
        # Pull parameters dynamically depending on what details were provided in string
        if age and email:
            cursor.execute("UPDATE tbl_user SET user_age = %s, user_email = %s WHERE user_name = %s", (age, email, name))
        elif age:
            cursor.execute("UPDATE tbl_user SET user_age = %s WHERE user_name = %s", (age, name))
        elif email:
            cursor.execute("UPDATE tbl_user SET user_email = %s WHERE user_name = %s", (email, name))
        else:
            cursor.close()
            return jsonify({"error": "No update metrics (age/email) were supplied"}), 400

        mysql.connection.commit()
        
        # Fetch and return updated user list
        users = get_all_users_list(cursor)
        cursor.close()
        return jsonify({"message": f"User targets for '{name}' synchronized", "users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
