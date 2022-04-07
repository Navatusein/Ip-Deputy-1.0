import asyncio

from datetime import datetime, timedelta


async def wait_until(hour: int = 0, minute: int = 0, second: int = 0):
    datetime_now = datetime.now().time()
    time_run = timedelta(hours=hour, minutes=minute, seconds=second)
    time_now = timedelta(hours=datetime_now.hour, minutes=datetime_now.minute, seconds=datetime_now.second)

    await asyncio.sleep((time_run - time_now).seconds)

