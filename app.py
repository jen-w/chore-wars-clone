from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Chore, Claim  # Import db and models from models.py
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/week')
def week():
    # Get today's date and calculate the date 7 days ago
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Fetch all claims created in the last 7 days
    recent_claims = Claim.query.filter(Claim.created_at >= seven_days_ago).all()

    return render_template('week.html', claims=recent_claims)

@app.route('/chores')
def chores():
    # Fetch all chores
    all_chores = Chore.query.all()
    return render_template('chores.html', chores=all_chores)

# Create New Claim Route
@app.route('/claim/create', methods=['GET', 'POST'])
def create_claim():
    if request.method == 'POST':
        # Get data from form submission
        chore_id = request.form['chore_id']
        value = request.form['value']
        created_by = request.form['created_by']
        completed_by = request.form['completed_by']
        note = request.form['note']

        # Create a new claim
        new_claim = Claim(
            chore_id=chore_id,
            value=value,
            created_by=created_by,
            completed_by=completed_by,
            note=note
        )
        db.session.add(new_claim)
        db.session.commit()

        return redirect(url_for('week'))  # Redirect to the week page after creation

    # Fetch all chores to display in the dropdown list for chore selection
    chores = Chore.query.all()
    return render_template('claim_form.html', chores=chores)

# Edit Claim Route
@app.route('/claim/edit/<int:id>', methods=['GET', 'POST'])
def edit_claim(id):
    claim = Claim.query.get(id)
    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    if request.method == 'POST':
        # Get data from form submission
        claim.chore_id = request.form['chore_id']
        claim.value = request.form['value']
        claim.completed_by = request.form['completed_by']
        claim.completed_at = request.form['completed_at']
        claim.note = request.form['note']
        claim.updated_at = datetime.utcnow()  # Update the timestamp

        db.session.commit()

        return redirect(url_for('week'))  # Redirect to the week page after editing

    # Fetch all chores to display in the dropdown list for chore selection
    chores = Chore.query.all()
    return render_template('claim_form.html', claim=claim, chores=chores)

# Create New Chore Route
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

    return render_template('chore_form.html')

# Edit Chore Route
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

    return render_template('chore_form.html', chore=chore)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)