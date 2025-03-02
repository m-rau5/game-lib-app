const carousel = document.querySelector(".carousel-items");

// Carousel Scroll Functions
function scrollToTheLeft(scrollAmount = 500) {
  document
    .querySelector(".carousel")
    .scrollBy({ left: -scrollAmount, behavior: "smooth" });
}

function scrollRight(scrollAmount = 500) {
  document
    .querySelector(".carousel")
    .scrollBy({ left: scrollAmount, behavior: "smooth" });
}

// handle the wishlist

async function toggleWishlist(gameId) {
  const wishlistBtn = document.getElementById(`wishlist-${gameId}`);

  // call udpate endpoint for the game's id
  const response = await fetch("/users/update_wishlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ game_id: gameId }),
  });

  const result = await response.json();

  if (result.success) {
    if (wishlistBtn.classList.contains("in-wishlist")) {
      wishlistBtn.classList.remove("in-wishlist");
      wishlistBtn.innerHTML = "❤️";
    } else {
      wishlistBtn.classList.add("in-wishlist");
      wishlistBtn.innerHTML = "💖";
    }
  } else {
    alert("Error: " + result.message);
  }
}
