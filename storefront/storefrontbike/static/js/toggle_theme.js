// toggle_theme.js
document.addEventListener("DOMContentLoaded", function() {
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const body = document.body;
    
    // Check local storage for saved theme preference
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
    }

    themeToggleBtn.addEventListener("click", function() {
        body.classList.toggle("dark-mode");
        
        // Save preference to local storage
        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});