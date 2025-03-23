from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Chore, Claim
from datetime import datetime, timedelta
from pytz import timezone
from collections import defaultdict

pacific_timezone = timezone('America/Los_Angeles')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'  # TODO: replace

db.init_app(app)

# Home page
@app.route('/')
def index():
    # Fetch all claims created in the last 7 days
    seven_days_ago = datetime.now(pacific_timezone).date() - timedelta(days=7)
    recent_claims = (
        Claim.query
        .filter(Claim.completed_at > seven_days_ago)
        .order_by(Claim.completed_at.desc())
        .all()
    )

    chores = fetch_chores()
    chore_dict = {chore.id: chore.name for chore in chores}

    tally = defaultdict(int)
    for claim in recent_claims:
        tally[claim.completed_by] += claim.value
    max_value = max(tally.values(), default=None)
    max_keys = [key for key, value in tally.items() if value == max_value]

    return render_template(
        'index.html', 
        chores=chores, 
        chore_dict=chore_dict,
        claims=recent_claims, 
        tally=tally, 
        winner=max_keys[0] if len(max_keys) == 1 else 'no one'
    )

# Chore config page
@app.route('/chores')
def chores():
    return render_template('chores.html')

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
        completed_at=datetime.now(pacific_timezone),
        completed_by=completed_by,
        note=""
    )
    db.session.add(new_claim)
    db.session.commit()

    # Redirect to the edit page after creation
    flash("good job, edit it below if you so desire", "success")
    return redirect(url_for('edit_claim', id=new_claim.id))

# Edit claim page and api
@app.route('/claim/edit/<int:id>', methods=['GET', 'POST'])
def edit_claim(id):
    claim = Claim.query.get(id)
    if not claim:
        flash("claim not found", "error")
        return redirect(request.referrer or url_for('index'))

    if request.method == 'POST':
        if request.form.get('delete') == '1':
            db.session.delete(claim)
            flash("deletion was successful", "info")
        else:
            claim.chore_id = request.form['chore_id']
            claim.value = request.form['value']
            claim.completed_by = request.form['completed_by']
            claim.completed_at = datetime.strptime(
                request.form['completed_at'], "%Y-%m-%dT%H:%M"
            )
            claim.note = request.form['note']
            claim.updated_at = datetime.now(pacific_timezone)
            flash("edit saved successfully", "info")

        db.session.commit()
        return redirect(url_for('index'))

    return render_template(
        'edit_claim.html', 
        claim=claim, 
        chores=fetch_chores(),
        completed_at_min=(
            datetime.now(pacific_timezone) - timedelta(days=6)
        ).strftime('%Y-%m-%d'),
        completed_at_max=datetime.now(pacific_timezone).strftime('%Y-%m-%d')
    )

# New chore page and api
@app.route('/chore/create', methods=['GET', 'POST'])
def create_chore():
    if request.method == 'POST':
        value = request.form['value']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        new_chore = Chore(value=value, name=name, description=description, category=category)
        db.session.add(new_chore)
        db.session.commit()

        flash("chore created successfully", "info")
        return redirect(url_for('chores'))

    return render_template('edit_chore.html')

# Edit chore page and api
@app.route('/chore/edit/<int:id>', methods=['GET', 'POST'])
def edit_chore(id):
    chore = Chore.query.get(id)
    if not chore:
        flash("fake chore detected, chore not found 404", "error")
        return redirect(url_for(create_chore))
    elif request.method == 'POST':
        if request.form.get('delete') == '1':
            if Claim.query.filter(Claim.chore_id == id).first() is not None:
                flash("sorry can't delete this without deleting historic claims", "error")
                return redirect(url_for('chores'))
            db.session.delete(chore)
            flash("deletion was successful", "info")
        else:
            chore.value = request.form['value']
            chore.name = request.form['name']
            chore.description = request.form['description']
            chore.category = request.form['category']
            flash("edit saved successfully", "info")

        db.session.commit()
        return redirect(url_for('chores'))

    return render_template('edit_chore.html', chore=chore)

@app.context_processor
def populate_common_template_data():
    return {
        'chores': fetch_chores(),
        'users': ['jenny', 'zep']
    }

def fetch_chores():
    return Chore.query.order_by(Chore.name).all()

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)