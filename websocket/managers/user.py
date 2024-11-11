import json
import logging
from typing import Any, Callable

import jwt
from cuid2 import cuid_wrapper
from fastapi import WebSocket

from handlers.user import joinUserToRoom, moveUser

logging.basicConfig(level=logging.DEBUG)
cuid_generator: Callable[[], str] = cuid_wrapper()


class UserManager:
    def __init__(self, ws: WebSocket):
        self.id: str = cuid_generator()
        self.userId: str | None = None
        self.ws: WebSocket = ws
        self.x: int = 0
        self.y: int = 0
        self.spaceId: str | None = None

    async def handle_message(self, message_type: str, payload: Any):
        if message_type == "join":
            print(f"joining space {payload}")
            token = payload.get("token")

            # verify token and get userId
            if not token:
                raise ValueError("No Token")

            logging.info("decoding jwt token")
            jwtPayload = jwt.decode(token.decode(), "secret", algorithms=["HS256"])

            if not jwtPayload:
                raise ValueError("couldnt verify token")

            self.userId = jwtPayload.get("userId")
            spaceId = payload.get("spaceId")

            if spaceId:
                return await joinUserToRoom(
                    ws=self.ws, spaceId=spaceId, userId=self.userId
                )
            return await self.ws.send_text("spaceId is required")

        elif message_type == "move":
            x = payload.get("x")
            y = payload.get("y")
            if x is not None and y is not None:
                return await moveUser(ws=self.ws, x=x, y=y, userId=self.userId)
            return await self.ws.send_text("x/y is required")

        return await self.ws.send_text("Invalid message type")

    async def start(self):
        try:
            while True:
                data = await self.ws.receive_text()
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    payload = message.get("payload", {})
                    print(f"payload ---------------------{payload}")
                    if not message_type:
                        logging.error("No message Type Defined")
                        await self.ws.send_text("No message type found")
                        continue

                    await self.handle_message(message_type, payload)

                except json.JSONDecodeError:
                    logging.error("Invalid JSON received")
                    await self.ws.send_text("Invalid message format")

        except Exception as e:
            logging.error(f"WebSocket error: {str(e)}")
            await self.ws.close()
