from fastapi.websockets import WebSocket


async def joinUserToRoom(ws: WebSocket, spaceId: str, userId: str | None = "asda"):
    return await ws.send_text(f"user - {userId} has joined space - {spaceId}")


async def moveUser(ws: WebSocket, x: str, y: str, userId: str | None = "asdad"):
    return await ws.send_text(f"user - {userId} is now at x - {x} and y - {y} ")
