from ocp_tessellate.ocp_utils import deserialize
from asyncio import StreamWriter, StreamReader
import asyncio

BUFFER_SIZE_HEADER = 4  # Length of the header that contains the length of the message


class AsyncServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handle_client(self, reader: StreamReader, writer: StreamWriter):
        header = await reader.read(BUFFER_SIZE_HEADER)
        buffer = await reader.read(int.from_bytes(header))

        addr = writer.get_extra_info("peername")
        print(f"Received data from {addr!r}")

        self.handle_data(buffer)

        print("Closing the connection")
        writer.close()

    async def serve(self):
        print(f"Serving on {self.host}:{self.port}")
        server = await asyncio.start_server(self.handle_client, self.host, self.port)

        async with server:
            await server.serve_forever()

    def handle_data(self, data):
        obj = deserialize(data)
        print(obj)


if __name__ == "__main__":
    server = AsyncServer("localhost", 9999)
    asyncio.run(server.serve())
