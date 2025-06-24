from flask import Blueprint, render_template, request, redirect, url_for, current_app
from datetime import datetime, timezone
from math import ceil

main = Blueprint("main", __name__)

# Home page with form for data collection
@main.route('/')
def index():
    return render_template('index.html')

# Handle form submission: Store data in MongoDB
@main.route('/submit', methods=['POST'])
def submit():
    try:
        age = int(request.form['age'])
        income = float(request.form['income'])
        gender = request.form['gender']

        expenses = {key: float(request.form.get(key, 0)) for key in
                    ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']}

        user_data = {
            "age": age,
            "gender": gender,
            "total_income": income,
            "timestamp": datetime.now(timezone.utc),
            "expenses": expenses
        }
        # Save to MongoDB
        current_app.collection.insert_one(user_data)
        # Redirect to success page
        return redirect(url_for('main.success'))

    except (ValueError, TypeError) as e:
        return redirect(url_for('main.error', message="Invalid input format."))

    except Exception as e:
        print(f"[ERROR] Failed to insert data: {e}")
        return redirect(url_for('main.error', message='Failed to insert data into database.'))

    
# Display the data collected
@main.route('/submissions')
def submissions():
    try:
        PER_PAGE = 10
        page = int(request.args.get('page', 1))
        gender_filter = request.args.get('gender', None)

        if page < 1:
            page = 1

        query = {}
        if gender_filter:
            query['gender'] = gender_filter

        total_records = current_app.collection.count_documents(query)
        total_pages = ceil(total_records / PER_PAGE)

        records = list(
            current_app.collection.find(query, {'_id': 0})
            .sort('timestamp', -1)
            .skip((page - 1) * PER_PAGE)
            .limit(PER_PAGE)
        )

        return render_template('submissions.html',
                               records=records,
                               page=page,
                               total_pages=total_pages,
                               gender_filter=gender_filter)
    except Exception as e:
        print(f"[ERROR] Failed to load submissions: {e}")
        return redirect(url_for('main.error', message = '[ERROR] Failed to load submissions'))

# Success data submission
@main.route('/success')
def success():
    return render_template('success.html')

# Error handling
@main.route('/error')
def error():
    message = request.args.get('message', None)
    return render_template('error.html', message = message)

# Optional: Handle any uncaught exceptions
@main.errorhandler(Exception)
def unhandled_exception(e):
    print(f"[UNCAUGHT EXCEPTION] {e}")
    return render_template('error.html'), 500