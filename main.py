from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes.attendance import router as attendance_router
from database.connection import db  # Ensure the database connection is imported

app = FastAPI()

# Enable CORS for WebSockets & HTTP requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance_router, prefix="/api")

# Store connected WebSocket clients
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # ✅ Explicitly accept the WebSocket connection
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.get("/")
async def home():
    return {"message": "AI Attendance System Backend is Running"}
