from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import db, Activity, Mood, Nutrition, Habit, HabitLog
from datetime import date, timedelta, datetime
from sqlalchemy import func
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import os
from groq import Groq
import json
from datetime import date, timedelta
from flask import current_app


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

main_bp = Blueprint('main', __name__)

def generate_ai_one_liner(avg_mood, completed_habits, total_habits):
    """Generate a quick AI insight for the dashboard"""
    insights = []
    
    if total_habits > 0:
        habit_rate = (completed_habits / total_habits) * 100
        if habit_rate == 100:
            insights.append("Perfect habit day! 🎉 Keep this momentum.")
        elif habit_rate >= 75:
            insights.append("Great habit progress! You're on track.")
        elif habit_rate >= 50:
            insights.append("Good start today. Complete the remaining habits.")
        else:
            insights.append("Let's boost today's habit completion.")
    
    if avg_mood >= 8:
        insights.append("Your mood is excellent today!")
    elif avg_mood <= 4:
        insights.append("Take a moment to self-care. Your mood matters.")
    
    return insights[0] if insights else "Keep consistent — small steps add up. 💪"

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    
    # Mood data
    latest_mood = Mood.query.filter_by(user_id=current_user.id).order_by(Mood.date.desc()).first()
    
    # Water today (sum all water entries for today)
    today_nutrition_entries = Nutrition.query.filter_by(user_id=current_user.id, date=today).all()
    today_water = sum(n.water for n in today_nutrition_entries)
    
    # Water this week
    week_start = today - timedelta(days=7)
    week_nutrition = Nutrition.query.filter_by(user_id=current_user.id).filter(Nutrition.date >= week_start).all()
    week_water_total = sum(n.water for n in week_nutrition)
    
    # Habits today
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    total_habits = len(habits)
    completed_today = HabitLog.query.filter_by(user_id=current_user.id, date=today, is_completed=True).count()
    completion_rate = round((completed_today / total_habits * 100) if total_habits > 0 else 0)
    
    # Calories today
    today_activity = Activity.query.filter_by(user_id=current_user.id, date=today).all()
    today_calories_burned = sum(a.calories for a in today_activity)
    today_activity_count = len(today_activity)
    calories_today = sum(n.calories for n in today_nutrition_entries)
    
    # Weekly activity
    activities_week = Activity.query.filter_by(user_id=current_user.id).filter(Activity.date >= week_start).all()
    total_weekly_activities = len(activities_week)
    
    # Calculate activity count per day for the sparkline
    weekly_activities_by_day = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Activity.query.filter_by(user_id=current_user.id, date=day).count()
        weekly_activities_by_day.append(count)
    
    # Weekly mood
    moods_week = Mood.query.filter_by(user_id=current_user.id).filter(Mood.date >= week_start).order_by(Mood.date.asc()).all()
    weekly_mood = [m.mood_score for m in moods_week] if moods_week else [0]*7
    
    # Day labels
    day_labels = [(today - timedelta(days=6-i)).strftime('%a') for i in range(7)]
    
    # Average mood
    avg_mood = round(sum(m.mood_score for m in moods_week) / len(moods_week)) if moods_week else 0
    
    # Longest streak
    longest_streak = 0
    for habit in habits:
        streak = compute_streak(habit)
        if streak > longest_streak:
            longest_streak = streak
    
    # AI one-liner
    ai_one_liner = generate_ai_one_liner(avg_mood, completed_today, total_habits)
    
    return render_template(
        'dashboard.html',
        user=current_user,
        latest_mood=latest_mood,
        today_water=today_water,
        week_water_total=week_water_total,
        total_habits=total_habits,
        completed_today=completed_today,
        completion_rate=completion_rate,
        today_calories_burned=today_calories_burned,
        today_activity_count=today_activity_count,
        calories_today=calories_today,
        total_weekly_activities=total_weekly_activities,
        weekly_mood=weekly_mood,
        weekly_activities=weekly_activities_by_day,
        day_labels=day_labels,
        avg_mood=avg_mood,
        longest_streak=longest_streak,
        ai_one_liner=ai_one_liner
    )


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


@login_required
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
    today_water = int(today_water)

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


@login_required
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


@login_required
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


@main_bp.route("/apply_recommendation", methods=['POST'])
@login_required
def apply_recommendation():
    """Apply a recommendation and create a habit (all categories convert to habits)"""
    data = request.get_json() or {}
    title = data.get('title')
    category = data.get('category')
    description = data.get('description', '')
    
    if not title or not category:
        return jsonify({"error": "title and category required"}), 400
    
    try:
        # Create habit from ANY recommendation category
        # Map category to appropriate habit description
        if category == 'activity':
            habit_description = f"Activity: {description}"
        elif category == 'mood':
            habit_description = f"Mood practice: {description}"
        elif category == 'nutrition':
            habit_description = f"Nutrition: {description}"
        elif category == 'habits':
            habit_description = description
        else:
            return jsonify({"error": "Invalid category"}), 400
        
        # Create habit in UNCOMPLETED state
        new_habit = Habit(
            user_id=current_user.id,
            name=title,
            description=habit_description,
            frequency='daily',
            target_count=1
        )
        db.session.add(new_habit)
        db.session.commit()
        
        # DO NOT create a log entry - leave it uncompleted
        # User must manually mark it complete in habits page
        
        return jsonify({
            "success": True,
            "message": f"Habit '{title}' created! Mark it complete when done.",
            "type": "habit",
            "habit_id": new_habit.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/delete_activity/<int:activity_id>", methods=['DELETE'])
@login_required
def delete_activity(activity_id):
    """Delete an activity by ID"""
    try:
        activity = Activity.query.filter_by(id=activity_id, user_id=current_user.id).first()
        if not activity:
            return jsonify({"error": "Activity not found"}), 404
        
        db.session.delete(activity)
        db.session.commit()
        return jsonify({"success": True, "message": "Activity deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/delete_mood/<int:mood_id>", methods=['DELETE'])
@login_required
def delete_mood(mood_id):
    """Delete a mood entry by ID"""
    try:
        mood = Mood.query.filter_by(id=mood_id, user_id=current_user.id).first()
        if not mood:
            return jsonify({"error": "Mood entry not found"}), 404
        
        db.session.delete(mood)
        db.session.commit()
        return jsonify({"success": True, "message": "Mood entry deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/delete_nutrition/<int:meal_id>", methods=['DELETE'])
@login_required
def delete_nutrition(meal_id):
    """Delete a nutrition entry by ID"""
    try:
        nutrition = Nutrition.query.filter_by(id=meal_id, user_id=current_user.id).first()
        if not nutrition:
            return jsonify({"error": "Nutrition entry not found"}), 404
        
        db.session.delete(nutrition)
        db.session.commit()
        return jsonify({"success": True, "message": "Nutrition entry deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/delete_habit/<int:habit_id>", methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    """Delete a habit and all its logs by ID"""
    try:
        habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()
        if not habit:
            return jsonify({"error": "Habit not found"}), 404
        
        # Delete all habit logs first
        HabitLog.query.filter_by(habit_id=habit_id).delete()
        # Then delete the habit
        db.session.delete(habit)
        db.session.commit()
        return jsonify({"success": True, "message": "Habit deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/recommendation")
@login_required
def recommendation():
    today = date.today()

    # Build weekly data ------------------------------------
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    weekly_activities = [
        Activity.query.filter_by(user_id=current_user.id, date=d).count()
        for d in days
    ]

    weekly_mood = [
        (Mood.query.filter_by(user_id=current_user.id, date=d).first().mood_score
         if Mood.query.filter_by(user_id=current_user.id, date=d).first() else 0)
        for d in days
    ]

    weekly_calories = []
    for d in days:
        acts = Activity.query.filter_by(user_id=current_user.id, date=d).all()
        weekly_calories.append(int(sum(a.calories for a in acts)))

    today_water = db.session.query(db.func.sum(Nutrition.water)).filter(
        Nutrition.user_id == current_user.id, Nutrition.date == today
    ).scalar() or 0
    today_water = int(today_water)

    total_habits = Habit.query.filter_by(user_id=current_user.id).count()
    completed_today = HabitLog.query.filter_by(
        user_id=current_user.id, date=today, is_completed=True
    ).count()
    habit_success = int((completed_today/total_habits)*100) if total_habits else 0

    weekly_data = {
        "activities": weekly_activities,
        "mood": weekly_mood,
        "calories": weekly_calories, 
        "water_today": today_water,
        "habit_success": habit_success
    }

    # CALL AI (Groq)
    ai_recs = generate_ai_recommendations(weekly_data)

    return render_template(
        "recommendation.html",
        recs=ai_recs
    )


@login_required
def generate_ai_recommendations(weekly_data):
    prompt = f"""
    You are a wellness AI coach. Based on the user's weekly data below, 
    generate personalized and actionable recommendations.

    IMPORTANT: Generate EXACTLY 3 recommendations for EACH category with one High, one Medium, and one Low priority item.

    The output MUST be ONLY valid JSON in this exact structure:

    {{
        "activity": [
            {{
                "title": "Recommendation 1",
                "description": "Description for recommendation 1",
                "priority": "High",
                "meta": ["detail1", "detail2"],
                "icon": "fa-running"
            }},
            {{
                "title": "Recommendation 2",
                "description": "Description for recommendation 2",
                "priority": "Medium",
                "meta": ["detail1", "detail2"],
                "icon": "fa-dumbbell"
            }},
            {{
                "title": "Recommendation 3",
                "description": "Description for recommendation 3",
                "priority": "Low",
                "meta": ["detail1", "detail2"],
                "icon": "fa-hiking"
            }}
        ],
        "mood": [
            {{
                "title": "Recommendation 1",
                "description": "Description for recommendation 1",
                "priority": "High",
                "meta": ["detail1", "detail2"],
                "icon": "fa-smile"
            }},
            {{
                "title": "Recommendation 2",
                "description": "Description for recommendation 2",
                "priority": "Medium",
                "meta": ["detail1", "detail2"],
                "icon": "fa-heart"
            }},
            {{
                "title": "Recommendation 3",
                "description": "Description for recommendation 3",
                "priority": "Low",
                "meta": ["detail1", "detail2"],
                "icon": "fa-music"
            }}
        ],
        "nutrition": [
            {{
                "title": "Recommendation 1",
                "description": "Description for recommendation 1",
                "priority": "High",
                "meta": ["detail1", "detail2"],
                "icon": "fa-apple-alt"
            }},
            {{
                "title": "Recommendation 2",
                "description": "Description for recommendation 2",
                "priority": "Medium",
                "meta": ["detail1", "detail2"],
                "icon": "fa-water"
            }},
            {{
                "title": "Recommendation 3",
                "description": "Description for recommendation 3",
                "priority": "Low",
                "meta": ["detail1", "detail2"],
                "icon": "fa-carrot"
            }}
        ],
        "habits": [
            {{
                "title": "Recommendation 1",
                "description": "Description for recommendation 1",
                "priority": "High",
                "meta": ["detail1", "detail2"],
                "icon": "fa-check-circle"
            }},
            {{
                "title": "Recommendation 2",
                "description": "Description for recommendation 2",
                "priority": "Medium",
                "meta": ["detail1", "detail2"],
                "icon": "fa-bullseye"
            }},
            {{
                "title": "Recommendation 3",
                "description": "Description for recommendation 3",
                "priority": "Low",
                "meta": ["detail1", "detail2"],
                "icon": "fa-calendar"
            }}
        ]
    }}

    Return ONLY valid JSON. No extra text before or after.

    USER WEEKLY DATA:
    {json.dumps(weekly_data, indent=2)}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
        result["activity"] = (result.get("activity") or [])[:3]
        result["mood"] = (result.get("mood") or [])[:3]
        result["nutrition"] = (result.get("nutrition") or [])[:3]
        result["habits"] = (result.get("habits") or [])[:3]
        return result
    except:
        return {"error": "Invalid JSON returned by AI", "raw": content}
