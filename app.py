

from flask import Flask, render_template, request, redirect
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    auth_plugin='mysql_native_password',
    autocommit=True
)

cursor = db.cursor()

# Home page
@app.route('/')
def home():
    return render_template('home.html')


# Add customer
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute("INSERT INTO customers (name) VALUES (%s)", (name,))
        return redirect('/customers')
    
    return render_template('add_customer.html')


# Add purchase with reward percentage logic
@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        amount = float(request.form['amount'])

        # Reward percentage logic
        if amount <= 2000:
            percent = 3
            points = amount * 0.03
        elif amount <= 10000:
            percent = 5
            points = amount * 0.05
        else:
            percent = 7
            points = amount * 0.07

        points = int(points)

        # Insert purchase
        cursor.execute(
            "INSERT INTO purchases (customer_id, amount, points, purchase_date) VALUES (%s,%s,%s,CURDATE())",
            (customer_id, amount, points)
        )

        # Update customer total points
        cursor.execute(
            "UPDATE customers SET points = points + %s WHERE customer_id = %s",
            (points, customer_id)
        )

        return redirect('/leaderboard')

    # Load customers for dropdown
    cursor.execute("SELECT customer_id, name FROM customers")
    customers = cursor.fetchall()

    return render_template('add_purchase.html', customers=customers)


# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    cursor.execute("SELECT name, points FROM customers ORDER BY points DESC")
    data = cursor.fetchall()
    return render_template('leaderboard.html', data=data)


# View customers
@app.route('/customers')
def customers():
    cursor.execute("SELECT * FROM customers")
    data = cursor.fetchall()
    return render_template('customers.html', data=data)


# Purchase report
@app.route('/report')
def report():
    cursor.execute("""
        SELECT purchases.purchase_id, customers.name, purchases.amount, purchases.points, purchases.purchase_date
        FROM purchases
        JOIN customers ON purchases.customer_id = customers.customer_id
        ORDER BY purchases.purchase_date DESC
    """)
    data = cursor.fetchall()
    return render_template('report.html', data=data)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)