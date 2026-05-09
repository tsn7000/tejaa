import os
from datetime import datetime
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super_secret_premium_key_2026"

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "fms_pro.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ==========================================
# 2. DATABASE MODELS
# ==========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class TimeTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    day = db.Column(db.String(20))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    subject = db.Column(db.String(100))
    user = db.relationship("User", backref="timetables")


class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_name = db.Column(db.String(100))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default="Pending")


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    content = db.Column(db.Text)


# ==========================================
# 3. PROFESSIONAL UI TEMPLATES
# ==========================================
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    :root { --primary: #4f46e5; --secondary: #6366f1; --bg: #f8fafc; --sidebar: #0f172a; --text: #334155; }
    * { margin:0; padding:0; box-sizing:border-box; font-family:'Inter', sans-serif; }
    body { background: var(--bg); display: flex; height: 100vh; overflow: hidden; color: var(--text); }
    
    .full-center { width:100%; height:100vh; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg, #0f172a, #1e293b); flex-direction: column; }
    .hidden { display: none; }
    
    .card { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .btn { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: 0.3s; }
    .btn:hover { background: #4338ca; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }
    .btn-green { background: #10b981; } .btn-green:hover { background: #059669; }
    .btn-red { background: #ef4444; } .btn-red:hover { background: #dc2626; }
    .input-field { width: 100%; padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 15px; font-size: 14px; outline: none; transition: 0.3s; }
    .input-field:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
    
    .sidebar { width: 280px; background: var(--sidebar); color: #cbd5e1; padding: 25px 20px; display: flex; flex-direction: column; transition: 0.3s; }
    .brand { font-size: 26px; font-weight: 700; color: #38bdf8; margin-bottom: 40px; text-align: center; letter-spacing: 1px;}
    .nav-btn { background: none; border: none; color: #94a3b8; padding: 15px 20px; text-align: left; cursor: pointer; width: 100%; font-size: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; align-items: center; transition: 0.3s; font-weight: 600;}
    .nav-btn i { margin-right: 15px; font-size: 18px; width: 20px; text-align: center; }
    .nav-btn:hover { background: rgba(255,255,255,0.05); color: white; transform: translateX(5px); }
    .nav-btn.active { background: var(--primary); color: white; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4); }
    .logout { margin-top: auto; color: #ef4444; } .logout:hover { background: rgba(239,68,68,0.1); color: #f87171; }
    
    .main { flex: 1; padding: 40px; overflow-y: auto; background: #f1f5f9; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; }
    .header h1 { font-size: 28px; color: #0f172a; }
    .time-badge { background: white; padding: 10px 20px; border-radius: 50px; font-weight: 600; box-shadow: 0 2px 10px rgba(0,0,0,0.05); color: var(--primary); display:flex; align-items:center; gap:8px;}
    
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px; margin-bottom: 35px; }
    .stat-card { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-left: 6px solid var(--primary); display: flex; align-items: center; justify-content: space-between; transition: 0.3s;}
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.08); }
    .stat-card.green { border-color: #10b981; } .stat-card.red { border-color: #ef4444; } .stat-card.blue { border-color: #3b82f6; }
    .stat-info h3 { font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;}
    .stat-info h2 { font-size: 36px; color: #0f172a; }
    .stat-icon { font-size: 45px; color: #f1f5f9; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { text-align: left; color: #64748b; padding: 15px; border-bottom: 2px solid #e2e8f0; font-weight: 600; text-transform: uppercase; font-size: 13px; }
    td { padding: 15px; border-bottom: 1px solid #f1f5f9; font-size: 15px; vertical-align: middle;}
    tr:hover td { background: #f8fafc; }
    .badge { padding: 6px 14px; border-radius: 50px; font-size: 12px; font-weight: 700; display:inline-block;}
    .busy { background: #fee2e2; color: #b91c1c; } .free { background: #dcfce7; color: #15803d; }
    
    .alert { background: #dcfce7; color: #15803d; padding: 15px 20px; margin-bottom: 25px; border-radius: 8px; font-weight: 600; border-left: 4px solid #10b981; display:flex; align-items:center; gap:10px; animation: slideDown 0.4s ease-out;}
    .alert-error { background: #fee2e2; color: #b91c1c; border-left: 4px solid #ef4444; }
    @keyframes slideDown { from{opacity:0; transform:translateY(-10px);} to{opacity:1; transform:translateY(0);} }
</style>
<script>
    function showTab(tabId, btnId) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
        document.getElementById(tabId).classList.remove('hidden');
        document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
        document.getElementById(btnId).classList.add('active');
    }
</script>
"""

HOME_HTML = (
    CSS_STYLE
    + """
<div class="full-center">
    <div class="card" style="width:550px; text-align:center; padding: 60px 40px; border-top: 8px solid var(--primary);">
        <div style="background:#eff6ff; width:100px; height:100px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin: 0 auto 25px;">
            <i class="fas fa-university" style="font-size:50px; color:var(--primary);"></i>
        </div>
        <h1 style="color:#0f172a; margin-bottom:15px; font-size: 32px;">KJ's Trinity FMS Portal</h1>
        <p style="color:#64748b; margin-bottom:45px; font-size:16px;">Welcome to the Next-Gen Faculty Management System.</p>
        
        <div style="display:flex; gap:20px; justify-content:center;">
            <a href="/login/hod" class="btn" style="flex:1; padding:20px; font-size:18px;"><i class="fas fa-user-tie"></i> HOD Portal</a>
            <a href="/login/faculty" class="btn" style="flex:1; padding:20px; font-size:18px; background:#475569;"><i class="fas fa-chalkboard-teacher"></i> Faculty Portal</a>
        </div>
    </div>
</div>
"""
)

LOGIN_HTML = (
    CSS_STYLE
    + """
<div class="full-center" style="background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.9)), url('{{ url_for('static', filename='college_bg.png') }}') no-repeat center center/cover;">
    <div class="card" style="width:420px; text-align:center; padding: 50px 40px; background: rgba(255, 255, 255, 0.95); box-shadow: 0 20px 40px rgba(0,0,0,0.4); border-top: 5px solid var(--primary);">
        <i class="fas {{ 'fa-user-tie' if role_type == 'HOD' else 'fa-chalkboard-teacher' }}" style="font-size:50px; color:var(--primary); margin-bottom:20px;"></i>
        <h2 style="color:#0f172a; margin-bottom:30px;">{{ role_type }} Secure Login</h2>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}<div class="alert alert-error" style="justify-content:center; padding:10px; font-size:14px;"><i class="fas fa-exclamation-circle"></i> {{ messages[0] }}</div>{% endif %}
        {% endwith %}
        
        <form method="POST">
            <div style="position:relative;">
                <i class="fas fa-user" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                <input type="text" name="username" class="input-field" placeholder="Username" style="padding-left:45px;" required>
            </div>
            <div style="position:relative;">
                <i class="fas fa-lock" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                <input type="password" name="password" class="input-field" placeholder="Password" style="padding-left:45px;" required>
            </div>
            
            <div style="text-align:right; margin-bottom: 15px;">
                <a href="/forgot_password/{{ role_type|lower }}" style="font-size:13px; color:var(--primary); font-weight:600; text-decoration:none;">Forgot Password?</a>
            </div>

            <button class="btn" style="width:100%; font-size:16px; padding:14px; background:var(--primary);">Secure Login <i class="fas fa-sign-in-alt"></i></button>
        </form>
        <div style="margin-top:25px;"><a href="/" style="color:#64748b; text-decoration:none; font-weight:600; transition:0.3s;"><i class="fas fa-arrow-left"></i> Return to Home</a></div>
    </div>
</div>
"""
)

FORGOT_PASS_HTML = (
    CSS_STYLE
    + """
<div class="full-center" style="background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.9)), url('{{ url_for('static', filename='college_bg.png') }}') no-repeat center center/cover;">
    <div class="card" style="width:420px; text-align:center; padding: 50px 40px; background: rgba(255, 255, 255, 0.95); box-shadow: 0 20px 40px rgba(0,0,0,0.4); border-top: 5px solid #ef4444;">
        <i class="fas fa-unlock-alt" style="font-size:50px; color:#ef4444; margin-bottom:20px;"></i>
        <h2 style="color:#0f172a; margin-bottom:10px;">Reset Password</h2>
        <p style="color:#64748b; font-size:13px; margin-bottom:25px;">Verify your identity to reset your password.</p>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}<div class="alert alert-error" style="justify-content:center; padding:10px; font-size:14px;"><i class="fas fa-exclamation-circle"></i> {{ messages[0] }}</div>{% endif %}
        {% endwith %}
        
        <form method="POST">
            <div style="position:relative;">
                <i class="fas fa-user" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                <input type="text" name="username" class="input-field" placeholder="Your Username" style="padding-left:45px;" required>
            </div>
            <div style="position:relative;">
                <i class="fas fa-id-card" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                <input type="text" name="full_name" class="input-field" placeholder="Your Full Name (e.g. Prof. Lakhan)" style="padding-left:45px;" required>
            </div>
            <div style="position:relative;">
                <i class="fas fa-key" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                <input type="password" name="new_password" class="input-field" placeholder="Enter New Password" style="padding-left:45px;" required>
            </div>
            
            <button class="btn btn-red" style="width:100%; margin-top:10px; font-size:16px; padding:14px;">Reset Password <i class="fas fa-save"></i></button>
        </form>
        <div style="margin-top:25px;"><a href="/login/{{ role_type|lower }}" style="color:#64748b; text-decoration:none; font-weight:600; transition:0.3s;"><i class="fas fa-arrow-left"></i> Back to Login</a></div>
    </div>
</div>
"""
)

DASHBOARD_HTML = (
    CSS_STYLE
    + """
<div class="sidebar">
    <div class="brand"><i class="fas fa-layer-group"></i> FMS Pro</div>
    
    {% if user.role == 'HOD' %}
    <button id="btn1" class="nav-btn active" onclick="showTab('tab-status', 'btn1')"><i class="fas fa-chart-pie"></i> Live Monitor</button>
    <button id="btn-master" class="nav-btn" onclick="showTab('tab-master', 'btn-master')"><i class="fas fa-table"></i> Master Timetable</button>
    <button id="btn2" class="nav-btn" onclick="showTab('tab-leaves', 'btn2')"><i class="fas fa-envelope-open-text"></i> Leave Requests</button>
    <button id="btn3" class="nav-btn" onclick="showTab('tab-notices', 'btn3')"><i class="fas fa-broadcast-tower"></i> Broadcast Notice</button>
    {% endif %}

    {% if user.role == 'Faculty' %}
    <button id="btn1" class="nav-btn active" onclick="showTab('tab-notices', 'btn1')"><i class="fas fa-clipboard-list"></i> Notice Board</button>
    <button id="btn2" class="nav-btn" onclick="showTab('tab-my-tt', 'btn2')"><i class="fas fa-calendar-check"></i> My Schedule</button>
    <button id="btn3" class="nav-btn" onclick="showTab('tab-apply', 'btn3')"><i class="fas fa-plane-departure"></i> Apply Leave</button>
    {% endif %}
    
    <button id="btn-set" class="nav-btn" onclick="showTab('tab-settings', 'btn-set')"><i class="fas fa-user-cog"></i> Settings</button>
    <a href="/logout" class="nav-btn logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
</div>

<div class="main">
    <div class="header">
        <div>
            <h1>Welcome back, {{ user.name }} 👋</h1>
            <p style="color:#64748b; margin-top:5px; font-size:15px;"><i class="fas fa-id-badge"></i> Role: {{ user.role }}</p>
        </div>
        <div class="time-badge"><i class="far fa-calendar-alt"></i> {{ day_now }} &nbsp;|&nbsp; <i class="far fa-clock"></i> {{ time_now }}</div>
    </div>

    {% with messages = get_flashed_messages() %}
        {% if messages %}<div class="alert"><i class="fas fa-check-circle"></i> {{ messages[0] }}</div>{% endif %}
    {% endwith %}

    {% if user.role == 'HOD' %}
    <div id="tab-status" class="tab-content">
        <div class="stat-grid">
            <div class="stat-card blue"><div class="stat-info"><h3>Total Faculty</h3><h2>{{ stats.total }}</h2></div><i class="fas fa-users stat-icon"></i></div>
            <div class="stat-card green"><div class="stat-info"><h3>Available Now</h3><h2>{{ stats.free }}</h2></div><i class="fas fa-coffee stat-icon"></i></div>
            <div class="stat-card red"><div class="stat-info"><h3>In Class (Busy)</h3><h2>{{ stats.busy }}</h2></div><i class="fas fa-chalkboard-teacher stat-icon"></i></div>
        </div>

        <div class="card">
            <h3 style="margin-bottom:20px; color:#0f172a;"><i class="fas fa-satellite-dish" style="color:var(--primary); margin-right:8px;"></i> Live Faculty Tracking System</h3>
            <table>
                <tr><th>Faculty Name</th><th>Current Status</th><th>Ongoing Activity</th></tr>
                {% for f in faculty_data %}
                <tr>
                    <td>
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="width:36px; height:36px; border-radius:50%; background:#e2e8f0; display:flex; align-items:center; justify-content:center; font-weight:bold; color:#475569;">{{ f.name[0] }}</div>
                            <b style="color:#334155;">{{ f.name }}</b>
                        </div>
                    </td>
                    <td><span class="badge {{ 'busy' if f.is_busy else 'free' }}"><i class="fas {{ 'fa-spinner fa-spin' if f.is_busy else 'fa-check' }}"></i> {{ 'ENGAGED' if f.is_busy else 'AVAILABLE' }}</span></td>
                    <td style="color:#64748b;">{{ f.activity }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <div id="tab-master" class="tab-content hidden">
        <div class="card">
            <h3 style="margin-bottom:20px;"><i class="fas fa-table" style="color:var(--primary); margin-right:8px;"></i> College Master Timetable</h3>
            <table>
                <tr><th>Faculty Name</th><th>Day</th><th>Time Slot</th><th>Class & Subject</th></tr>
                {% for t in all_tt %}
                <tr>
                    <td><b style="color:#334155;">{{ t.user.name }}</b></td>
                    <td>{{ t.day }}</td>
                    <td><span style="background:#f1f5f9; padding:5px 10px; border-radius:6px; font-size:13px; color:#475569;"><i class="far fa-clock"></i> {{ t.start_time }} - {{ t.end_time }}</span></td>
                    <td style="font-weight:600;">{{ t.subject }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    
    <div id="tab-leaves" class="tab-content hidden">
        <div class="card">
            <h3 style="margin-bottom:20px;"><i class="fas fa-inbox" style="color:var(--primary); margin-right:8px;"></i> Pending Leave Requests</h3>
            <table>
                <tr><th>Applicant</th><th>Reason for Leave</th><th>Duration</th><th>Quick Action</th></tr>
                {% for l in leaves %}
                <tr>
                    <td><b style="color:#334155;">{{ l.user_name }}</b></td><td>{{ l.reason }}</td><td><i class="far fa-calendar" style="color:#94a3b8;"></i> {{ l.start_date }} to {{ l.end_date }}</td>
                    <td>
                        <form method="POST" action="/handle_leave" style="display:flex; gap:8px;">
                            <input type="hidden" name="leave_id" value="{{ l.id }}">
                            <button name="action" value="Approved" class="btn btn-green" style="padding:8px 12px;"><i class="fas fa-check"></i></button>
                            <button name="action" value="Rejected" class="btn btn-red" style="padding:8px 12px;"><i class="fas fa-times"></i></button>
                        </form>
                    </td>
                </tr>
                {% else %}<tr><td colspan="4" style="text-align:center; padding:40px; color:#94a3b8;">No pending requests.</td></tr>{% endfor %}
            </table>
        </div>
    </div>
    
    <div id="tab-notices" class="tab-content hidden">
        <div class="card" style="border-top: 5px solid var(--primary);">
            <h3 style="margin-bottom:20px;"><i class="fas fa-bullhorn" style="color:var(--primary); margin-right:8px;"></i> Broadcast Official Notice</h3>
            <form method="POST" action="/update_notice">
                <textarea name="content" class="input-field" rows="6" placeholder="Type important announcements here..." required>{{ inst_notice }}</textarea>
                <button class="btn"><i class="fas fa-paper-plane"></i> Publish to Portal</button>
            </form>
        </div>
    </div>
    {% endif %}

    {% if user.role == 'Faculty' %}
    <div id="tab-notices" class="tab-content">
        <div class="stat-grid">
            <div class="stat-card blue"><div class="stat-info"><h3>Lectures Today</h3><h2>{{ stats.today_classes }}</h2></div><i class="fas fa-book-reader stat-icon"></i></div>
            <div class="stat-card green"><div class="stat-info"><h3>Leaves Approved</h3><h2>{{ stats.total_leaves }}</h2></div><i class="fas fa-umbrella-beach stat-icon"></i></div>
        </div>
        <div class="card" style="border-left: 5px solid var(--primary);">
            <h3 style="margin-bottom:15px; color:#0f172a;"><i class="fas fa-university" style="color:var(--primary); margin-right:8px;"></i> Official Notice Board</h3>
            <div style="padding:25px; background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0;">
                <p style="font-size:16px; color:#334155; white-space: pre-wrap;"><i class="fas fa-quote-left" style="color:#cbd5e1; margin-right:10px;"></i>{{ inst_notice if inst_notice else "No recent updates." }}</p>
            </div>
        </div>
    </div>

    <div id="tab-my-tt" class="tab-content hidden">
        <div class="card">
            <h3 style="margin-bottom:20px;"><i class="fas fa-plus-circle" style="color:var(--primary); margin-right:8px;"></i> Add Class to Schedule</h3>
            <form method="POST" action="/add_tt" style="display:grid; grid-template-columns: 1fr 1fr 1fr 2fr auto; gap:15px; align-items:center;">
                <select name="day" class="input-field" style="margin:0;"><option>Monday</option><option>Tuesday</option><option>Wednesday</option><option>Thursday</option><option>Friday</option><option>Saturday</option></select>
                <input type="time" name="start" class="input-field" style="margin:0;" required>
                <input type="time" name="end" class="input-field" style="margin:0;" required>
                <input type="text" name="subject" placeholder="Subject/Class" class="input-field" style="margin:0;" required>
                <button class="btn" style="height:100%;"><i class="fas fa-save"></i> Save</button>
            </form>
        </div>
        <div class="card">
            <h3 style="margin-bottom:20px;"><i class="fas fa-calendar-week" style="color:var(--primary); margin-right:8px;"></i> My Weekly Timetable</h3>
            <table>
                <tr><th>Day</th><th>Time Slot</th><th>Subject</th><th>Action</th></tr>
                {% for t in my_tt %}
                <tr>
                    <td><b style="color:#334155;">{{ t.day }}</b></td>
                    <td><span style="background:#f1f5f9; padding:5px 10px; border-radius:6px; font-size:13px; color:#475569;"><i class="far fa-clock"></i> {{ t.start_time }} - {{ t.end_time }}</span></td>
                    <td style="font-weight:600;">{{ t.subject }}</td>
                    <td><a href="/delete_tt/{{ t.id }}" class="btn btn-red" style="padding:8px 12px;"><i class="fas fa-trash"></i></a></td>
                </tr>
                {% else %}<tr><td colspan="4" style="text-align:center; padding:30px; color:#94a3b8;">No classes scheduled yet.</td></tr>{% endfor %}
            </table>
        </div>
    </div>

    <div id="tab-apply" class="tab-content hidden">
        <div class="card" style="max-width:700px;">
            <h3 style="margin-bottom:20px;"><i class="fas fa-file-signature" style="color:var(--primary); margin-right:8px;"></i> Submit Leave Application</h3>
            <form method="POST" action="/apply_leave">
                <label style="font-weight:600; font-size:14px; color:#475569; display:block; margin-bottom:8px;">Reason</label>
                <input type="text" name="reason" class="input-field" placeholder="Medical emergency, etc." required>
                <div style="display:flex; gap:20px;">
                    <div style="flex:1;"><label style="font-weight:600; font-size:14px; color:#475569; display:block; margin-bottom:8px;">Start Date</label><input type="date" name="start" class="input-field" required></div>
                    <div style="flex:1;"><label style="font-weight:600; font-size:14px; color:#475569; display:block; margin-bottom:8px;">End Date</label><input type="date" name="end" class="input-field" required></div>
                </div>
                <button class="btn" style="margin-top:15px;"><i class="fas fa-paper-plane"></i> Submit to HOD</button>
            </form>
        </div>
        <div class="card">
            <h3 style="margin-bottom:20px;"><i class="fas fa-history" style="color:var(--primary); margin-right:8px;"></i> History</h3>
             <table>
                <tr><th>Duration</th><th>Reason</th><th>Status</th></tr>
                {% for l in my_leaves %}
                <tr>
                    <td><i class="far fa-calendar-alt" style="color:#94a3b8; margin-right:5px;"></i> {{ l.start_date }} to {{ l.end_date }}</td>
                    <td style="color:#334155;">{{ l.reason }}</td>
                    <td>
                        {% if l.status == 'Approved' %}<span class="badge" style="background:#dcfce7; color:#15803d;"><i class="fas fa-check"></i> Approved</span>
                        {% elif l.status == 'Rejected' %}<span class="badge" style="background:#fee2e2; color:#b91c1c;"><i class="fas fa-times"></i> Rejected</span>
                        {% else %}<span class="badge" style="background:#fef3c7; color:#b45309;"><i class="fas fa-clock"></i> Pending</span>{% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    {% endif %}

    <div id="tab-settings" class="tab-content hidden">
        <div class="card" style="max-width:500px;">
            <h3 style="margin-bottom:20px;"><i class="fas fa-user-shield" style="color:var(--primary); margin-right:8px;"></i> Security Settings</h3>
            <form method="POST" action="/change_password">
                <label style="font-weight:600; font-size:14px; color:#475569; display:block; margin-bottom:8px;">Enter New Password</label>
                <div style="position:relative;">
                    <i class="fas fa-key" style="position:absolute; left:15px; top:15px; color:#94a3b8;"></i>
                    <input type="password" name="new_password" class="input-field" placeholder="Create strong password" style="padding-left:45px;" required>
                </div>
                <button class="btn" style="width:100%;"><i class="fas fa-save"></i> Save</button>
            </form>
        </div>
    </div>
</div>
"""
)


# ==========================================
# 4. APPLICATION LOGIC & ROUTES
# ==========================================
def get_live_status(faculty_id):
    now = datetime.now()
    today_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    slot = (
        TimeTable.query.filter_by(user_id=faculty_id, day=today_day)
        .filter(
            TimeTable.start_time <= current_time, TimeTable.end_time >= current_time
        )
        .first()
    )

    if slot:
        return True, f"In Class: {slot.subject}"
    return False, "Available"


@app.route("/")
def home():
    return render_template_string(HOME_HTML)


@app.route("/login/<role_type>", methods=["GET", "POST"])
def login(role_type):
    actual_role = "Faculty" if role_type.upper() == "FACULTY" else "HOD"

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        user = User.query.filter_by(username=u, password=p, role=actual_role).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Invalid Credentials!")

    return render_template_string(LOGIN_HTML, role_type=actual_role)


@app.route("/forgot_password/<role_type>", methods=["GET", "POST"])
def forgot_password(role_type):
    actual_role = "Faculty" if role_type.upper() == "FACULTY" else "HOD"

    if request.method == "POST":
        u = request.form["username"]
        fn = request.form["full_name"]
        new_p = request.form["new_password"]

        # Verify if the user exists with matching username and exactly matching Full Name
        user = User.query.filter_by(username=u, name=fn, role=actual_role).first()

        if user:
            user.password = new_p
            db.session.commit()
            flash("Password reset successfully! Please login with your new password.")
            return redirect(url_for("login", role_type=role_type.lower()))
        else:
            flash(
                "Identity Verification Failed! Username and Full Name do not match our records."
            )

    return render_template_string(FORGOT_PASS_HTML, role_type=actual_role)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])
    now = datetime.now()
    today_str = now.strftime("%A")

    inst_db = Notice.query.filter_by(type="institute").first()
    inst_notice = inst_db.content if inst_db else ""

    faculty_data, pending_leaves, my_tt, my_leaves, all_tt, stats = (
        [],
        [],
        [],
        [],
        [],
        {},
    )

    if user.role == "HOD":
        all_faculty = User.query.filter_by(role="Faculty").all()
        busy_count = 0
        for f in all_faculty:
            is_busy, activity = get_live_status(f.id)
            if is_busy:
                busy_count += 1
            faculty_data.append(
                {"name": f.name, "is_busy": is_busy, "activity": activity}
            )

        pending_leaves = (
            Leave.query.filter_by(status="Pending").order_by(Leave.id.desc()).all()
        )
        all_tt = TimeTable.query.order_by(TimeTable.day, TimeTable.start_time).all()
        stats = {
            "total": len(all_faculty),
            "busy": busy_count,
            "free": len(all_faculty) - busy_count,
        }

    elif user.role == "Faculty":
        my_tt = (
            TimeTable.query.filter_by(user_id=user.id)
            .order_by(TimeTable.day, TimeTable.start_time)
            .all()
        )
        my_leaves = (
            Leave.query.filter_by(user_id=user.id).order_by(Leave.id.desc()).all()
        )
        today_classes = len([t for t in my_tt if t.day == today_str])
        approved_leaves = len([l for l in my_leaves if l.status == "Approved"])
        stats = {"today_classes": today_classes, "total_leaves": approved_leaves}

    return render_template_string(
        DASHBOARD_HTML,
        user=user,
        faculty_data=faculty_data,
        leaves=pending_leaves,
        my_tt=my_tt,
        my_leaves=my_leaves,
        all_tt=all_tt,
        inst_notice=inst_notice,
        stats=stats,
        time_now=now.strftime("%I:%M %p"),
        day_now=today_str,
    )


@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        user.password = request.form["new_password"]
        db.session.commit()
        flash("Password updated successfully!")
    return redirect(url_for("dashboard"))


@app.route("/update_notice", methods=["POST"])
def update_notice():
    if "user_id" in session:
        notice = Notice.query.filter_by(type="institute").first()
        if not notice:
            db.session.add(Notice(type="institute", content=request.form["content"]))
        else:
            notice.content = request.form["content"]
        db.session.commit()
        flash("Notice broadcasted!")
    return redirect(url_for("dashboard"))


@app.route("/add_tt", methods=["POST"])
def add_tt():
    if "user_id" in session:
        db.session.add(
            TimeTable(
                user_id=session["user_id"],
                day=request.form["day"],
                start_time=request.form["start"],
                end_time=request.form["end"],
                subject=request.form["subject"],
            )
        )
        db.session.commit()
        flash("Class added!")
    return redirect(url_for("dashboard"))


@app.route("/delete_tt/<int:id>")
def delete_tt(id):
    slot = TimeTable.query.get(id)
    if slot and slot.user_id == session["user_id"]:
        db.session.delete(slot)
        db.session.commit()
        flash("Class removed!")
    return redirect(url_for("dashboard"))


@app.route("/apply_leave", methods=["POST"])
def apply_leave():
    user = User.query.get(session["user_id"])
    db.session.add(
        Leave(
            user_id=user.id,
            user_name=user.name,
            reason=request.form["reason"],
            start_date=request.form["start"],
            end_date=request.form["end"],
        )
    )
    db.session.commit()
    flash("Leave applied!")
    return redirect(url_for("dashboard"))


@app.route("/handle_leave", methods=["POST"])
def handle_leave():
    leave = Leave.query.get(request.form["leave_id"])
    if leave:
        leave.status = request.form["action"]
        db.session.commit()
        flash(f"Leave {request.form['action']}!")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ==========================================
# 5. DATABASE INITIALIZATION
# ==========================================
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(
            User(username="admin", password="123", name="Dr. Head of Dept", role="HOD")
        )

        faculties = [
            ("pratima", "Prof. Pratima"),
            ("lakhan", "Prof. Lakhan"),
            ("sunita", "Prof. Sunita"),
            ("shweta", "Prof. Shweta"),
            ("sumaira", "Prof. Sumaira"),
            ("matale", "Prof. Matale"),
            ("gulnaz", "Prof. Gulnaz"),
            ("snehal", "Prof. Snehal"),
            ("anand", "Prof. Anand"),
            ("priyanka", "Prof. Priyanka"),
            ("yogita", "Prof. Yogita"),
        ]

        faculty_ids = {}
        for uname, fname in faculties:
            u = User(username=uname, password="123", name=fname, role="Faculty")
            db.session.add(u)
            db.session.commit()
            faculty_ids[uname] = u.id

        tt_data = [
            (faculty_ids["pratima"], "Monday", "08:45", "09:45", "OE-II (SE-A & SE-B)"),
            (faculty_ids["shweta"], "Monday", "09:45", "10:45", "MIL (SE-B) & DS (BE)"),
            (faculty_ids["lakhan"], "Monday", "11:30", "12:30", "PA (SE-B)"),
            (faculty_ids["matale"], "Monday", "11:30", "12:30", "PS (SE-A)"),
            (faculty_ids["sumaira"], "Monday", "09:45", "10:45", "ES (SE-A)"),
            (faculty_ids["sumaira"], "Monday", "11:30", "12:30", "DSBA (TE)"),
            (faculty_ids["gulnaz"], "Monday", "13:45", "14:45", "CG (SE-A)"),
            (faculty_ids["snehal"], "Monday", "14:45", "15:45", "DBMSSS (SE-A)"),
            (faculty_ids["priyanka"], "Monday", "08:45", "09:45", "CNS (TE)"),
            (faculty_ids["anand"], "Monday", "09:45", "10:45", "CC (TE)"),
            (faculty_ids["yogita"], "Monday", "12:30", "13:30", "WAD (TE)"),
            (faculty_ids["sunita"], "Monday", "12:30", "13:30", "E-V (BE)"),
            (faculty_ids["lakhan"], "Tuesday", "08:45", "09:45", "PA (SE-A)"),
            (faculty_ids["pratima"], "Tuesday", "11:30", "12:30", "OE-II (SE-B)"),
            (faculty_ids["sunita"], "Tuesday", "12:30", "13:30", "DBMSSC (SE-B)"),
            (faculty_ids["gulnaz"], "Tuesday", "13:45", "14:45", "CG (SE-B)"),
            (faculty_ids["shweta"], "Tuesday", "14:45", "15:45", "MIL (SE-B)"),
            (faculty_ids["anand"], "Tuesday", "08:45", "09:45", "E-VI (BE)"),
            (faculty_ids["shweta"], "Tuesday", "09:45", "10:45", "DS (BE)"),
            (faculty_ids["priyanka"], "Tuesday", "08:45", "09:45", "CNS (TE)"),
            (faculty_ids["yogita"], "Tuesday", "09:45", "10:45", "WAD (TE)"),
            (faculty_ids["sumaira"], "Tuesday", "14:45", "15:45", "DSBA (TE)"),
            (faculty_ids["lakhan"], "Wednesday", "11:30", "12:30", "PA (SE-A)"),
            (faculty_ids["pratima"], "Wednesday", "11:30", "12:30", "OE-II (SE-A)"),
            (faculty_ids["snehal"], "Wednesday", "12:30", "13:30", "DBMSSS (SE-A)"),
            (faculty_ids["matale"], "Wednesday", "12:30", "13:30", "PS (SE-A)"),
            (faculty_ids["shweta"], "Wednesday", "09:45", "10:45", "DS (BE)"),
            (faculty_ids["sunita"], "Wednesday", "11:30", "12:30", "E-V (BE)"),
            (faculty_ids["yogita"], "Wednesday", "11:30", "12:30", "WAD (TE)"),
            (faculty_ids["sumaira"], "Wednesday", "12:30", "13:30", "DSBA (TE)"),
            (faculty_ids["priyanka"], "Wednesday", "14:45", "15:45", "CNS (TE)"),
            (faculty_ids["sunita"], "Thursday", "08:45", "09:45", "DBMSSC (SE-B)"),
            (faculty_ids["sumaira"], "Thursday", "09:45", "10:45", "ES (SE-B)"),
            (faculty_ids["lakhan"], "Thursday", "13:45", "14:45", "PA (SE-B)"),
            (faculty_ids["matale"], "Thursday", "14:45", "15:45", "PAS (SE-B)"),
            (faculty_ids["gulnaz"], "Thursday", "13:45", "14:45", "CG (SE-A)"),
            (faculty_ids["shweta"], "Thursday", "14:45", "15:45", "MIL (SE-A)"),
            (faculty_ids["gulnaz"], "Thursday", "08:45", "09:45", "SE (BE)"),
            (faculty_ids["anand"], "Thursday", "14:45", "15:45", "E-VI (BE)"),
            (faculty_ids["priyanka"], "Thursday", "08:45", "09:45", "CNS (TE)"),
            (faculty_ids["anand"], "Thursday", "13:45", "14:45", "CC (TE)"),
            (faculty_ids["lakhan"], "Friday", "14:45", "15:45", "PA (SE-A)"),
            (faculty_ids["anand"], "Friday", "08:45", "09:45", "E-VI (BE)"),
            (faculty_ids["sunita"], "Friday", "14:45", "15:45", "E-V (BE)"),
            (faculty_ids["sumaira"], "Friday", "09:45", "10:45", "DSBA (TE)"),
            (faculty_ids["yogita"], "Friday", "11:30", "12:30", "WAD (TE)"),
            (faculty_ids["priyanka"], "Friday", "12:30", "13:30", "CNS (TE)"),
            (faculty_ids["anand"], "Friday", "14:45", "15:45", "CC (TE)"),
        ]

        for user_id, day, start, end, sub in tt_data:
            db.session.add(
                TimeTable(
                    user_id=user_id,
                    day=day,
                    start_time=start,
                    end_time=end,
                    subject=sub,
                )
            )

        db.session.commit()


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
