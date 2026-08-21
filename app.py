from flask import Flask, render_template, request, jsonify, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "app-secret-key"


import os
import threading
from xhtml2pdf import pisa # type: ignore
from io import BytesIO
from email_service import trigger_email
from database import init_db

init_db()


@app.route('/')
def index():
    return render_template('index.html')


# -- Authentication Endpoints -- #
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password)
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, hashed_pw, name))
        conn.commit()
        trigger_email(email, "Welcome to BookUrTicket!", f"Hi {name},\n\nThank you for registering on BookUrTicket.")
        with open('auth.log', 'a') as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] REGISTRATION SUCCESS: {email}\n")
        return jsonify({"success": True, "message": "Registered successfully."}), 201
    except sqlite3.IntegrityError:
        with open('auth.log', 'a') as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] REGISTRATION FAILED: Email already exists - {email}\n")
        return jsonify({"error": "Email already exists"}), 409
    finally:
        if conn: conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    
    with open('auth.log', 'a') as f:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not user:
            f.write(f"[{timestamp}] LOGIN FAILED: User not found - {email}\n")
        elif not check_password_hash(user['password'], password):
            f.write(f"[{timestamp}] LOGIN FAILED: Incorrect password - {email}\n")
        else:
            f.write(f"[{timestamp}] LOGIN SUCCESS: {email}\n")
    
    if user:
        if check_password_hash(user['password'], password):
            session['user_email'] = email
            session['user_name'] = user['name']
            trigger_email(email, "New Login to BookUrTicket", f"Hi {user['name']},\n\nNew login detected. No action required if this was you.")
            return jsonify({"success": True, "user": {"name": user['name'], "email": user['email'], "avatar_url": dict(user).get('avatar_url')}})
        else:
            # Special hint for Google Login simulation accounts
            if check_password_hash(user['password'], "google-oauth-dummy"):
                return jsonify({"error": "This account was created via Google Login. Please use the 'Sign in with Google' button."}), 401
            return jsonify({"error": "Incorrect password. Please try again."}), 401
    
    return jsonify({"error": "Invalid email and password please register"}), 401
    
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email', '').strip().lower()
    
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        # Realistic security practice: Don't leak whether an email exists or not
        return jsonify({"success": True, "message": "If an account exists with this email, a temporary password has been sent."})
        
    import random
    import string
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_pw = generate_password_hash(temp_password)
    
    c.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
    conn.commit()
    conn.close()
    
    trigger_email(email, "Password Reset - BookUrTicket", f"Hi {user['name']},\n\nYou requested a password reset.\nYour new temporary password is: {temp_password}\n\nPlease login using this password and update it from your profile immediately.\n\nThanks,\nBookUrTicket Team")
    
    return jsonify({"success": True, "message": "A temporary password has been sent to your email."})

@app.route('/api/google-login', methods=['POST'])
def google_login():
    data = request.json
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    if not email: return jsonify({"error": "Invalid payload"}), 400
        
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    
    avatar_url = None
    if not user:
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, generate_password_hash("google-oauth-dummy"), name))
        conn.commit()
        trigger_email(email, "Welcome to BookUrTicket via Google!", f"Hi {name},\n\nThank you for registering via Google.")
    else:
        avatar_url = dict(user).get('avatar_url')
    
    session['user_email'] = email
    session['user_name'] = name
    conn.close()
    
    return jsonify({"success": True, "user": {"name": name, "email": email, "avatar_url": avatar_url}})
    
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/me', methods=['GET'])
def get_me():
    if 'user_email' in session:
        conn = sqlite3.connect('movies.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT name, email, avatar_url FROM users WHERE email=?", (session['user_email'],))
        user = c.fetchone()
        conn.close()
        if user:
            return jsonify({"success": True, "user": {"name": user['name'], "email": user['email'], "avatar_url": user['avatar_url']}})
    return jsonify({"success": False}), 401

@app.route('/api/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'user_email' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    if 'avatar' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['avatar']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']: return jsonify({"error": "Invalid file type"}), 400
            
        safe_filename = f"avatar_{session['user_email'].replace('@','_')}.{ext}"
        filepath = os.path.join('static', 'images', 'avatars', safe_filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        web_path = filepath.replace('\\', '/')
        avatar_url = f"/{web_path}"
        
        conn = sqlite3.connect('movies.db')
        c = conn.cursor()
        c.execute("UPDATE users SET avatar_url=? WHERE email=?", (avatar_url, session['user_email']))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "avatar_url": avatar_url})

@app.route('/api/delete-avatar', methods=['POST'])
def delete_avatar():
    if 'user_email' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("UPDATE users SET avatar_url=NULL WHERE email=?", (session['user_email'],))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user_email' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    new_password = data.get('new_password')
    if not new_password: return jsonify({"error": "Missing new password"}), 400
    
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (generate_password_hash(new_password), session['user_email']))
    conn.commit()
    conn.close()
    
    trigger_email(session['user_email'], "Password Changed", "Your password was recently updated on BookUrTicket.")
    return jsonify({"success": True})

# -- Core App Endpoints -- #
@app.route('/api/movies', methods=['GET'])
def get_movies():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Process boolean
    for m in movies:
        m['is_top'] = bool(m['is_top'])
        
    return jsonify(movies)

@app.route('/api/movies/<int:movie_id>/showtimes', methods=['GET'])
def get_showtimes(movie_id):
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM showtimes WHERE movie_id=?", (movie_id,))
    showtimes = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(showtimes)

@app.route('/api/showtimes/<int:showtime_id>/seats', methods=['GET'])
def get_booked_seats(showtime_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT seats FROM bookings WHERE showtime_id=?", (showtime_id,))
    bookings = c.fetchall()
    conn.close()
    
    booked_seats = []
    for booking in bookings:
        seats = booking[0].split(',')
        booked_seats.extend(seats)
        
    return jsonify({"booked": booked_seats})

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    showtime_id = data.get('showtime_id')
    seats = data.get('seats')
    user_email = data.get('user_email')
    movie_title = data.get('movie_title')
    time = data.get('time')
    amount = data.get('amount', 0)
    
    if not all([showtime_id, seats, user_email]): return jsonify({"error": "Missing data"}), 400
    
    if 'user_email' not in session or session['user_email'] != user_email:
        return jsonify({"error": "Unauthorized user"}), 401
        
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    c.execute("SELECT seats FROM bookings WHERE showtime_id=?", (showtime_id,))
    bookings = c.fetchall()
    booked_seats = []
    for booking in bookings:
        booked_seats.extend(booking[0].split(','))
        
    for seat in seats:
        if seat in booked_seats:
            conn.close()
            return jsonify({"error": f"Seat {seat} is already booked"}), 400
            
    c.execute("INSERT INTO bookings (showtime_id, seats, user_email, amount) VALUES (?, ?, ?, ?)", 
             (showtime_id, ",".join(seats), user_email, amount))
    booking_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Generate PDF and Send Email with Attachment flawlessly via Server
    pdf_path = generate_ticket_pdf(booking_id)
    
    trigger_email(user_email, "Booking Confirmed - Ticket Attached!", 
                  f"Hi,\n\nYour booking is confirmed for {movie_title} at {time}.\n"
                  f"Please find your official E-Ticket attached perfectly to this email.\n\n"
                  f"Enjoy your movie!", attachment_path=pdf_path)
                  
    return jsonify({"success": True, "booking_id": booking_id}), 201


def generate_ticket_pdf(booking_id):
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.seats, b.amount, s.time, m.title, m.image_url, u.name as user_name, u.email as user_email
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        LEFT JOIN users u ON b.user_email = u.email
        WHERE b.id = ?
    ''', (booking_id,))
    t = c.fetchone()
    conn.close()
    
    from datetime import datetime
    current_date_str = datetime.now().strftime("%b %d, %Y").upper()
    
    # THE ULTIMATE PDF REPLICA (matching the website perfectly)
    html = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4 landscape; margin: 2cm; }}
            body {{ font-family: 'Helvetica', 'Arial', sans-serif; background-color: #f8f9fa; color: #fff; }}
            .ticket-table {{ width: 800px; background-color: #000; border-radius: 15px; border: 1px solid #ffd700; overflow: hidden; }}
            .left-sec {{ width: 550px; padding: 40px; border-right: 2px dashed #ffd700; vertical-align: top; }}
            .right-sec {{ width: 250px; background-color: #ffd700; color: #000; padding: 30px; text-align: center; vertical-align: middle; }}
            .cinema-name {{ color: #ffd700; font-weight: bold; font-size: 11pt; letter-spacing: 2px; margin-bottom: 20px; }}
            .movie-title {{ font-size: 38pt; font-weight: 900; line-height: 1.1; margin-bottom: 25px; color: #fff; }}
            .info-label {{ color: #888; font-size: 9pt; text-transform: uppercase; margin-bottom: 3px; }}
            .info-val {{ color: #fff; font-size: 14pt; font-weight: bold; margin-bottom: 18px; }}
            .stub-label {{ color: #333; font-size: 11pt; font-weight: bold; margin-bottom: 8px; }}
            .stub-amount {{ font-size: 34pt; font-weight: bold; color: #000; }}
            .barcode-line {{ background-color: #fff; height: 1px; width: 100%; margin-top: 10px; opacity: 0.3; }}
            .barcode-line-stub {{ background-color: #000; height: 1px; width: 100%; margin-top: 15px; opacity: 0.6; }}
        </style>
    </head>
    <body>
        <table class="ticket-table" cellspacing="0" cellpadding="0">
            <tr>
                <td class="left-sec">
                    <div class="cinema-name">BOOKURTICKET PREMIUM</div>
                    <div class="movie-title">{t['title'].upper()}</div>
                    
                    <table width="100%">
                        <tr>
                            <td colspan="2" style="padding-bottom: 25px;">
                                <div class="info-label">Issued to</div>
                                <div style="font-size: 38pt; font-weight: 900; color: #ffd700; line-height: 1; margin-bottom: 5px;">{t['user_name'] or 'GUEST'}</div>
                                <div style="font-size: 28pt; font-weight: bold; color: #ffffff;">{t['user_email'] or 'N/A'}</div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="info-label">Date</div>
                                <div class="info-val">{current_date_str}</div>
                            </td>
                            <td>
                                <div class="info-label">Showtime</div>
                                <div class="info-val">{t['time']}</div>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding-top: 5px;">
                                <div class="info-label">Seats</div>
                                <div class="info-val">{t['seats']}</div>
                            </td>
                        </tr>
                    </table>
                    <div class="barcode-line"></div>
                    <div style="font-size: 7pt; color: #666; margin-top: 5px;">SERIAL: BK-{t['seats'][0:2].upper()}-{booking_id}</div>
                </td>
                <td class="right-sec">
                    <div class="stub-label">TOTAL PAID</div>
                    <div class="stub-amount">Rs. {t['amount']:.2f}</div>
                    <div class="barcode-line-stub"></div>
                    <div style="font-size: 8pt; margin-top: 10px; font-weight: bold;">OFFICIAL PASS ✅</div>
                    <div style="font-size: 7pt; margin-top: 20px; opacity: 0.7;">Enjoy your movie!</div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    if not os.path.exists('tickets'): os.makedirs('tickets')
    filepath = f"tickets/Ticket_{booking_id}.pdf"
    
    with open(filepath, "wb") as f:
        pisa.CreatePDF(html, dest=f)
        
    return filepath

@app.route('/api/my-bookings', methods=['GET'])
def get_my_bookings():
    if 'user_email' not in session: 
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.seats, b.amount, s.time, m.title, m.image_url, m.language 
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE b.user_email = ?
    ''', (session['user_email'],))
    
    bookings = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(bookings)

@app.route('/api/ticket/<int:booking_id>')
def view_standalone_ticket(booking_id):
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.seats, b.amount, s.time, m.title, m.image_url, u.name as user_name, u.email as user_email
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        LEFT JOIN users u ON b.user_email = u.email
        WHERE b.id = ?
    ''', (booking_id,))
    ticket = c.fetchone()
    conn.close()
    if not ticket: return "Ticket not found", 404
    return render_template('ticket_view.html', t=ticket, booking_id=booking_id)

@app.route('/api/download-ticket/<int:booking_id>')
def download_standalone_ticket(booking_id):
    pdf_path = f"tickets/Ticket_{booking_id}.pdf"
    if not os.path.exists(pdf_path):
        return "PDF not generated yet. Please contact support.", 404
    return send_file(pdf_path, as_attachment=True, download_name=f"BookUrTicket_{booking_id}.pdf")


@app.route('/api/favorites', methods=['GET', 'POST'])
def handle_favorites():
    if 'user_email' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    user_email = session['user_email']

    if request.method == 'POST':
        data = request.json
        movie_id = data.get('movie_id')
        action = data.get('action') # 'add' or 'remove'
        
        if action == 'add':
            try:
                c.execute("INSERT INTO favorites (user_email, movie_id) VALUES (?, ?)", (user_email, movie_id))
            except sqlite3.IntegrityError:
                pass # Already exists
        else:
            c.execute("DELETE FROM favorites WHERE user_email=? AND movie_id=?", (user_email, movie_id))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    
    # GET favorites
    c.execute('''
        SELECT m.* FROM movies m
        JOIN favorites f ON m.id = f.movie_id
        WHERE f.user_email = ?
    ''', (user_email,))
    
    favs = [dict(row) for row in c.fetchall()]
    for m in favs: m['is_top'] = bool(m['is_top'])
    conn.close()
    return jsonify(favs)

def is_admin():
    return session.get('user_email') == 'admin@bookurticket.com'

@app.route('/api/admin/metrics', methods=['GET'])
def admin_metrics():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bookings")
    bookings_count = c.fetchone()[0]
    
    c.execute("SELECT SUM(amount) FROM bookings")
    revenue = c.fetchone()[0] or 0
    conn.close()
    return jsonify({"users": users_count, "bookings": bookings_count, "revenue": revenue})

@app.route('/api/admin/bookings', methods=['GET'])
def admin_all_bookings():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT b.id, b.user_email, u.name as user_name, b.seats, b.amount, s.time, m.title 
                 FROM bookings b 
                 JOIN showtimes s ON b.showtime_id = s.id 
                 JOIN movies m ON s.movie_id = m.id 
                 LEFT JOIN users u ON b.user_email = u.email
                 ORDER BY b.id DESC''')
    bookings = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(bookings)
    
@app.route('/api/admin/bookings/<int:booking_id>', methods=['DELETE'])
def admin_delete_booking(booking_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/admin/users', methods=['GET'])
def admin_all_users():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name, email FROM users ORDER BY id DESC")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/movies', methods=['POST'])
def admin_add_movie():
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("INSERT INTO movies (title, synopsis, image_url, genre, language, is_top, trailer_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
             (data['title'], data['synopsis'], data['image_url'], data['genre'], data['language'], data.get('is_top', False), data.get('trailer_url', "")))

    movie_id = c.lastrowid
    # Default showtimes
    c.executemany("INSERT INTO showtimes (movie_id, time) VALUES (?, ?)", [(movie_id, "10:00"), (movie_id, "14:30"), (movie_id, "19:00")])
    conn.commit()
    conn.close()
    return jsonify({"success": True})
    
@app.route('/api/admin/movies/<int:movie_id>', methods=['DELETE'])
def admin_delete_movie(movie_id):
    if not is_admin(): return jsonify({"error": "Unauthorized"}), 403
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    c.execute("DELETE FROM showtimes WHERE movie_id=?", (movie_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
