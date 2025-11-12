from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, Activity, Mood
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/activity')
def activity():
    # Fetch all activities for logged-in user
    user_activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.date.desc()).all()
    return render_template('activity.html', user=current_user, activities=user_activities)


@main_bp.route('/add_activity', methods=['POST'])
@login_required
def add_activity():
    title = request.form.get('title')
    category = request.form.get('category')
    duration = request.form.get('duration')
    calories = request.form.get('calories')
    intensity = request.form.get('intensity')
    date = request.form.get('date')
    notes = request.form.get('notes')

    new_activity = Activity(
        user_id=current_user.id,
        title=title,
        category=category,
        duration=int(duration),
        calories=int(calories),
        intensity=intensity,
        notes=notes,
        date=datetime.strptime(date, '%Y-%m-%d')
    )
    db.session.add(new_activity)
    db.session.commit()
    flash('Activity added successfully!', 'success')
    return redirect(url_for('main.activity'))


@main_bp.route('/habits')
def habits():
    return render_template('habits.html')


@main_bp.route('/mood', methods=['GET', 'POST'])
@login_required
def mood():
    if request.method == 'POST':
        mood_type = request.form.get('mood_type')
        mood_score = int(request.form.get('mood_score'))
        energy_score = int(request.form.get('energy_score'))
        stress_score = int(request.form.get('stress_score'))
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        notes = request.form.get('notes')

        new_mood = Mood(
            user_id=current_user.id,
            mood_type=mood_type,
            mood_score=mood_score,
            energy_score=energy_score,
            stress_score=stress_score,
            date=date,
            notes=notes
        )

        db.session.add(new_mood)
        db.session.commit()
        flash('Mood logged successfully!', 'success')
        return redirect(url_for('main.mood'))

    # Show all moods for current user
    moods = Mood.query.filter_by(user_id=current_user.id).order_by(Mood.date.desc()).all()
    return render_template('mood.html', moods=moods)


@main_bp.route('/nutrition')
def nutrition():
    return render_template('nutrition.html')


@main_bp.route('/analytics')
def analytics():
    return render_template('analytics.html')


@main_bp.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')