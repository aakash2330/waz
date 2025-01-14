import asyncio
import json
import threading
import redis


class RedisManager:
    instance = None

    def __init__(self, host="localhost", port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.subscriber = self.redis_client.pubsub()

    @staticmethod
    def getInstance():
        if not RedisManager.instance:
            RedisManager.instance = RedisManager()
            return RedisManager.instance
        return RedisManager.instance

    def subscribe(self, channel, callback, userId):
        self.subscriber.subscribe(channel)

        async def async_listen():
            while True:  # Continuous listening loop
                try:
                    message = self.subscriber.get_message()  # Non-blocking get
                    if message:
                        print(f"Message received from pubsub ----------- {message}")
                        if message["type"] == "message":  # Only process actual messages
                            await callback(
                                message=message["data"],  # or message.get('data')
                                spaceId=channel,
                                userId=userId,
                            )
                    await asyncio.sleep(0.001)  # Small delay to prevent CPU hogging
                except Exception as e:
                    print(f"Error in async_listen: {e}")

        def listen():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(async_listen())
            except Exception as e:
                print(f"Error in listen thread: {e}")

        listen_thread = threading.Thread(target=listen, daemon=True)
        listen_thread.start()

    def unsubscribe(self, channel):
        self.subscriber.unsubscribe(channel)

    def publish(self, channel, message):
        message_str = json.dumps(message)
        self.redis_client.publish(channel, message_str)

    def close(self):
        self.redis_client.close()


# {"type":"join","payload":{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRiOTdjZGE0LTM5OWItNDA3Yy1iNjg4LTUyMWRjNDMxZTgwMyIsInVzZXJuYW1lIjoiYWRtaW4yIiwidHlwZSI6ImFkbWluIiwiYXZhdGFySWQiOm51bGx9.-RZLZcV21iwvzXLwSmbSje-WsDuXLEn4jv2T6p0TkP4","spaceId":"1aa44976-3f63-4b99-893b-b9c897ee3d2f"}}}}
# {"type":"join","payload":{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImI1OTI5YjQyLTQ0NDAtNDg4Mi05YjEyLTk4MDRhNWQ4M2NjMSIsInVzZXJuYW1lIjoiYWRtaW4xMDEiLCJ0eXBlIjoiYWRtaW4iLCJhdmF0YXJJZCI6bnVsbH0.9gNjUHt-yXqWPQDXFG_KZnAVSKRM0KfhzZGLkN1JmZQ","spaceId":"1aa44976-3f63-4b99-893b-b9c897ee3d2f"}}
# {"type":"move","payload":{"x":"1","y":"1"}}
