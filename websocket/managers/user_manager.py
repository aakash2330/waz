import importlib
import json
import logging
from typing import Any, Callable

import jwt
import requests
from cuid2 import cuid_wrapper
from fastapi import WebSocket

from .redis_manager import RedisManager

logging.basicConfig(level=logging.DEBUG)
cuid_generator: Callable[[], str] = cuid_wrapper()


class UserManager:
    def __init__(self, ws: WebSocket):
        self.id: str = cuid_generator()
        self.userId: str | None = None
        self.username: str | None = None
        self.ws: WebSocket = ws
        self.x: int = 0
        self.y: int = 0
        self.spaceId: str | None = None

    async def handle_message(self, message_type: str, payload: Any):
        if message_type == "join":
            print(f"joining space {payload}")
            token = payload.get("token")

            # Verify token and get userId
            if not token:
                raise ValueError("No Token")

            logging.info("decoding jwt token")
            jwtPayload = jwt.decode(token, "secret", algorithms=["HS256"])

            if not jwtPayload:
                raise ValueError("couldn't verify token")

            # If token is validated, set the userId to the ID in token
            self.userId = jwtPayload.get("id")
            self.username = jwtPayload.get("username")

            spaceId = payload.get("spaceId")
            if spaceId:
                # Check if the space with the given ID exists
                backend_url = f"http://localhost:8080/user/space/check/{spaceId}"
                space_id_exists = requests.get(
                    backend_url,
                    headers={
                        "Content-Type": "text",
                        "authorization": f"Bearer {token}",
                    },
                ).json()

                # If space ID exists, let user join the room
                if space_id_exists.get("space_exists"):
                    return await self.joinUserToRoom(spaceId=spaceId)
                else:
                    raise ValueError(f"Space Id {spaceId} does not exist")

            return await self.ws.send_text("spaceId is required")

        elif message_type == "move":
            x = payload.get("x")
            y = payload.get("y")
            if x is not None and y is not None:
                return await self.moveUser(x=x, y=y)
            return await self.ws.send_text("x/y is required")

        elif message_type == "leave":
            x = payload.get("x")
            y = payload.get("y")
            if x is not None and y is not None:
                return await self.moveUser(x=x, y=y)
            return await self.ws.send_text("x/y is required")

        return await self.ws.send_text("Invalid message type")

    async def joinUserToRoom(self, spaceId: str):
        # Publish in the room that a user has joined
        room_manager = (
            importlib.import_module("managers.room_manager").RoomManager().getInstance()
        )
        room_manager.joinUserToRoom(user=self, spaceId=spaceId)

    async def moveUser(self, x, y):

        # TODO:check if the move is valid or not , for now let's just assume every move is valid
        # check whethether the user is part of the room or not
        # broadcast it to every other user minus self that the user has moved

        redis_client = RedisManager.getInstance()
        print(f"user {self.userId} moved to positon {x} , {y}")

        redis_client.publish(
            channel=self.spaceId,
            message={
                "type": "move",
                "payload": {"userId": f"{self.userId}", "x": x, "y": y},
            },
        )
        self.x = x
        self.y = y

    async def leaveRoom(self):
        room_manager = (
            importlib.import_module("managers.room_manager").RoomManager().getInstance()
        )
        room_manager.(user=self, spaceId=spaceId)

    async def start(self):
        try:
            while True:
                data = await self.ws.receive_text()
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    payload = message.get("payload", {})
                    if not message_type:
                        logging.error("No message type defined")
                        await self.ws.send_text("No message type found")
                        continue

                    await self.handle_message(message_type, payload)

                except json.JSONDecodeError:
                    logging.error("Invalid JSON received")
                    await self.ws.send_text("Invalid message format")

        except Exception as e:
            logging.error(f"WebSocket error: {str(e)}")
            await self.ws.close()
