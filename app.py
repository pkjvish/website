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

# Modern Bootstrap 5 Sticky Note Business Card SPA Dashboard UI Layout
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sticky Notes Customer Matrix</title>
    <!-- Absolute paths for CSS CDNs -->
    <link href="jsdelivr.net" rel="stylesheet">
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { 
            background-color: #e5e7eb; 
            background-image: radial-gradient(#d1d5db 1px, transparent 1px);
            background-size: 16px 16px;
            font-family: 'Segoe UI', system-ui, sans-serif; 
        }
        
        /* Sticky Note / Visiting Card Design Grid */
        .sticky-note-card {
            border: none;
            border-radius: 4px;
            padding: 24px;
            min-height: 200px;
            position: relative;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        /* Subtle rotation logic to make cards look like real stuck notes */
        .sticky-note-card:nth-child(even) { transform: rotate(1.5deg); }
        .sticky-note-card:nth-child(odd) { transform: rotate(-1.5deg); }
        .sticky-note-card:nth-child(3n) { transform: rotate(2deg); }
        
        .sticky-note-card:hover {
            transform: scale(1.05) rotate(0deg) !important;
            box-shadow: 10px 15px 25px rgba(0,0,0,0.15);
            z-index: 10;
        }
        
        /* Pin Header effect simulation */
        .sticky-note-card::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 12px;
            background-color: rgba(255,255,255,0.4);
            border-radius: 2px;
        }

        /* Sleek Cross Closing Action Button */
        .delete-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            border: none;
            background: transparent;
            color: rgba(0, 0, 0, 0.4);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .delete-btn:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }
        
        .card-name {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1f2937;
            letter-spacing: -0.5px;
        }
        
        .card-meta {
            font-size: 0.85rem;
            font-weight: 600;
            color: rgba(0,0,0,0.5);
        }
        
        .form-control { border-radius: 8px; border-color: #cbd5e1; }
        .form-control:focus { box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15); border-color: #4f46e5; }
        .btn-submit { border-radius: 8px; font-weight: 600; background: #4f46e5; border: none; }
        .btn-submit:hover { background: #4338ca; }
    </style>
</head>
<body>

    <div class="container py-5">
        <!-- Header -->
        <header class="d-flex flex-column flex-md-row justify-content-between align-items-md-center pb-3 mb-5 border-bottom border-secondary-subtle">
            <div>
                <h1 class="fw-black text-dark mb-1"><i class="bi bi-pin-angle-fill text-danger me-2"></i>Sticky Card Board</h1>
                <p class="text-muted mb-0">Single Page Matrix rendering random color visiting card layouts dynamically.</p>
            </div>
            <div class="mt-3 mt-md-0">
                <button onclick="fetchCustomerCards()" class="btn btn-light border shadow-sm btn-sm px-3 py-2 fw-semibold text-secondary">
                    <i class="bi bi-arrow-clockwise me-1 text-primary"></i> Refresh Board
                </button>
            </div>
        </header>

        <!-- Status Notification Banner -->
        <div id="statusAlert" class="alert d-none shadow-sm mb-4" role="alert"></div>

        <div class="row g-4">
            <!-- Left Side Control Panel Form -->
            <div class="col-12 col-lg-4">
                <div class="card shadow-sm border p-4 bg-white rounded-3 sticky-top" style="top: 24px; z-index: 100;">
                    <h5 class="fw-bold text-dark mb-4"><i class="bi bi-file-earmark-medical-fill text-success me-2"></i>Create Note Parameters</h5>
                    
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
                        <button type="submit" class="btn btn-primary btn-submit w-100 shadow-sm py-2">
                            <i class="bi bi-pin-fill me-1"></i> Pin to Dashboard
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Side Sticky Notes Pinboard display grid area -->
            <div class="col-12 col-lg-8">
                <h5 class="fw-bold text-dark mb-4"><i class="bi bi-kanban-fill text-primary me-2"></i>Active Board Deck</h5>
                
                <!-- Display Grid Layout Architecture -->
                <div id="cardsGrid" class="row row-cols-1 row-cols-md-2 g-4">
                    <!-- Cards mount here dynamically with unique colors via JS -->
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

        // Palette of distinct visiting note pastel hex colors
        const stickNoteColors = [
            '#fef08a', // Pastel Yellow
            '#fbcfe8', // Pastel Pink
            '#bbf7d0', // Pastel Green / Mint
            '#bfdbfe', // Pastel Blue
            '#e9d5ff', // Pastel Lavender
            '#fed7aa', // Pastel Orange
            '#ccfbf1'  // Pastel Teal
        ];

        function pushNotification(message, isSuccess = true) {
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = `alert shadow-sm border mb-4 d-block ${isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle'}`;
            alertBox.innerHTML = `<i class="bi ${isSuccess ? 'bi-check-circle' : 'bi-exclamation-triangle'}-fill me-2"></i> ${message}`;
            setTimeout(() => { alertBox.className = 'alert d-none'; }, 4000);
        }

        // 1. FETCH ASYNC: Read database array and construct diverse colored notes
        async function fetchCustomerCards() {
            try {
                const response = await fetch(`${API_BASE_URL}/users`, { headers: dashboardHeaders });
                const data = await response.json();
                const grid = document.getElementById('cardsGrid');
                grid.innerHTML = '';

                const customers = data.filter(item => item.user_id !== undefined);

                if (customers.length === 0) {
                    grid.innerHTML = `
                        <div class="col-12 w-100 text-center py-5 bg-white border border-secondary-subtle rounded-3 text-muted italic">
                            <i class="bi bi-clipboard-x display-5 d-block mb-2 text-muted"></i> Pinboard is currently empty.
                        </div>`;
                    return;
                }

                customers.forEach((customer, index) => {
                    // Unique color assignment math mapping strategy based on index sequence loops
                    const assignedColor = stickNoteColors[index % stickNoteColors.length];
                    
                    grid.innerHTML += `
                        <div class="col">
                            <div class="sticky-note-card shadow" style="background-color: ${assignedColor};">
                                <!-- Cross Delete Handle Button -->
                                <button onclick="dropCustomerCard('${customer.user_name}')" class="delete-btn" title="Remove Card">
                                    <i class="bi bi-x-lg font-bold" style="font-size: 0.9rem;"></i>
                                </button>
                                
                                <div class="mt-2">
                                    <div class="card-name text-truncate">${customer.user_name}</div>
                                    <div class="card-meta mt-1">
                                        <i class="bi bi-calendar-event me-1"></i> Age: ${customer.user_age} years old
                                    </div>
                                </div>
                                
                                <div class="pt-3 border-top border-dark border-opacity-10 mt-4">
                                    <div class="text-dark text-opacity-70 small text-truncate fw-medium">
                                        <i class="bi bi-envelope-at-fill me-1 opacity-50"></i> ${customer.user_email}
                                    </div>
                                    <div class="text-end text-dark text-opacity-25 font-monospace fs-7 fw-bold mt-2">
                                        #ID-${customer.user_id}
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });
            } catch (err) {
                pushNotification("Connection failure. Flask engine backend unreachable.", false);
            }
        }

        // 2. POST ASYNC: Appends notes onto live view layout
        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const age = document.getElementById('custAge').value;
            const email = document.getElementById('custEmail').value.trim();

            try {
                const res = await fetch(`${API_BASE_URL}/userc?name=${encodeURIComponent(name)}&age=${age}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    pushNotification(`Sticky visiting card for "${name}" pinned safely.`);
                    document.getElementById('customerForm').reset();
                    fetchCustomerCards();
                } else {
                    const errData = await res.json();
                    pushNotification(errData.error || "Failed to parse parameter inputs.", false);
                }
            } catch (err) {
                pushNotification("Network runtime processing error.", false);
            }
        });

        // 3. DELETE ASYNC: Erases note card map parameters instantly
        async function dropCustomerCard(name) {
            if (!confirm(`Wipe "${name}" from the active board?`)) return;
            try {
                const res = await fetch(`${API_BASE_URL}/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    pushNotification(`User card "${name}" successfully cleared from board configuration maps.`);
                    fetchCustomerCards();
                } else {
                    pushNotification(`Could not complete card deletion profile cycle.`, false);
                }
            } catch (err) {
                pushNotification("Network fault encountered during profile deletion execution.", false);
            }
        }

        window.onload = fetchCustomerCards;
    </script>
    
    <!-- Absolute path for Bootstrap JS bundle CDN -->
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

# 5. ROUTE: ADD USER VIA URL QUERY PARAMETERS
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
