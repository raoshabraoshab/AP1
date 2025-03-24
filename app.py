from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chat history file
CHAT_HISTORY_FILE = "chat_history.txt"

# HTML Template with WebRTC Support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vikrant's Chatroom</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #ACC8E5; }
        #chatbox { width: 50%; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px gray; }
        ul { list-style-type: none; padding: 0; }
        li { background: #d1e7dd; padding: 10px; margin: 5px; border-radius: 5px; text-align: left; }
        input, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid gray; }
        button { background-color: #28a745; color: white; cursor: pointer; }
        button:hover { background-color: #218838; }
        video { width: 100%; max-width: 500px; border-radius: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Vikrant's Chatroom 🚀</h2>
    <div id="chatbox">
        <h3>Room ID: <span id="room_id"></span></h3>
        <ul id="messages"></ul>
        <input id="msg" type="text" placeholder="Type your message">
        <button onclick="sendMessage()">Send</button>
        <button onclick="pickEmoji()">😊</button>
        <button onclick="startCall()">📹 Start Video</button>
    </div>

    <video id="localVideo" autoplay muted></video>
    <video id="remoteVideo" autoplay></video>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io();
        var username = prompt("Enter your name:") || "Anonymous";
        var roomID = prompt("Enter Room ID (or leave empty to create a new room):") || Math.random().toString(36).substring(7);
        document.getElementById("room_id").innerText = roomID;
        socket.emit("join_room", roomID);

        socket.on("message", function(data) {
            var li = document.createElement("li");
            li.innerHTML = data;
            document.getElementById("messages").appendChild(li);
        });

        function sendMessage() {
            var msg = document.getElementById("msg").value;
            if (msg.trim() !== "") {
                socket.emit("message", { room: roomID, msg: "<b>" + username + ":</b> " + msg });
                document.getElementById("msg").value = "";
            }
        }

        function pickEmoji() {
            var emoji = prompt("Enter an emoji 😊:") || "";
            document.getElementById("msg").value += emoji;
        }

        document.getElementById("msg").addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });

        // WebRTC Setup
        var localVideo = document.getElementById("localVideo");
        var remoteVideo = document.getElementById("remoteVideo");
        var peerConnection;
        var config = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

        function startCall() {
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                .then(stream => {
                    localVideo.srcObject = stream;
                    peerConnection = new RTCPeerConnection(config);
                    stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));

                    peerConnection.ontrack = event => {
                        remoteVideo.srcObject = event.streams[0];
                    };

                    peerConnection.onicecandidate = event => {
                        if (event.candidate) {
                            socket.emit("ice_candidate", { room: roomID, candidate: event.candidate });
                        }
                    };

                    peerConnection.createOffer()
                        .then(offer => peerConnection.setLocalDescription(offer))
                        .then(() => {
                            socket.emit("offer", { room: roomID, offer: peerConnection.localDescription });
                        });
                });
        }

        socket.on("offer", function(data) {
            peerConnection = new RTCPeerConnection(config);
            peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                .then(stream => {
                    localVideo.srcObject = stream;
                    stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));
                });

            peerConnection.createAnswer()
                .then(answer => peerConnection.setLocalDescription(answer))
                .then(() => {
                    socket.emit("answer", { room: roomID, answer: peerConnection.localDescription });
                });
        });

        socket.on("answer", function(data) {
            peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
        });

        socket.on("ice_candidate", function(data) {
            peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('join_room')
def handle_join_room(data):
    join_room(data)
    emit("message", f"<i>⚡ User has joined the room {data}!</i>", room=data)

@socketio.on('message')
def handle_message(data):
    room = data["room"]
    msg = data["msg"]
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(msg + "\n")
    emit("message", msg, room=room)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data["room"])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data["room"])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    emit('ice_candidate', data, room=data["room"])

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
