# app.py
from flask import Flask, render_template, session, redirect, url_for, request, flash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24) # Replace with a strong, unique secret key in production

# --- Dummy Data (for demonstration purposes) ---
users = {
    "test@example.com": {"password": "password123", "name": "Test User"},
    "bujji@example.com": {"password": "bujji123", "name": "Bujji"}
}

# In a real application, this would be stored in a database
bookings_db = []

# --- Routes ---

@app.route('/')
def index():
    """Renders the landing page."""
    return render_template('index.html')

@app.route('/home')
def home():
    """Renders the welcome page with login/signup options."""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == 'test@example.com' and password == 'password':
            session['logged_in'] = True
            session['user_email'] = email
            session['user_name'] = 'Test User'
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
        elif email in users:
            flash('Email already registered.', 'danger')
        else:
            users[email] = {"password": password, "name": name}
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handles forgot password requests."""
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            flash(f'A password reset link has been sent to {email}. (This is a dummy message)', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    """Renders the user dashboard."""
    if 'logged_in' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    user_name = session.get('user_name', 'Guest')
    return render_template('dashboard.html', user_name=user_name)

@app.route('/about_us')
def about_us():
    """Renders the About Us page."""
    return render_template('about_us.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Handles photographer booking."""
    if 'logged_in' not in session:
        flash('Please log in to book a photographer.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        booking_type = request.form['type']

        # Dummy price calculation based on type
        price_map = {
            "Wedding": 15000,
            "Events": 10000,
            "Birthday": 7000,
            "Tour": 8000,
            "Wildlife": 12000,
            "Adventure": 11000
        }
        price = price_map.get(booking_type, 5000) # Default price

        # Dummy photographer assignment
        photographer_name = "Assigned Photographer" # In a real app, this would be dynamic

        # Store booking details (in a real app, this goes to a DB)
        bookings_db.append({
            "event_type": booking_type,
            "booking_date": date,
            "booking_time": datetime.now().strftime("%H:%M"), # Dummy time
            "photographer_name": photographer_name,
            "status": "Pending",
            "price": price,
            "user_email": session['user_email']
        })

        flash('Booking confirmed!', 'success')
        return render_template('booking.html',
                               message="Your booking has been placed successfully!",
                               name=name,
                               location=location,
                               date=date,
                               type=booking_type,
                               price=price)
    return render_template('booking.html')

@app.route('/profile')
def profile():
    """Renders photographer profiles."""
    if 'logged_in' not in session:
        flash('Please log in to view photographer profiles.', 'warning')
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/booking_history')
def booking_history():
    """Renders the user's booking history."""
    if 'logged_in' not in session:
        flash('Please log in to view your booking history.', 'warning')
        return redirect(url_for('login'))
    
    user_bookings = [b for b in bookings_db if b['user_email'] == session['user_email']]
    return render_template('booking_history.html', bookings=user_bookings)

@app.route('/user_reviews')
def user_reviews():
    """Renders user reviews."""
    return render_template('user_reviews.html')

@app.route('/photographer_categories')
def photographer_categories():
    """Renders photographer categories."""
    return render_template('photographer_categories.html')

@app.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('logged_in', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, debug=True)
