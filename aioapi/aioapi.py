import re
import asyncio
import colorama

from urllib.parse import parse_qs
from .responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from .requests import Request


colorama.init(True)


class EndPoint:
    def __init__(self, method, path, endpoint_func, response_class):
        self.method = method
        self.path = path
        self.endpoint_func = endpoint_func
        self.response_class = response_class

    def __str__(self):
        return f'EndPoint(method="{self.method}", path="{self.path}", response_class="{self.response_class}")'

class AioAPI:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.endpoints: list[EndPoint] = [] # Хранение доступных эндпоинтов

    def find_endpoint_and_params(self, url: str) -> tuple[EndPoint, dict]:
        parts = url.split('?', maxsplit=1)

        path = parts[0]
        query_string = parts[1] if len(parts) > 1 else ""
        params = dict()
        
        for endpoint in self.endpoints:
            pattern = re.sub(r'\{[^}]*\}', r'([^\/]+)', endpoint.path)

            match = re.match(f"^{pattern}$", path)
            if endpoint.method == self.method and match:
                groups = match.groups()
                if groups:
                    params.update(dict(zip(re.findall(r'{([^}]+)}', endpoint.path), groups)))
                break
        else:
            return None, None

        if query_string:
            parsed_query = parse_qs(query_string)
            params.update({k: v[0] for k, v in parsed_query.items()})

        for key in params.keys():
            type_ = endpoint.endpoint_func.__annotations__.get(key)
            if type_ is not None:
                params[key] = type_(params[key])
        return endpoint, params

    async def write(self, writer, response: Response, data):
        if response.status_code == 200:
            print(colorama.Fore.GREEN + f"{self.method} on {self.path} | {self.type}", end=f"{colorama.Fore.GREEN} - ")
            print(colorama.Fore.GREEN + "200")
        else:
            print(colorama.Fore.RED + f"{self.method} on {self.path} | {self.type}", end=f"{colorama.Fore.RED} - ")
            print(colorama.Fore.RED + str(response.status_code))
        writer.write(response.get_bytes() + data)
        await writer.drain()
        writer.close()

    def get(self, path, response_class=PlainTextResponse):
        """Создание нового эндпоинта с методом GET"""
        def inner(func):
            self.endpoints.append(EndPoint("GET", path, func, response_class))
            return None
        return inner

    def post(self, path, response_class=PlainTextResponse):
        """Создание нового эндпоинта с методом POST"""
        def inner(func):
            self.endpoints.append(EndPoint("POST", path, func, response_class))
            return None
        return inner

    def put(self, path, response_class=PlainTextResponse):
        """Создание нового эндпоинта с методом PUT"""
        def inner(func):
            self.endpoints.append(EndPoint("PUT", path, func, response_class))
            return None
        return inner

    def delete(self, path, response_class=PlainTextResponse):
        """Создание нового эндпоинта с методом DELETE"""
        def inner(func):
            self.endpoints.append(EndPoint("DELETE", path, func, response_class))
            return None
        return inner

    async def return_404(self, writer):
        """Возвращение 404 если эндпоинт не найден"""
        await self.return_json(writer, await JSONResponse({"detail": "Not Found"}).get(), 404) # Возвращение 404 если страница не найденв

    async def return_html(self, writer, contents, status_code=200):
        """Функция возвращения text/html"""
        response = Response(contents, status_code, "text/html")
        await self.write(writer, response, contents)

    async def return_json(self, writer, contents, status_code=200):
        """Функция возвращения json"""
        response = Response(contents, status_code, "text/json")
        await self.write(writer, response, contents)

    async def return_text(self, writer, contents, status_code=200):
        """Функция возвращения text/plain"""
        response = Response(contents, status_code, "text/plain")
        await self.write(writer, response, contents)

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Функция-хэндлер для запросов"""
        request = await reader.readline()
        self.method, self.path, self.type = request.decode().strip().split() or ("", "", "")
        if (self.method, self.path, self.type) == ("", "", ""): # хз, какая то ошибка, это пока заглушка (надеюсь временная)
            return

        endpoint, params = self.find_endpoint_and_params(self.path)
        if endpoint is None:
            await self.return_404(writer)
            return

        # Передача в функцию-эндпоинт аргументов, которые она требует
        if endpoint.endpoint_func.__annotations__.get("request") == Request: # проверка, требуется ли request с аннотацией класса Request
            request = await reader.read(1024)
            kwargs_request = {key: value for key, value in map(lambda e: e.split(": "), request.decode().strip().split("\n"))}
            params["request"] = Request(**kwargs_request)
        answer = await endpoint.endpoint_func(**params)
        if isinstance(answer, (dict, tuple, list)): # Возвращаем словари, списки и кортежи (кортеж преобразовывается в список)
            contents = await JSONResponse(answer).get()
            await self.return_json(writer, contents)
        elif isinstance(answer, (HTMLResponse, JSONResponse, PlainTextResponse)):
            await self.return_html(writer, await answer.get())
        else: # Возвращаем строку 
            contents = await PlainTextResponse(str(answer)).get()
            await self.return_text(writer, contents)

    async def run(self):
        # Создание асинхронного сервера
        server = await asyncio.start_server(
            self._handle_connection,
            self.host,
            self.port
        )

        addr = server.sockets[0].getsockname()
        print(colorama.Fore.GREEN + f"Сервер запущен на {addr}")

        async with server:
            await server.serve_forever()
