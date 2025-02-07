const carousel = document.querySelector(".carousel-items");

// Carousel Scroll Functions
function scrollToTheLeft() {
  document
    .querySelector(".carousel")
    .scrollBy({ left: -220, behavior: "smooth" });
}

function scrollRight() {
  document
    .querySelector(".carousel")
    .scrollBy({ left: 220, behavior: "smooth" });
}
