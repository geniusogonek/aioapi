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

class Response:
    def __init__(self, body=b'', status_code=200, content_type='text/html'):
        self.body = body
        self.status_code = status_code
        self.content_type = content_type

    @property
    def headers(self):
        return {
            'Content-Type': self.content_type,
            'Content-Length': len(self.body),
        }

    def get_bytes(self):
        status_line = f"HTTP/1.1 {self.status_code} {self._get_status_message()}\r\n".encode()
        header_lines = [
            f"{key}: {value}\r\n".encode()
            for key, value in self.headers.items()
        ]
        blank_line = b"\r\n"
        return status_line + b''.join(header_lines) + blank_line + self.body

    def _get_status_message(self):
        messages = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
        }
        return messages.get(self.status_code, "Unknown")