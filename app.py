from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Chore, Claim  # Import db and models from models.py
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Home page
@app.route('/')
def index():
    return render_template('index.html', chores=fetch_chores())

# This week page
@app.route('/week')
def week(message=None):    
    # Fetch all claims created in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_claims = Claim.query.filter(Claim.completed_at >= seven_days_ago).all()
    
    chores = fetch_chores()
    chore_dict = {chore.id: chore.name for chore in chores}

    tally = defaultdict(int)
    for claim in recent_claims:
        tally[claim.completed_by] += claim.value

    return render_template(
        'week.html', 
        chores=chores, 
        chore_dict=chore_dict,
        claims=recent_claims, 
        message=message,
        tally=tally, 
        winner=max(tally, key=tally.get)
    )

# Chore config page
@app.route('/chores')
def chores():
    return render_template('chores.html', chores=fetch_chores())

# New claim api
@app.route('/claim/create', methods=['POST'])
def create_claim():
    # Get data from form submission
    chore_id = request.form['chore_id']
    completed_by = request.form['completed_by']
    chore = Chore.query.get(chore_id)

    # Create a new claim
    new_claim = Claim(
        chore_id=chore_id,
        value=chore.value,
        created_by="",
        completed_at=datetime.utcnow(),
        completed_by=completed_by,
        note=""
    )
    db.session.add(new_claim)
    db.session.commit()

    # Redirect to the edit page after creation
    return redirect(url_for('edit_claim', id=new_claim.id, message="Claim created successfully"))

# Edit claim page and api
@app.route('/claim/edit/<int:id>', methods=['GET', 'POST', 'DELETE'])
def edit_claim(id, message=None):
    claim = Claim.query.get(id)
    if not claim:
        message = "claim not found"

    if request.method == 'POST':
        alert_message = None
        if request.form['delete'] == '1':
            db.session.delete(claim)
            alert_message = "Deletion was successful"
        else:
            claim.chore_id = request.form['chore_id']
            claim.value = request.form['value']
            claim.completed_by = request.form['completed_by']
            claim.completed_at = request.form['completed_at']
            claim.note = request.form['note']
            claim.updated_at = datetime.utcnow()  # Update the timestamp
            alert_message = "Edit saved successfully"
        db.session.commit()
        return redirect(url_for('week', message=alert_message))

    # Fetch all chores to display in the dropdown list for chore selection
    return render_template('claim_form.html', claim=claim, chores=fetch_chores(), message=message)

# New chore page and api
@app.route('/chore/create', methods=['GET', 'POST'])
def create_chore():
    if request.method == 'POST':
        # Get data from form submission
        value = request.form['value']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        # Create a new chore
        new_chore = Chore(value=value, name=name, description=description, category=category)
        db.session.add(new_chore)
        db.session.commit()

        return redirect(url_for('chores'))  # Redirect to the chores page after creation

    return render_template('chore_form.html', chores=fetch_chores())

# Edit chore page and api
@app.route('/chore/edit/<int:id>', methods=['GET', 'POST'])
def edit_chore(id):
    chore = Chore.query.get(id)
    if not chore:
        return jsonify({"message": "Chore not found"}), 404

    if request.method == 'POST':
        # Get data from form submission
        chore.value = request.form['value']
        chore.name = request.form['name']
        chore.description = request.form['description']
        chore.category = request.form['category']

        db.session.commit()

        return redirect(url_for('chores'))  # Redirect to the chores page after editing

    return render_template('chore_form.html', chore=chore, chores=fetch_chores())

def fetch_chores():
    return Chore.query.all()

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)