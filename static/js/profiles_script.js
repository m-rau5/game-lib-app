function openSettingsPopup() {
  document.getElementById("settings-popup").style.display = "block";
}

function closeSettingsPopup() {
  document.getElementById("settings-popup").style.display = "none";
}

// Handle form submission
document
  .getElementById("change-username-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const newUsername = document.getElementById("new-username").value;

    const response = await fetch("/users/user_profile/change_username", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_username: newUsername }),
    });

    const result = await response.json();

    if (result.success) {
      alert("Username updated successfully!");
      location.reload(); // Refresh the page to reflect changes
    } else {
      alert("Error: " + result.message);
    }
  });
