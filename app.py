from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL Connection Map
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# Helper function to fetch the complete formatted user list with Age tracking included
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

# Modern Bootstrap 5 Card-Based SPA Dashboard UI Layout
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Profile Matrix</title>
    <!-- Absolute paths for CSS CDNs -->
    <link href="jsdelivr.net" rel="stylesheet">
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { background-color: #f1f5f9; font-family: 'Segoe UI', system-ui, sans-serif; }
        .profile-card { border: none; border-radius: 16px; background: #ffffff; transition: all 0.25s ease; position: relative; }
        .profile-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.06)!important; }
        .delete-btn { position: absolute; top: 12px; right: 12px; border: none; background: rgba(239, 68, 68, 0.1); color: #ef4444; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; cursor: pointer; }
        .delete-btn:hover { background: #ef4444; color: #ffffff; transform: rotate(90deg); }
        .avatar-emblem { width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.25rem; }
        .form-control { border-radius: 10px; border-color: #e2e8f0; padding: 10px 14px; font-size: 0.95rem; }
        .form-control:focus { box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15); border-color: #4f46e5; }
        .btn-submit { border-radius: 10px; padding: 11px; font-weight: 600; background: #4f46e5; border: none; }
        .btn-submit:hover { background: #4338ca; }
    </style>
</head>
<body>

    <div class="container py-5">
        <!-- Header Section -->
        <header class="d-flex flex-column flex-md-row justify-content-between align-items-md-center pb-3 mb-5 border-bottom">
            <div>
                <h1 class="fw-black text-dark mb-1"><i class="bi bi-person-vcard text-primary me-2"></i>Customer Matrix</h1>
                <p class="text-muted mb-0">Single Page Profile Engine with dynamic card instantiation.</p>
            </div>
            <div class="mt-3 mt-md-0">
                <button onclick="fetchCustomerCards()" class="btn btn-white border shadow-sm btn-sm px-3 py-2 fw-semibold text-secondary">
                    <i class="bi bi-arrow-clockwise me-1 text-primary"></i> Sync Directory
                </button>
            </div>
        </header>

        <!-- Status Notification Ribbon -->
        <div id="statusAlert" class="alert d-none shadow-sm mb-4" role="alert"></div>

        <div class="row g-4">
            <!-- Left Side Input Interface Card -->
            <div class="col-12 col-xl-4">
                <div class="card shadow-sm border p-4 bg-white sticky-top" style="top: 24px; z-index: 100;">
                    <h5 class="fw-bold text-dark mb-4"><i class="bi bi-plus-circle-fill text-success me-2"></i>Register Profile</h5>
                    
                    <form id="customerForm">
                        <div class="mb-3">
                            <label class="form-label text-muted fw-bold small text-uppercase">Full Name</label>
                            <input type="text" id="custName" required placeholder="e.g. Pankaj Kumar" class="form-control shadow-none">
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-muted fw-bold small text-uppercase">Age Parameter</label>
                            <input type="number" id="custAge" required min="1" max="120" placeholder="e.g. 28" class="form-control shadow-none">
                        </div>
                        <div class="mb-4">
                            <label class="form-label text-muted fw-bold small text-uppercase">Email Address</label>
                            <input type="email" id="custEmail" required placeholder="e.g. pankaj@example.com" class="form-control shadow-none">
                        </div>
                        <button type="submit" class="btn btn-primary btn-submit w-100 shadow-sm">
                            <i class="bi bi-person-plus-fill me-1"></i> Instantiation Card
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Side Customer Cards Deck display area -->
            <div class="col-12 col-xl-8">
                <h5 class="fw-bold text-dark mb-4"><i class="bi bi-grid-3x3-gap-fill text-primary me-2"></i>Active Card Deck</h5>
                
                <!-- Explicitly Card Grid Format (No tables) -->
                <div id="cardsGrid" class="row row-cols-1 row-cols-md-2 g-3">
                    <!-- Dynamic asynchronous DOM mounting handles cards injection here -->
                </div>
            </div>
        </div>
    </div>

    <!-- Asynchronous Runtime Engine Script -->
    <script>
        const API_BASE_URL = window.location.origin;

        const dashboardHeaders = { 
            'X-Requested-From': 'Dashboard',
            'Accept': 'application/json',
            'Bypass-Tunnel-Reminder': 'true'
        };

        function pushNotification(message, isSuccess = true) {
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = `alert shadow-sm border mb-4 d-block ${isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle'}`;
            alertBox.innerHTML = `<i class="bi ${isSuccess ? 'bi-check-circle' : 'bi-exclamation-triangle'}-fill me-2"></i> ${message}`;
            setTimeout(() => { alertBox.className = 'alert d-none'; }, 4000);
        }

        // 1. FETCH ASYNC: Read database array and render pure cards format
        async function fetchCustomerCards() {
            try {
                const response = await fetch(`${API_BASE_URL}/users`, { headers: dashboardHeaders });
                const data = await response.json();
                const grid = document.getElementById('cardsGrid');
                grid.innerHTML = '';

                // Strip operational metadata instruction strings from the array view map
                const customers = data.filter(item => item.user_id !== undefined);

                if (customers.length === 0) {
                    grid.innerHTML = `
                        <div class="col-12 w-100 text-center py-5 bg-white border rounded-4 text-muted italic">
                            <i class="bi bi-person-vcard display-5 d-block mb-2 text-slate-300"></i> No customer cards available in workspace database.
                        </div>`;
                    return;
                }

                customers.forEach(customer => {
                    const firstLetter = customer.user_name ? customer.user_name.charAt(0).toUpperCase() : '?';
                    
                    grid.innerHTML += `
                        <div class="col">
                            <div class="card profile-card h-100 shadow-sm border p-4">
                                <!-- Cross Delete Trigger button on each profile card layout -->
                                <button onclick="dropCustomerCard('${customer.user_name}')" class="delete-btn" title="Delete Profile">
                                    <i class="bi bi-x-lg font-bold" style="font-size: 0.85rem;"></i>
                                </button>
                                
                                <div class="d-flex align-items-center gap-3 mb-3">
                                    <div class="avatar-emblem bg-indigo-subtle text-indigo text-primary">
                                        ${firstLetter}
                                    </div>
                                    <div class="overflow-hidden">
                                        <h6 class="fw-bold text-dark mb-0 text-truncate" style="max-width: 180px;">${customer.user_name}</h6>
                                        <span class="badge bg-secondary-subtle text-secondary rounded-pill mt-1">Age: ${customer.user_age} yrs</span>
                                    </div>
                                </div>
                                
                                <div class="pt-2 border-top">
                                    <div class="text-secondary small d-flex align-items-center gap-1.5 text-truncate">
                                        <i class="bi bi-envelope-at text-muted"></i> ${customer.user_email}
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });
            } catch (err) {
                pushNotification("Connection failure. Flask engine backend unreachable.", false);
            }
        }

        // 2. POST ASYNC: Appends profile entries on same page via background thread processing
        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const age = document.getElementById('custAge').value;
            const email = document.getElementById('custEmail').value.trim();

            try {
                const res = await fetch(`${API_BASE_URL}/userc?name=${encodeURIComponent(name)}&age=${age}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    pushNotification(`Profile card for "${name}" generated safely.`);
                    document.getElementById('customerForm').reset();
                    fetchCustomerCards();
                } else {
                    const errData = await res.json();
                    pushNotification(errData.error || "Failed to map parameters entry structure.", false);
                }
            } catch (err) {
                pushNotification("Network runtime write failure.", false);
            }
        });

        // 3. DELETE ASYNC: Removes and drops structural parameters instantly from screen
        async function dropCustomerCard(name) {
            try {
                const res = await fetch(`${API_BASE_URL}/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    pushNotification(`User "${name}" has been wiped from database arrays.`);
                    fetchCustomerCards();
                } else {
                    pushNotification(`Could not execute card drop operation. Profile not located.`, false);
                }
            } catch (err) {
                pushNotification("Network connection failure during deletion cycle.", false);
            }
        }

        window.onload = fetchCustomerCards;
    </script>
    
    <!-- Absolute path for JS bundle CDN -->
    <script src="jsdelivr.net"></script>
</body>
</html>
"""

# 3. ROUTE: SERVES INTEGRATED GRAPHICAL DASHBOARD UI
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
        
        user_list.append({
            "instruction": "To add a user, go to /userc?name=abc&age=25&email=abc.com. To delete a user, go to /userd?name=abc"
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. ROUTE: ADD USER VIA URL QUERY PARAMETERS (Includes Age processing mapping)
@app.route('/userc', methods=['GET'])
def add_user_via_url():
    name = request.args.get('name')
    age = request.args.get('age')
    email = request.args.get('email')

    if not name or not age or not email:
        return jsonify({
            "error": "Missing query parameters.",
            "instruction": "Please build your URL target exactly like this: /userc?name=abc&age=25&email=abc.com"
        }), 400

    try:
        cur = mysql.connection.cursor()
        # Updated SQL to write the age column parameters
        cur.execute("INSERT INTO tbl_user(user_name, user_age, user_email) VALUES (%s, %s, %s)", (name, age, email))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": "User added successfully! Modify your parameters to add more users: /userc?name=abc&age=25&email=abc.com"
        })
        return jsonify(user_list), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 6. ROUTE: DELETE USER BY URL QUERY PARAMETER (BY NAME)
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
        
        cur.execute("SELECT user_id FROM tbl_user WHERE user_name = %s", (name,))
        if not cur.fetchone():
            user_list = get_all_users_list(cur)
            cur.close()
            user_list.append({
                "error": f"User '{name}' not found.",
                "instruction": "Verify spelling or review active profiles at /users"
            })
            return jsonify(user_list), 404
            
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
