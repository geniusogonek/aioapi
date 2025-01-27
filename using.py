import asyncio

from aioapi import AioAPI
from aioapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from aioapi.requests import Request


app = AioAPI(host="127.0.0.1", port=8080)


@app.get("/html")
async def html():
    """ТУТ МОЖНО ВЕРНУТЬ HTML КАК В ФАСТАПИ"""
    return HTMLResponse("index.html")


@app.get("/json")
async def json_():
    """МОЖНО DICT, TUPLE, LIST ВОЗВРАЩАТЬ И ОН БУДЕТ JSON, ПРЯМО КАК В ФАСТПАПИ"""
    return {"status": "ok", "users": ({"username": "test"}, {"username": "test2"})}
    # OR return JSONResponse({"status": "ok""})


@app.get("/str")
async def string():
    """МОЖНО ВОЗВРАЩАТЬ СТРОКИ И ОНО ВЕРНЕТСЯ КЛИЕНТУ (КАК В ФАСТАПИ)"""
    return "its the best web framework by genius dev"
    # OR return PlainTextResponse("its the best web framework by genius dev")


@app.get("/request")
async def request_(request: Request):
    """ЕСТЬ РЕКВЕСТЫ!!! (КАК В ФАСТАПИ)"""
    return {"status": "ok", "request": request.user_agent}


async def main():
    try:
        await app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())