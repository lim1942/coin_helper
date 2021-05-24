import aiohttp
import asyncio

async def main():

    async with aiohttp.ClientSession() as session:
        async with session.get('http://www.baidu.com') as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            print("Body:", html[:15], "...")
loop = asyncio.get_event_loop()
c = asyncio.run_coroutine_threadsafe(main(),loop)