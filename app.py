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

# Corrected Multi-Column Inverted Card-Based SPA Layout
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Floating Mini Card Dashboard</title>
    <!-- Absolute paths for CSS CDNs -->
    <link href="jsdelivr.net" rel="stylesheet">
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { 
            background-color: #f1f5f9;
            background-image: radial-gradient(#cbd5e1 1.5px, transparent 1.5px);
            background-size: 24px 24px;
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            padding-bottom: 180px; /* Safe padding room for bottom dock */
        }
        
        /* Floating Mini Visiting Card Layout */
        .mini-card {
            border: none;
            border-radius: 12px;
            padding: 16px;
            width: 240px; /* Precise mini size framework */
            min-height: 125px;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        /* Playful rotating sticky note simulation */
        .mini-card:nth-child(even) { transform: rotate(1deg); }
        .mini-card:nth-child(odd) { transform: rotate(-1deg); }
        
        .mini-card:hover {
            transform: scale(1.06) rotate(0deg) translateY(-4px) !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            z-index: 50;
        }

        /* Top-Right Cross Closing Button */
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
            padding-right: 18px; /* Avoid overlapping with cross btn */
        }
        
        .user-detail {
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(30, 41, 59, 0.7);
        }

        /* Fixed Flat Glass-Blur Control Dock along bottom viewport */
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
        }
        .btn-dock-submit:hover { background: #4338ca; }
        
        .btn-toggle-main {
            border-radius: 50px;
            font-weight: 600;
            padding: 12px 32px;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
            transition: all 0.2s;
        }
        .btn-toggle-main:hover { transform: translateY(-1px); }
        
        /* Toast aligned directly above the bottom input bar controls */
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
        
        /* Fixed horizontal dimensions constraint matrix */
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

    <!-- Main Container For Top Floating Cards Area -->
    <div class="container-fluid px-4 pt-4">
        <header class="mb-4 pb-2">
            <h3 class="fw-bold text-slate-800 m-0"><i class="bi bi-pin-angle-fill text-danger me-2"></i>Pinboard Board</h3>
        </header>

        <!-- Dynamic Card Flex Grid Wrap (Floating top area) -->
        <div id="cardsBoard" class="d-flex flex-wrap gap-3 align-items-start justify-content-start">
            <!-- Mini notes load dynamically here -->
        </div>
    </div>

    <!-- Status Toast Alert Banner Notification -->
    <div id="toastContainer">
        <div id="statusAlert" class="alert d-none shadow-lg border p-3 rounded-3 text-sm font-medium transition text-center" role="alert"></div>
    </div>

    <!-- Fixed Bottom User Entry Dock Component -->
    <div class="bottom-dock py-3">
        <div class="container-fluid px-4 px-md-5">
            
            <!-- Baseline State Trigger Button -->
            <div id="triggerButtonContainer" class="text-center">
                <button onclick="toggleFormTray(true)" id="mainToggleBtn" class="btn btn-primary btn-toggle-main">
                    <i class="bi bi-person-plus-fill me-1"></i> Add User
                </button>
            </div>

            <!-- Horizontal Rows Tray Configuration Layout -->
            <div id="formFieldsTray" class="hidden-fields-tray">
                <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
                    <h6 class="fw-bold text-slate-700 m-0"><i class="bi bi-file-earmark-person text-success me-1"></i> Input Profile Parameters</h6>
                    <button type="button" onclick="toggleFormTray(false)" class="btn-close" aria-label="Close"></button>
                </div>
                
                <!-- Fixed structural row grid preventing columns from dropping -->
                <form id="customerForm" class="row gx-3 gy-2 align-items-center">
                    <div class="col-12 col-md-4">
                        <input type="text" id="custName" required placeholder="Customer Full Name" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-12 col-md-2">
                        <input type="number" id="custAge" required min="1" max="120" placeholder="Age" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-12 col-md-4">
                        <input type="email" id="custEmail" required placeholder="Email Address (e.g. santosh@email.com)" class="form-control form-control-custom shadow-none">
                    </div>
                    <div class="col-12 col-md-2">
                        <button type="submit" class="btn btn-primary btn-dock-submit shadow-sm">
                            <i class="bi bi-check-circle-fill me-1"></i> Submit User
                        </button>
                    </div>
                </form>
            </div>
            
        </div>
    </div>

    <!-- AJAX SPA JavaScript Runtime Framework Core -->
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
                tray.classList.add('show');
                mainBtn.classList.add('d-none');
            } else {
                tray.classList.remove('show');
                mainBtn.classList.remove('d-none');
                document.getElementById('customerForm').reset();
            }
        }

        function showNotification(message, isSuccess = true) {
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = `alert shadow-lg border p-3 rounded-3 text-sm font-medium d-block ${isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle'}`;
            alertBox.innerHTML = `<i class="bi ${isSuccess ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2"></i> ${message}`;
            setTimeout(() => { alertBox.className = 'alert d-none'; }, 4000);
        }

        // 1. FETCH ASYNC: Pull user records and render top-floating mini cards
        async function fetchCustomerCards() {
            try {
                const response = await fetch(`${API_BASE_URL}/users`, { headers: dashboardHeaders });
                const data = await response.json();
                const board = document.getElementById('cardsBoard');
                board.innerHTML = '';

                const customers = data.filter(item => item.user_id !== undefined);

                if (customers.length === 0) {
                    board.innerHTML = `
                        <div class="w-100 text-center py-5 bg-white border border-secondary-subtle rounded-3 text-muted italic">
                            <i class="bi bi-clipboard-x display-6 d-block mb-2 opacity-50"></i> Pinboard workspace is currently empty.
                        </div>`;
                    return;
                }

                customers.forEach((customer, idx) => {
                    const assignedColor = pastelColors[idx % pastelColors.length];
                    
                    board.innerHTML += `
                        <div class="mini-card" style="background-color: ${assignedColor};">
                            <button onclick="dropCustomerCard('${customer.user_name}')" class="cross-delete-btn" title="Delete Card">
                                <i class="bi bi-x-lg" style="font-size: 0.75rem;"></i>
                            </button>
                            
                            <div>
                                <div class="user-title text-truncate">${customer.user_name}</div>
                                <div class="user-detail mt-1 fw-bold text-dark text-opacity-50">
                                    <i class="bi bi-hash small"></i> Age: ${customer.user_age} yrs
                                </div>
                            </div>
                            
                            <div class="pt-2 border-top border-dark border-opacity-10 mt-2">
                                <div class="user-detail text-truncate fw-semibold">
                                    <i class="bi bi-envelope-at-fill opacity-50 small"></i> ${customer.user_email}
                                </div>
                            </div>
                        </div>`;
                });
            } catch (err) {
                showNotification("Connection failure. Flask backend server unreachable.", false);
            }
        }

        // 2. POST ASYNC: Add entries from bottom layout form safely via AJAX
        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const age = document.getElementById('custAge').value;
            const email = document.getElementById('custEmail').value.trim();

            try {
                const res = await fetch(`${API_BASE_URL}/userc?name=${encodeURIComponent(name)}&age=${age}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    showNotification(`Mini card for "${name}" instantiated on top.`);
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

        // 3. DELETE ASYNC: Erase card parameter instantly via cross close button
        async function dropCustomerCard(name) {
            try {
                const res = await fetch(`${API_BASE_URL}/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    showNotification(`Mini card for "${name}" dropped successfully.`);
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
    
    <!-- Absolute path for Bootstrap JS bundle CDN -->
    <script src="jsdelivr.net"></script>
</body>
</html>
