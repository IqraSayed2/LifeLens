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

function deleteActivity(activityId) {
  if (
    confirm(
      "Are you sure you want to delete this activity? This action cannot be undone."
    )
  ) {
    fetch(`/delete_activity/${activityId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (response.ok) {
          const cards = document.querySelectorAll(".activity-card");
          for (let card of cards) {
            const deleteBtn = card.querySelector(".activity-delete-btn");
            if (
              deleteBtn &&
              deleteBtn.getAttribute("onclick").includes(activityId)
            ) {
              card.style.animation = "fadeOut 0.3s ease";
              setTimeout(() => card.remove(), 300);
              break;
            }
          }
          showNotification("Activity deleted successfully", "success");
        } else {
          showNotification("Failed to delete activity", "error");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showNotification("Error deleting activity", "error");
      });
  }
}

function showNotification(message, type = "success") {
  const notification = document.createElement("div");
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        background: ${type === "success" ? "#10b981" : "#ef4444"};
        color: white;
    `;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
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

function deleteMood(moodId) {
  if (confirm("Are you sure? This action cannot be undone.")) {
    fetch(`/delete_mood/${moodId}`, { method: "DELETE" })
      .then((response) => {
        if (response.ok) {
          const cards = document.querySelectorAll(".mood-card");
          for (let card of cards) {
            const deleteBtn = card.querySelector(".mood-delete-btn");
            if (
              deleteBtn &&
              deleteBtn.getAttribute("onclick").includes(moodId)
            ) {
              card.style.animation = "fadeOut 0.3s ease";
              setTimeout(() => card.remove(), 300);
              break;
            }
          }
          showNotification("Mood entry deleted successfully", "success");
        } else {
          showNotification("Failed to delete mood entry", "error");
        }
      })
      .catch((error) => showNotification("Error deleting mood entry", "error"));
  }
}

function showNotification(message, type) {
  const notification = document.createElement("div");
  notification.className = "notification";
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.padding = "12px 20px";
  notification.style.borderRadius = "6px";
  notification.style.color = "white";
  notification.style.fontSize = "14px";
  notification.style.zIndex = "9999";
  notification.style.animation = "slideIn 0.3s ease";
  notification.style.backgroundColor =
    type === "success" ? "#10b981" : "#ef4444";
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
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

function deleteNutrition(mealId) {
  if (confirm("Are you sure? This action cannot be undone.")) {
    fetch(`/delete_nutrition/${mealId}`, { method: "DELETE" })
      .then((response) => {
        if (response.ok) {
          const cards = document.querySelectorAll(".nutrition-card");
          for (let card of cards) {
            const deleteBtn = card.querySelector(".nutrition-delete-btn");
            if (
              deleteBtn &&
              deleteBtn.getAttribute("onclick").includes(mealId)
            ) {
              card.style.animation = "fadeOut 0.3s ease";
              setTimeout(() => card.remove(), 300);
              break;
            }
          }
          showNotification("Nutrition entry deleted successfully", "success");
        } else {
          showNotification("Failed to delete nutrition entry", "error");
        }
      })
      .catch((error) =>
        showNotification("Error deleting nutrition entry", "error")
      );
  }
}

function showNotification(message, type) {
  const notification = document.createElement("div");
  notification.className = "notification";
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.padding = "12px 20px";
  notification.style.borderRadius = "6px";
  notification.style.color = "white";
  notification.style.fontSize = "14px";
  notification.style.zIndex = "9999";
  notification.style.animation = "slideIn 0.3s ease";
  notification.style.backgroundColor =
    type === "success" ? "#10b981" : "#ef4444";
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
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

function deleteHabit(habitId) {
  if (confirm("Are you sure? This action cannot be undone.")) {
    fetch(`/delete_habit/${habitId}`, { method: "DELETE" })
      .then((response) => {
        if (response.ok) {
          const habitItem = document
            .querySelector(`[data-habit-id="${habitId}"]`)
            .closest(".habitstrack-habit-item");
          habitItem.style.animation = "fadeOut 0.3s ease";
          setTimeout(() => habitItem.remove(), 300);
          showNotification("Habit deleted successfully", "success");
        } else {
          showNotification("Failed to delete habit", "error");
        }
      })
      .catch((error) => showNotification("Error deleting habit", "error"));
  }
}

function showNotification(message, type) {
  const notification = document.createElement("div");
  notification.className = "notification";
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.padding = "12px 20px";
  notification.style.borderRadius = "6px";
  notification.style.color = "white";
  notification.style.fontSize = "14px";
  notification.style.zIndex = "9999";
  notification.style.animation = "slideIn 0.3s ease";
  notification.style.backgroundColor =
    type === "success" ? "#10b981" : "#ef4444";
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ============================== ANALYTICS ====================================================
