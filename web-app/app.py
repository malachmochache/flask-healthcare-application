from flask import Flask, render_template, request, redirect, url_for, Response
from mongodb_util import init_mongo
import csv
from io import StringIO
from datetime import datetime, timezone
from math import ceil


app = Flask(__name__)

# Data connection
collection = init_mongo()

# Home page with form for data collection
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission: Store data in MongoDB
@app.route('/submit', methods=['POST'])
def submit():
    try:
        user_data = {
            "age": int(request.form['age']),
            "gender": request.form['gender'],
            "total_income": float(request.form['income']),
            "timestamp": datetime.now(timezone.utc),
            "expenses": {
                "utilities": float(request.form.get('utilities', 0)),
                "entertainment": float(request.form.get('entertainment', 0)),
                "school_fees": float(request.form.get('school_fees', 0)),
                "shopping": float(request.form.get('shopping', 0)),
                "healthcare": float(request.form.get('healthcare', 0)),
            }
        }
        # Save to MongoDB
        collection.insert_one(user_data)
        # Redirect to success page
        return redirect(url_for('success'))
    except Exception as e:
        print(f"[ERROR] Failed to insert data: {e}")
        return redirect(url_for('error'))

# Display the data collected
@app.route('/submissions')
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

        total_records = collection.count_documents(query)
        total_pages = ceil(total_records / PER_PAGE)

        records = list(
            collection.find(query, {'_id': 0})
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
        return redirect(url_for('error', message = '[ERROR] Failed to load submissions'))

# API to export user data as csv
@app.route('/api/export')
def api_download_csv():
    try:
        gender = request.args.get('gender', None)

        query = {}
        if gender:
            query['gender'] = gender

        records = list(collection.find(query, {'_id': 0}))
        if not records:
            return Response("No data available", status=404)

        # Flatten expenses
        flat_records = []
        for r in records:
            base = {
                'age': r.get('age'),
                'gender': r.get('gender'),
                'total_income': r.get('total_income'),
                'timestamp': r.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if r.get('timestamp') else '',
            }
            base.update(r.get('expenses', {}))
            flat_records.append(base)

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=flat_records[0].keys())
        writer.writeheader()
        writer.writerows(flat_records)
        output.seek(0)

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )

    except Exception as e:
        print(f"[API ERROR] Failed to generate CSV: {e}")
        return Response("Internal server error", status=500)

# Success data submission
@app.route('/success')
def success():
    return render_template('success.html')

# Error handling
@app.route('/error')
def error():
    message = request.args.get('message', None)
    return render_template('error.html', message = message)

# Optional: Handle any uncaught exceptions
@app.errorhandler(Exception)
def unhandled_exception(e):
    print(f"[UNCAUGHT EXCEPTION] {e}")
    return render_template('error.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
