from flask import Flask, render_template, redirect, url_for, request, session, flash
import boto3
from botocore.exceptions import ClientError
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ DynamoDB Connection ------------------
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

# Connect to tables
users_table = dynamodb.Table('Users')
bookings_table = dynamodb.Table('Bookings')


# ------------------ Routes ------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        try:
            users_table.put_item(Item={
                'email': email,
                'name': name,
                'password': password
            })
            flash("Signup successful. Please log in.", "success")
            return redirect(url_for('login'))

        except ClientError as e:
            flash(f"Error: {e.response['Error']['Message']}", "danger")

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')

            if user and user['password'] == password:
                session['logged_in'] = True
                session['user_email'] = email
                session['user_name'] = user.get('name', 'User')
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "danger")

        except ClientError as e:
            flash(f"Error: {e.response['Error']['Message']}", "danger")

    return render_template('login.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        flash(f"Password reset link sent to {email}.", "info")
        return redirect(url_for('login'))

    return render_template('forgot_password.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_name=session.get('user_name', ''))


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        type_ = request.form['type']
        email = session.get('user_email')

        # Price logic
        pricing = {
            "Wedding": 12000,
            "Events": 9000,
            "Birthday": 7500,
            "Tour": 10000,
            "Wildlife": 18000,
            "Adventure": 15000
        }
        price = pricing.get(type_, 10000)

        booking_id = str(uuid.uuid4())

        try:
            bookings_table.put_item(Item={
                'booking_id': booking_id,
                'user_email': email,
                'name': name,
                'location': location,
                'booking_date': date,
                'event_type': type_,
                'price': price,
                'photographer_name': "Assigned Photographer",
                'status': "Upcoming"
            })

            flash("✅ Booking Confirmed!", "success")
            return render_template('booking.html', message="✅ Booking Confirmed!",
                                   name=name, location=location, date=date, type=type_, price=price)

        except ClientError as e:
            flash(f"Error: {e.response['Error']['Message']}", "danger")

    return render_template('booking.html')


@app.route('/booking_history')
def booking_history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_email = session.get('user_email')
    try:
        response = bookings_table.scan(
            FilterExpression='user_email = :email',
            ExpressionAttributeValues={':email': user_email}
        )
        bookings = response.get('Items', [])
        # Sort by booking_date (assumes ISO 8601 format: YYYY-MM-DD)
        bookings.sort(key=lambda x: x['booking_date'], reverse=True)

        return render_template('booking_history.html', bookings=bookings)

    except ClientError as e:
        flash(f"Error retrieving bookings: {e.response['Error']['Message']}", "danger")
        return render_template('booking_history.html', bookings=[])


@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('profile.html')


@app.route('/user_reviews')
def user_reviews():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('user_reviews.html')


@app.route('/photographer_categories')
def photographer_categories():
    return render_template('photographer_categories.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
