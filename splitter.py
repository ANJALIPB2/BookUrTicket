import os

# --- FRONTEND SPLIT ---
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def extract_section(start_marker, end_marker, filename):
    global html
    start = html.find(start_marker)
    if end_marker:
        end = html.find(end_marker)
    else:
        end = len(html)
        
    if start != -1 and end != -1:
        content = html[start:end]
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        # Add Jinja template include in its place
        include_tag = f"{{% include '{os.path.basename(filename)}' %}}\n        "
        html = html[:start] + include_tag + html[end:]

# Do it safely from bottom to top to preserve indices
extract_section("<!-- Admin View -->", "<!-- Authentication Modal -->", "templates/admin.html")
extract_section("<!-- Unified User Profile Dashboard -->", "{% include 'admin.html' %}", "templates/profile.html")
extract_section("<!-- Cinemas View -->", "{% include 'profile.html' %}", "templates/cinemas.html")
extract_section("<!-- Hero Section -->", "{% include 'cinemas.html' %}", "templates/home.html")
extract_section("<!-- Navbar", "<main id=\"app-container\">", "templates/navbar.html")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Frontend HTML Split Successfully!")

# --- BACKEND SPLIT ---
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

# 1. database.py
db_start = app_py.find("# Initialize DB\ndef init_db():")
db_content = app_py[db_start:]
# init_db ends right at the end of the init_db call:
end_init = db_content.find("init_db()\n") + 10
actual_db_code = "import sqlite3\nfrom werkzeug.security import generate_password_hash\n\n" + db_content[:end_init]

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(actual_db_code)

# 2. email_service.py
email_start = app_py.find("# ==========================================\n# \U0001f4e7 REAL EMAIL CONFIGURATION")
email_end = app_py.find("# Initialize DB\ndef init_db():")
email_code = """import smtplib
from email.mime.text import MIMEText
import threading

""" + app_py[email_start:email_end]

with open('email_service.py', 'w', encoding='utf-8') as f:
    f.write(email_code)

# 3. Clean up app.py
new_app_py = app_py[:email_start] + "\nfrom email_service import trigger_email\nfrom database import init_db\n\ninit_db()\n\n" + app_py[email_start + end_init + (email_end - email_start):]

# Clean redundant imports from top of app.py
lines = new_app_py.split("\n")
clean_lines = []
for l in lines:
    if "import smtplib" in l or "MIMEText" in l or "MIMEMultipart" in l or "import threading" in l:
        continue
    clean_lines.append(l)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write("\n".join(clean_lines))

print("Backend Python Split Successfully!")
