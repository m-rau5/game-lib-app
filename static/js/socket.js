// const socket = io.connect("http://localhost:5000");
const socket = io.connect("https://game-lib-app.onrender.com");

// Log connection
socket.on("connect", () => {
  console.log("Connected to WebSocket!");
});

// Listen for user status updates
socket.on("user_status", (data) => {
  console.log(
    `User ${data.username} is now ${data.online ? "online" : "offline"}`
  );
});
