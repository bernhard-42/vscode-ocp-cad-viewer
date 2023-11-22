from persistence import modify_copyreg
from build123d import *
import pickle
from backend import BUFFER_SIZE_HEADER
import asyncio

modify_copyreg()

box = Box(10, 10, 10).solid()


class AsyncSender:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def send(self, obj):
        try:
            data = pickle.dumps(obj)
            reader, writer = await asyncio.open_connection(self.host, self.port)

            header = len(data).to_bytes(BUFFER_SIZE_HEADER)
            writer.write(header + data)
            await writer.drain()

            writer.close()
            await writer.wait_closed()

        except Exception as e:
            print(f"Error sending/receiving message: {e}")


if __name__ == "__main__":
    sender = AsyncSender("localhost", 9999)
    asyncio.run(sender.send(box))
