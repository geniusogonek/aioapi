import json
import aiofiles


class HTMLResponse:
    def __init__(self, name):
        self.name = name

    async def get(self):
        async with aiofiles.open(self.name, mode="rb") as file:
            contents = await file.read()
        return contents


class JSONResponse:
    def __init__(self, data):
        self.data = data

    async def get(self):
        return json.dumps(self.data).encode()


class PlainTextResponse:
    def __init__(self, data):
        self.data = data

    async def get(self):
        return self.data.encode()