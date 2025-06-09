from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# Менеджер подключений
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Эндпоинт WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Сообщение: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Клиент отключился")

# HTML для теста
@app.get("/")
def get():
    return HTMLResponse("""
    <html>
        <head>
            <title>WebSocket Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <input id="msg" type="text" placeholder="Введите сообщение..."/>
            <button onclick="sendMessage()">Отправить</button>
            <ul id="messages"></ul>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = (event) => {
                    const messages = document.getElementById("messages");
                    const li = document.createElement("li");
                    li.innerText = event.data;
                    messages.appendChild(li);
                };
                function sendMessage() {
                    const input = document.getElementById("msg");
                    ws.send(input.value);
                    input.value = "";
                }
            </script>
        </body>
    </html>
    """)
