import logging

from fastapi import FastAPI, WebSocket
from managers.user_manager import UserManager

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


@app.websocket("/ws")
async def joinRoom(websocket: WebSocket):
    await websocket.accept()
    user = UserManager(ws=websocket)
    await user.start()
    await websocket.send_text("Websocket connection Established")
