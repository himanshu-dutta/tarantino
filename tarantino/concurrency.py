from tarantino.imports import asyncio


def set_timeout(fn, sec, *args, **kwargs):
    async def _wrapper():
        await asyncio.sleep(sec)
        await fn(*args, **kwargs)

    task = asyncio.create_task(_wrapper())
    return task.cancel


def set_interval(fn, sec, *args, **kwargs):
    async def _wrapper():
        while True:
            await asyncio.sleep(sec)
            await fn(*args, **kwargs)

    task = asyncio.create_task(_wrapper())
    return task.cancel
