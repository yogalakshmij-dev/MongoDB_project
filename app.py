from flask import Flask, render_template, request, redirect, url_for, flash, session
import re
from bson import ObjectId 
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "yoga@sql"
mongo_url = "mongodb+srv://yogaj1010:F8MpvAIdLJSvDf6l@cluster0.vbpts.mongodb.net/"

client = MongoClient(mongo_url)
db = client.emp_details
collection = db.employee
users_collection = db.users
employee_collection=db.employees

def validate_password(password):
    """ Validate password strength """
    if len(password) < 8:
        return False
    elif not re.search(r"[a-z]", password):
        return False
    elif not re.search(r"[A-Z]", password):
        return False
    elif not re.search(r"[0-9]", password):
        return False
    elif not re.search(r"[!@#$%^&*+=]", password):
        return False
    return True

# Signup page
@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another.", 'danger')
            return redirect(url_for('signup'))

        # Validate password
        if not validate_password(password):
            flash('Password should be at least 8 characters long and contain uppercase, lowercase, digit, and special characters.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password and save to database
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "password": hashed_password}
        users_collection.insert_one(user_data)

        flash("Signup successful! Please log in.", 'success')
        return redirect(url_for('login'))

    return render_template("signup.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Find the user in the database
        user = users_collection.find_one({"username": username})

        # Validate credentials
        if user and check_password_hash(user['password'], password):
            session['username'] = username  # Save username in session
            flash("Login successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", 'danger')

    return render_template("login.html")

# # Home page (protected by login)
# @app.route("/home")
# def home():
#     if 'username' in session:
#         current_date = datetime.now()  # Get the current date
#         return render_template("home.html", username=session['username'], current_date=current_date)
#     else:
#         flash("Please log in to access this page.", 'danger')
#         return redirect(url_for('login'))
    
# Home page (protected by login)
# @app.route("/home", methods=["GET", "POST"])
# def home():
#     if 'username' in session:
#         current_date = datetime.now()  # Get the current date
        
#         # Fetch user details from the database
#         user = users_collection.find_one({"username": session['username']})
        
#         # Pass the user details and current view to the template
#         view = request.args.get('view', 'default')  # Get the view from query params
#         return render_template("home.html", username=session['username'], current_date=current_date, user=user, view=view)
#     else:
#         flash("Please log in to access this page.", 'danger')
#         return redirect(url_for('login'))


# @app.route("/home", methods=["GET", "POST"])
# def home():
#     if 'username' in session:
#         current_date = datetime.now()  # Get the current date
#         user = users_collection.find_one({"username": session['username']})
#         view = request.args.get('view', 'default')

#         timesheet_entries = []  # Initialize empty list for timesheet entries

#         if view == 'timesheet':
#             # Fetch all timesheet entries from the database
#             timesheet_entries = collection.find()

#         return render_template(
#             "home.html", 
#             username=session['username'], 
#             current_date=current_date, 
#             user=user, 
#             view=view, 
#             timesheet_entries=timesheet_entries
#         )
#     else:
#         flash("Please log in to access this page.", 'danger')
#         return redirect(url_for('login'))

@app.route("/home", methods=["GET", "POST"])
def home():
    if 'username' in session:
        current_date = datetime.now()  # Get the current date
        user = users_collection.find_one({"username": session['username']})
        view = request.args.get('view', 'default')

        # Fetch employee details for the logged-in user
        employees = employee_collection.find_one({"username": session['username']})

        timesheet_entries = []  # Initialize empty list for timesheet entries

        if view == 'timesheet':
            # Fetch all timesheet entries from the database
            timesheet_entries = collection.find()

        return render_template(
            "home.html", 
            username=session['username'], 
            current_date=current_date, 
            user=user, 
            employee=employees,  # Pass employee details to the template
            view=view, 
            timesheet_entries=timesheet_entries
        )
    else:
        flash("Please log in to access this page.", 'danger')
        return redirect(url_for('login'))


    
#  #Profile    
# @app.route("/profile", methods=["GET"])
# def profile():
#     if 'username' in session:
#         user = users_collection.find_one({"username": session['username']})
#         if user:
#             employee = collection.find_one({"Name": user["username"]})  # Assuming Name matches the user's username
#             return render_template("home.html", user=user, employee=employee, view='profile')
#         else:
#             flash("User details not found.", 'danger')
#             return redirect(url_for('home'))
#     else:
#         flash("Please log in to access your profile.", 'danger')
#         return redirect(url_for('login'))




@app.route("/insert", methods=["GET", "POST"])
def insert():
    if 'username' not in session:  # Ensure the user is logged in
        flash("Please log in to add an entry.", 'danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        name = request.form.get("name")
        position = request.form.get("position")
        department = request.form.get("department")
        date = request.form.get("date")
        hours_worked = request.form.get("hours_worked")

        timesheet_entry = {
            "Name": name,
            "Position": position,
            "Department": department,
            "Date": date,
            "HoursWorked": hours_worked,
        }

        collection.insert_one(timesheet_entry)
        flash("Timesheet entry added successfully!", 'success')
        return redirect(url_for('home', view='timesheet'))

    return render_template("insert.html")




# Logout functionality
@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    flash("You have been logged out.", 'success')
    return redirect(url_for('login'))


@app.route('/timesheet/edit/<id>', methods=['GET', 'POST'])
def edit_timesheet(id):
    # Fetch the timesheet entry by ObjectId
    entry = collection.find_one({"_id": ObjectId(id)})

    if request.method == 'POST':
        # Update the entry with new data
        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "Date": request.form['date'],
                "Name": request.form['name'],
                "Position": request.form['position'],
                "Department": request.form['department'],
                "HoursWorked": request.form['hours_worked']
            }}
        )
        flash("Timesheet entry updated successfully!", 'success')
        return redirect(url_for('home', view='timesheet'))

    return render_template('edit_timesheet.html', entry=entry)

@app.route('/timesheet/delete/<id>', methods=['POST'])
def delete_timesheet(id):
    collection.delete_one({"_id": ObjectId(id)})
    flash("Timesheet entry deleted successfully!", 'success')
    return redirect(url_for('home', view='timesheet'))





if __name__ == "__main__":
    app.run(debug=True)

