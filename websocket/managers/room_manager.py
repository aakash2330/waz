import json
import logging
from typing import Dict

from managers.user_manager import UserManager
from .redis_manager import RedisManager


logging.basicConfig(level=logging.DEBUG)


class RoomManager:
    instance = None

    def __init__(self):
        self.rooms: dict[str, list[UserManager]] = dict()

    @staticmethod
    def getInstance():
        if not RoomManager.instance:
            RoomManager.instance = RoomManager()
            return RoomManager.instance
        return RoomManager.instance

    def joinUserToRoom(self, user: UserManager, spaceId):
        redis_client = RedisManager.getInstance()
        # find if user is a part of any space , if it is , remove it and add to new space
        if user.spaceId:
            self.rooms[user.spaceId] = [
                item for item in self.rooms[user.spaceId] if item.id != user.id
            ]
        if not self.rooms.get(spaceId):
            self.rooms[spaceId] = [user]
            user.spaceId = spaceId
            redis_client.subscribe(
                channel=user.spaceId, userId=user.id, callback=self.broadcast
            )
        else:
            self.rooms[spaceId].append(user)
            user.spaceId = spaceId

        print(f"subscribed the room {self.rooms}")

        redis_client.publish(
            channel=user.spaceId,
            message={"type": "join", "payload": {"userId": f"{user.userId}"}},
        )
        logging.info(f"user - {user.userId} has joined space - {user.spaceId}")

    def removeUserFromRoom(self, user: UserManager):
        if user.spaceId:
            self.rooms[user.spaceId] = [
                item for item in self.rooms[user.spaceId] if item.id != user.id
            ]

    async def broadcast(self, userId: str, spaceId: str, message):
        print("all the users are in the room are ------------------")
        for x in self.rooms[spaceId]:
            print(x.username)
        if self.rooms.get(spaceId):
            for x in self.rooms[spaceId]:
                print(f"{x.id} ------------------- here is userId")
                if x.id:
                    print(f"sending message to userId {x.id}")
                    if isinstance(message, bytes):
                        message = message.decode()
                    await x.ws.send_text(message)
        else:
            logging.error(f"unable to find room for the spaceId {spaceId}")
