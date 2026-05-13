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

# Enhanced Layout Template with clean string concatenation for JavaScript stability
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Floating Mini Card Dashboard</title>
    <link href="jsdelivr.net" rel="stylesheet">
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { 
            background-color: #f1f5f9;
            background-image: radial-gradient(#cbd5e1 1.5px, transparent 1.5px);
            background-size: 24px 24px;
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            padding-bottom: 140px;
        }
        .mini-card {
            border: none;
            border-radius: 12px;
            padding: 16px;
            width: 250px;
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
            font-size: 1.05rem;
            font-weight: 700;
            color: #1e293b;
            padding-right: 18px;
            line-height: 1.3;
        }
        .user-detail {
            font-size: 0.85rem;
            font-weight: 600;
            color: rgba(30, 41, 59, 0.7);
        }
        .bottom-dock {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.96);
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
        }
        .form-control-custom:focus {
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
            border-color: #4f46e5;
            outline: none;
        }
        .btn-dock-submit {
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 600;
            background: #4f46e5;
            border: none;
            transition: all 0.2s;
            color: #ffffff;
            white-space: nowrap;
        }
        .btn-dock-submit:hover { background: #4338ca; }
        .btn-toggle-main {
            border-radius: 50px;
            font-weight: 600;
            padding: 12px 32px;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
            transition: all 0.2s;
        }
        #toastContainer {
            position: fixed;
            bottom: 110px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1060;
            width: auto;
            min-width: 320px;
            max-width: 90%;
        }
        .hidden-fields-tray {
            display: none;
            width: 100%;
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
        <div id="statusAlert" class="alert d-none shadow-lg border p-3 rounded-3 text-sm font-medium text-center" role="alert"></div>
    </div>

    <div class="bottom-dock py-3">
        <div class="container-fluid px-4 px-md-5">
            <div id="triggerButtonContainer" class="text-center">
                <button onclick="toggleFormTray(true)" id="mainToggleBtn" class="btn btn-primary btn-toggle-main">
                    <i class="bi bi-person-plus-fill me-1"></i> Create User
                </button>
            </div>
            
            <div id="formFieldsTray" class="hidden-fields-tray">
                <form id="customerForm" class="d-md-flex align-items-center justify-content-between gap-3 w-100">
                    <div class="flex-grow-1">
                        <input type="text" id="custName" required placeholder="Customer Full Name" class="form-control form-control-custom w-100 shadow-none">
                    </div>
                    <div style="min-width: 90px; max-width: 120px;">
                        <input type="number" id="custAge" required min="1" max="120" placeholder="Age" class="form-control form-control-custom w-100 shadow-none">
                    </div>
                    <div class="flex-grow-1">
                        <input type="email" id="custEmail" required placeholder="Email Address" class="form-control form-control-custom w-100 shadow-none">
                    </div>
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary btn-dock-submit shadow-sm">Submit User</button>
                        <button type="button" onclick="toggleFormTray(false)" class="btn btn-outline-secondary rounded-3 px-3">Cancel</button>
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
            'Bypass-Tunnel-Reminder': 'true'
        };
        const pastelColors = ['#fef08a', '#fbcfe8', '#bbf7d0', '#bfdbfe', '#e9d5ff', '#fed7aa', '#ccfbf1'];

        function toggleFormTray(shouldOpen) {
            const tray = document.getElementById('formFieldsTray');
            const mainBtn = document.getElementById('mainToggleBtn');
            if (shouldOpen) {
                tray.style.display = 'block';
                mainBtn.style.display = 'none';
            } else {
                tray.style.display = 'none';
                mainBtn.style.display = 'inline-block';
                document.getElementById('customerForm').reset();
            }
        }

        function showNotification(message, isSuccess) {
            isSuccess = (isSuccess === undefined) ? true : isSuccess;
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = 'alert shadow-lg border p-3 rounded-3 text-sm font-medium d-block ' + (isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle');
            alertBox.innerHTML = '<i class="bi ' + (isSuccess ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill') + ' me-2"></i> ' + message;
            setTimeout(function() { alertBox.className = 'alert d-none'; }, 4000);
        }

        async function fetchCustomerCards() {
            try {
                const response = await fetch(API_BASE_URL + '/users', { headers: dashboardHeaders });
                const data = await response.json();
                const board = document.getElementById('cardsBoard');
                board.innerHTML = '';
                const customers = data.filter(function(item) { return item.user_id !== undefined; });
                if (customers.length === 0) {
                    board.innerHTML = '<div class="w-100 text-center py-5 bg-white border border-secondary-subtle rounded-3 text-muted italic"><i class="bi bi-clipboard-x display-6 d-block mb-2 opacity-50"></i> Pinboard workspace is currently empty.</div>';
                    return;
                }
                customers.forEach(function(customer, idx) {
                    const assignedColor = pastelColors[idx % pastelColors.length];
                    board.innerHTML += '<div class="mini-card" style="background-color: ' + assignedColor + ';"><button onclick="dropCustomerCard(\'' + customer.user_name + '\')" class="cross-delete-btn" title="Delete Card"><i class="bi bi-x-lg" style="font-size: 0.75rem;"></i></button><div><div class="user-title text-truncate">' + customer.user_name + ' (' + customer.user_age + ' yrs)</div></div><div class="pt-2 border-top border-dark border-opacity-10 mt-2"><div class="user-detail text-truncate fw-semibold"><i class="bi bi-envelope-at-fill opacity-50 small"></i> ' + customer.user_email + '</div></div></div>';
                });
            } catch (err) {
                showNotification("Connection failure. Flask backend server unreachable.", false);
            }
        }

        document.getElementById('customerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const age = document.getElementById('custAge').value;
            const email = document.getElementById('custEmail').value.trim();
            try {
                const res = await fetch(API_BASE_URL + '/userc?name=' + encodeURIComponent(name) + '&age=' + age + '&email=' + encodeURIComponent(email), { headers: dashboardHeaders });
                if (res.ok) {
                    showNotification('Mini card for "' + name + '" instantiated on top.', true);
                    toggleFormTray(false);
                    fetchCustomerCards();
                } else {
                    const errData = await res.json();
                    showNotification(errData.error || "Failed to process parameter inputs.", false);
                }
            } catch (err) {
                showNotification("Network data runtime transmission error.", false);
            }
        });

        async function dropCustomerCard(name) {
            try {
                const res = await fetch(API_BASE_URL + '/userd?name=' + encodeURIComponent(name), { headers: dashboardHeaders });
                if (res.ok) {
                    showNotification('Mini card for "' + name + '" dropped successfully.', true);
                    fetchCustomerCards();
                } else {
                    showNotification("Could not execute card wipe operation.", false);
                }
            } catch (err) {
                showNotification("Network connection failure during deletion cycle.", false);
            }
        }
        window.onload = fetchCustomerCards;
    </script>
    <script src="jsdelivr.net"></script>
</body>
</html>"""

# 3. ROUTE: SERVES INTEGRATED DASHBOARD SPA
@app.route('/', methods=['GET'])
def home_dashboard():
    return render_template_string(DASHBOARD_HTML)

# 4. ROUTE: LIST ALL USERS FROM DATABASE
@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        cur = mysql.connection.cursor()
        user_list = get_all_users_list(cur)
        cur.close()
        user_list.append({"instruction": "To add a user, go to /userc?name=abc&age=25&email=abc.com. To delete a user, go to /userd?name=abc"})
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. ROUTE: ADD USER VIA URL QUERY PARAMETERS
@app.route('/userc', methods=['GET'])
def add_user_via_url():
    name = request.args.get('name')
    age = request.args.get('age')
    email = request.args.get('email')

    if not name or not age or not email:
        return jsonify({"error": "Missing query parameters.", "instruction": "Please build your URL target exactly like this: /userc?name=abc&age=25&email=abc.com"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_user(user_name, user_age, user_email) VALUES (%s, %s, %s)", (name, age, email))
        mysql.connection.commit()
        user_list = get_all_users_list(cur)
        cur.close()
        user_list.append({"instruction": "User added successfully! Modify your parameters to add more users: /userc?name=abc&age=25&email=abc.com"})
        return jsonify(user_list), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 6. ROUTE: DELETE USER BY URL QUERY PARAMETER (BY NAME)
@app.route('/userd', methods=['GET'])
def delete_user_via_url():
    name = request.args.get('name')

    if not name:
        return jsonify({"error": "Missing target query parameter.", "instruction": "Please pass the user name to remove like this: /userd?name=abc"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM tbl_user WHERE user_name = %s", (name,))
        if not cur.fetchone():
            user_list = get_all_users_list(cur)
            cur.close()
            user_list.append({"error": f"User '{name}' not found.", "instruction": "Verify spelling or review active profiles at /users"})
            return jsonify(user_list), 404
            
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        user_list = get_all_users_list(cur)
        cur.close()
        user_list.append({"instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."})
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
