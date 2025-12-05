from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import db, Activity, Mood, Nutrition, Habit, HabitLog
from datetime import date, timedelta, datetime
from sqlalchemy import func
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

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


@main_bp.route('/nutrition', methods=['GET', 'POST'])
@login_required
def nutrition():
    if request.method == 'POST':
        meal_type = request.form.get('meal_type')
        food_items = request.form.get('food_items')

        calories = int(request.form.get('calories'))
        protein = int(request.form.get('protein'))
        carbs = int(request.form.get('carbs'))
        fat = int(request.form.get('fat'))
        water = int(request.form.get('water'))

        date = datetime.strptime(request.form.get('date'), "%Y-%m-%d")
        notes = request.form.get('notes')

        new_meal = Nutrition(
            user_id=current_user.id,
            meal_type=meal_type,
            food_items=food_items,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            water=water,
            date=date,
            notes=notes
        )

        db.session.add(new_meal)
        db.session.commit()
        flash("Meal logged successfully!", "success")
        return redirect(url_for('main.nutrition'))

    meals = Nutrition.query.filter_by(user_id=current_user.id).order_by(Nutrition.date.desc()).all()
    return render_template('nutrition.html', meals=meals)


def compute_streak(habit, max_days=365):
    """
    Return consecutive days count for which habit was completed.
    Counts from the most recent completed day backwards.
    """
    streak = 0
    today = date.today()
    
    # Find the most recent day with a completed log
    most_recent_completed = None
    for i in range(max_days):
        check_day = today - timedelta(days=i)
        log = HabitLog.query.filter_by(habit_id=habit.id, user_id=habit.user_id, date=check_day).first()
        if log and log.is_completed:
            most_recent_completed = check_day
            break
    
    # If no completed day found, streak is 0
    if not most_recent_completed:
        return 0
    
    # Count consecutive days backwards from most recent completed day
    for i in range(max_days):
        check_day = most_recent_completed - timedelta(days=i)
        log = HabitLog.query.filter_by(habit_id=habit.id, user_id=habit.user_id, date=check_day).first()
        if log and log.is_completed:
            streak += 1
        else:
            break
    
    return streak

@main_bp.route('/habits')
@login_required
def habits():
    # all habits for the user
    habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.created_at.desc()).all()

    # get or create today's log for each habit (but don't commit here, just read)
    today = date.today()
    todays_logs = {}
    completed_today = 0
    total_habits = len(habits)

    for h in habits:
        log = HabitLog.query.filter_by(habit_id=h.id, user_id=current_user.id, date=today).first()
        if not log:
            # No log yet — treat as uncompleted (we won't auto-create DB row here)
            todays_logs[h.id] = None
        else:
            todays_logs[h.id] = log
            if log.is_completed:
                completed_today += 1

    # compute stats
    completion_rate = int((completed_today / total_habits) * 100) if total_habits > 0 else 0

    # compute streaks per habit and optionally overall average streak
    streaks = {h.id: compute_streak(h) for h in habits}

    return render_template(
        'habits.html',
        habits=habits,
        todays_logs=todays_logs,
        completed_today=completed_today,
        total_habits=total_habits,
        completion_rate=completion_rate,
        streaks=streaks
    )

@main_bp.route('/add_habit', methods=['POST'])
@login_required
def add_habit():
    name = request.form.get('name')
    description = request.form.get('description')
    frequency = request.form.get('frequency') or 'daily'
    target_count = int(request.form.get('target_count') or 1)

    if not name:
        flash('Habit name is required', 'danger')
        return redirect(url_for('main.habits'))

    habit = Habit(
        user_id=current_user.id,
        name=name.strip(),
        description=description.strip() if description else None,
        frequency=frequency,
        target_count=target_count
    )
    db.session.add(habit)
    db.session.commit()
    flash('Habit created', 'success')
    return redirect(url_for('main.habits'))


@main_bp.route('/toggle_habit', methods=['POST'])
@login_required
def toggle_habit():
    """
    Expects JSON: { "habit_id": <id> }
    Toggles today's is_completed for current user/habit.
    Returns JSON with new state and updated stats.
    """
    data = request.get_json() or {}
    habit_id = data.get('habit_id')
    if not habit_id:
        return jsonify({"error": "habit_id required"}), 400

    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()
    if not habit:
        return jsonify({"error": "habit not found"}), 404

    today = date.today()
    log = HabitLog.query.filter_by(habit_id=habit.id, user_id=current_user.id, date=today).first()

    if not log:
        # create log with completed
        log = HabitLog(habit_id=habit.id, user_id=current_user.id, date=today, completed_count=1, is_completed=True)
        db.session.add(log)
    else:
        # toggle
        if log.is_completed:
            log.is_completed = False
            # decrement completed_count (but not below 0)
            log.completed_count = max(0, log.completed_count - 1)
        else:
            log.is_completed = True
            log.completed_count = log.completed_count + 1

    db.session.commit()

    # recompute today's totals for user
    total_habits = Habit.query.filter_by(user_id=current_user.id).count()
    completed_today = HabitLog.query.filter_by(user_id=current_user.id, date=today, is_completed=True).count()
    completion_rate = int((completed_today / total_habits) * 100) if total_habits > 0 else 0

    # compute streak for this habit
    current_streak = compute_streak(habit)

    return jsonify({
        "habit_id": habit.id,
        "is_completed": log.is_completed,
        "completed_today": completed_today,
        "total_habits": total_habits,
        "completion_rate": completion_rate,
        "streak": current_streak
    })


@main_bp.route("/analytics")
@login_required
def analytics():
    today = date.today()

    # last 7 days
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    day_labels = [d.strftime("%a") for d in days]

    # Weekly Activities Count
    weekly_activities = [
        Activity.query.filter_by(user_id=current_user.id, date=d).count()
        for d in days
    ]
    total_weekly_activities = sum(weekly_activities)

    # Weekly Calories
    weekly_calories = []
    for d in days:
        acts = Activity.query.filter_by(user_id=current_user.id, date=d).all()
        weekly_calories.append(sum(a.calories for a in acts))
    total_calories_burned = sum(weekly_calories)

    # Weekly Mood
    weekly_mood = []
    for d in days:
        m = Mood.query.filter_by(user_id=current_user.id, date=d).first()
        weekly_mood.append(m.mood_score if m else 0)
    mood_values = [m for m in weekly_mood if m > 0]
    avg_mood = round(sum(mood_values)/len(mood_values), 1) if mood_values else 0

    # Habit Stats
    total_habits = Habit.query.filter_by(user_id=current_user.id).count()
    completed_today = HabitLog.query.filter_by(
        user_id=current_user.id, date=today, is_completed=True
    ).count()
    habit_success = int((completed_today/total_habits)*100) if total_habits else 0

    # Longest streak
    all_habits = Habit.query.filter_by(user_id=current_user.id).all()
    streaks = []
    for h in all_habits:
        streaks.append(compute_streak(h))
    longest_streak = max(streaks) if streaks else 0

    # Water Intake Today
    today_water = db.session.query(db.func.sum(Nutrition.water)).filter(
        Nutrition.user_id == current_user.id,
        Nutrition.date == today
    ).scalar() or 0

    # 1. MOOD DISTRIBUTION PIE CHART (last 7 days mood types)
    mood_records = Mood.query.filter(
        Mood.user_id == current_user.id,
        Mood.date >= (today - timedelta(days=6))
    ).all()
    mood_dist = {}
    for m in mood_records:
        mood_dist[m.mood_type] = mood_dist.get(m.mood_type, 0) + 1
    mood_labels = list(mood_dist.keys()) if mood_dist else ["No Data"]
    mood_counts = list(mood_dist.values()) if mood_dist else [0]

    # 2. MACRO BREAKDOWN PIE CHART (last 7 days macros)
    nutrition_records = Nutrition.query.filter(
        Nutrition.user_id == current_user.id,
        Nutrition.date >= (today - timedelta(days=6))
    ).all()
    total_protein = sum(n.protein for n in nutrition_records)
    total_carbs = sum(n.carbs for n in nutrition_records)
    total_fat = sum(n.fat for n in nutrition_records)
    macro_labels = ["Protein", "Carbs", "Fat"]
    macro_values = [total_protein, total_carbs, total_fat]

    # 3. CALORIES IN VS CALORIES OUT (last 7 days)
    calories_in = []
    calories_out = []
    for d in days:
        # Calories in (from nutrition)
        intake = db.session.query(db.func.sum(Nutrition.calories)).filter(
            Nutrition.user_id == current_user.id,
            Nutrition.date == d
        ).scalar() or 0
        calories_in.append(int(intake))
        
        # Calories out (from activities)
        burned = db.session.query(db.func.sum(Activity.calories)).filter(
            Activity.user_id == current_user.id,
            Activity.date == d
        ).scalar() or 0
        calories_out.append(int(burned))

    # 4. HABIT COMPLETION TREND (last 7 days)
    habit_completion_trend = []
    for d in days:
        total = Habit.query.filter_by(user_id=current_user.id).count()
        completed = HabitLog.query.filter_by(
            user_id=current_user.id, date=d, is_completed=True
        ).count()
        rate = int((completed / total) * 100) if total > 0 else 0
        habit_completion_trend.append(rate)

    # 5. SCATTER: MOOD VS ACTIVITY (last 7 days)
    scatter_data = []
    for d in days:
        activities = Activity.query.filter_by(user_id=current_user.id, date=d).count()
        mood = Mood.query.filter_by(user_id=current_user.id, date=d).first()
        mood_score = mood.mood_score if mood else 0
        if mood_score > 0:  # Only include if mood was logged
            scatter_data.append({"x": activities, "y": mood_score})

    # AI Analysis
    ml_results = analyze_wellness(weekly_activities, weekly_mood, weekly_calories)

    return render_template(
        "analytics.html",

        # charts
        weekly_activities=weekly_activities,
        weekly_calories=weekly_calories,
        weekly_mood=weekly_mood,
        day_labels=day_labels,

        # New charts data
        mood_labels=mood_labels,
        mood_counts=mood_counts,
        macro_labels=macro_labels,
        macro_values=macro_values,
        calories_in=calories_in,
        calories_out=calories_out,
        habit_completion_trend=habit_completion_trend,
        scatter_data=scatter_data,

        # stats
        total_weekly_activities=total_weekly_activities,
        total_calories_burned=total_calories_burned,
        avg_mood=avg_mood,
        habit_success=habit_success,
        completed_today=completed_today,
        today_water=today_water,
        longest_streak=longest_streak,

        # AI
        ai_insight=ml_results["insight"],
        activity_corr=ml_results["activity_mood_corr"],
        calorie_corr=ml_results["calorie_mood_corr"],
        predicted_mood=ml_results["prediction"]
    )


def analyze_wellness(activity_list, mood_list, calories_list):
    # Convert to numpy arrays
    X = np.array([activity_list, calories_list]).T
    y = np.array(mood_list)

    # Remove missing values
    valid = y > 0
    X, y = X[valid], y[valid]

    if len(y) < 3:
        return {
            "insight": "Not enough data for AI analysis.",
            "activity_mood_corr": 0,
            "calorie_mood_corr": 0,
            "prediction": 0
        }

    # 1. Correlation
    activity_corr = np.corrcoef(activity_list, mood_list)[0][1]
    calorie_corr = np.corrcoef(calories_list, mood_list)[0][1]

    # 2. Regression model
    model = LinearRegression()
    model.fit(X, y)
    predicted_mood = model.predict([[2, 200]])[0]

    return {
        "activity_mood_corr": round(activity_corr, 2),
        "calorie_mood_corr": round(calorie_corr, 2),
        "prediction": round(predicted_mood, 1),
        "insight": generate_ai_text(activity_corr, calorie_corr)
    }


def generate_ai_text(activity_corr, calorie_corr):
    insight = ""

    if activity_corr > 0.6:
        insight += "Your mood strongly improves on active days. Try adding short activities on low-energy days. "
    elif activity_corr < -0.3:
        insight += "High activity seems to reduce your mood. Try balancing intense days with rest. "

    if calorie_corr > 0.5:
        insight += "Burning more calories correlates with better mood. Keep it up! "
    elif calorie_corr < -0.3:
        insight += "High calorie days lower your mood—avoid overexertion. "

    if insight == "":
        insight = "Your lifestyle trends look balanced. Keep maintaining consistency."

    # AI Recommendation
    recommendation = ""
    if activity_corr > 0.5 and calorie_corr > 0.5:
        recommendation = "Aim for 20–30 minutes of moderate activity daily."
    elif activity_corr < 0:
        recommendation = "Your body may be stressed. Try light stretching or meditation."
    elif calorie_corr < 0:
        recommendation = "Ensure proper nutrition and hydration on workout days."
    else:
        recommendation = "Maintain your routine; consistency is improving your wellness."

    return insight + " Recommendation: " + recommendation




@main_bp.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')