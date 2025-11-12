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
