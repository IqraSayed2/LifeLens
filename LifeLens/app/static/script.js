// ==================================== BASE PAGE =====================================================

function toggleMobileSidebar() {
  const sidebar = document.querySelector(".navbar-sidebar");
  sidebar.classList.toggle("show");
}

// Close sidebar when clicking outside on mobile
document.addEventListener("click", function (event) {
  const sidebar = document.querySelector(".navbar-sidebar");
  const menuBtn = document.querySelector(".navbar-mobile-menu-btn");
  if (window.innerWidth <= 768 && sidebar.classList.contains("show")) {
    if (!sidebar.contains(event.target) && !menuBtn.contains(event.target)) {
      sidebar.classList.remove("show");
    }
  }
});

// ==================================== ACTIVITY PAGE ================================================

function openActivityModal() {
  const modal = document.getElementById("activityModal");
  modal.classList.add("show");
  document.body.style.overflow = "hidden";
}
function closeActivityModal() {
  const modal = document.getElementById("activityModal");
  modal.classList.remove("show");
  document.body.style.overflow = "auto";
}
function closeModalOnOverlay(event) {
  if (event.target === event.currentTarget) {
    closeActivityModal();
  }
}

// ======================================= MOOD ===========================================

function openMoodModal() {
  document.getElementById("moodModal").classList.add("show");
}
function closeMoodModal() {
  document.getElementById("moodModal").classList.remove("show");
}
function closeModalOnOverlay(event) {
  if (event.target === event.currentTarget) {
    closeMoodModal();
  }
}
function selectMood(btn) {
  document
    .querySelectorAll(".mood-type-btn")
    .forEach((b) => b.classList.remove("selected"));
  btn.classList.add("selected");
  document.getElementById("moodType").value = btn.dataset.mood;
}
function updateSliderValue(type, value) {
  document.getElementById(type + "Value").textContent = value + "/10";
}

// ====================================== NUTRITION ===============================================

function openNutritionModal() {
  document.getElementById("nutritionModal").classList.add("show");
}
function closeNutritionModal() {
  document.getElementById("nutritionModal").classList.remove("show");
}
function closeModalOnOverlay(e) {
  if (e.target === e.currentTarget) closeNutritionModal();
}

// ====================================== HABITS ===============================================

function openHabitsModal() {
  document.getElementById("habitsModal").classList.add("show");
  document.body.style.overflow = "hidden";
}
function closeHabitsModal() {
  document.getElementById("habitsModal").classList.remove("show");
  document.body.style.overflow = "auto";
}
function closeModalOnOverlay(event) {
  if (event.target === event.currentTarget) closeHabitsModal();
}

// Toggle habit completion via AJAX
async function toggleHabit(event, habitId) {
  // prevent the parent .habitstrack-habit-item onclick when clicking checkbox
  event.stopPropagation();

  try {
    // static files aren't processed by Jinja, so use the endpoint path directly
    const resp = await fetch("/toggle_habit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ habit_id: habitId }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      alert(data.error || "Failed to toggle habit");
      return;
    }

    // Update the item UI
    const item = document.querySelector('[data-habit-id="' + habitId + '"]');
    const checkboxIcon = item.querySelector(".habitstrack-checkbox i");

    if (data.is_completed) {
      item.classList.remove("uncompleted");
      item.classList.add("completed");
      checkboxIcon.style.display = "block";
    } else {
      item.classList.remove("completed");
      item.classList.add("uncompleted");
      checkboxIcon.style.display = "none";
    }

    // Update stats on page
    document.getElementById("completedToday").textContent =
      data.completed_today;
    document.getElementById("totalHabits").textContent = data.total_habits;
    document.getElementById("completionRate").textContent =
      data.completion_rate + "%";

    // Update streak display inside the item (use class selector for reliability)
    const streakSpan = item.querySelector(".habit-streak-display");
    if (streakSpan) {
      streakSpan.textContent = "Streak: " + data.streak + "d";
    }

    // Update max streak card by finding all streak displays and getting the max
    const allStreakSpans = document.querySelectorAll(".habit-streak-display");
    let maxStreak = 0;
    allStreakSpans.forEach((span) => {
      const streakText = span.textContent;
      const match = streakText.match(/Streak: (\d+)d/);
      if (match) {
        maxStreak = Math.max(maxStreak, parseInt(match[1]));
      }
    });
    const maxStreakDisplay = document.getElementById("maxStreakDisplay");
    if (maxStreakDisplay) {
      maxStreakDisplay.textContent = maxStreak + " days";
    }
  } catch (err) {
    console.error(err);
    alert("Network error toggling habit");
  }
}

// ============================== ANALYTICS ====================================================
