const socket = new WebSocket('ws://yourserver/ws/fbapp/{game_name}/');

// When the WebSocket opens
socket.onopen = function(e) {
    console.log("Connection established");
};

// When a message is received from the server
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const play = data.play;
    
    // Update your UI with the new play
    console.log("New Play:", play);
    document.getElementById("play-container").innerText = play;
};

// When the WebSocket connection closes
socket.onclose = function(e) {
    console.log("Connection closed");
};

// Handle errors
socket.onerror = function(e) {
    console.error("WebSocket error:", e);
};
