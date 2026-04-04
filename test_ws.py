import asyncio
import websockets

async def test():
    async with websockets.connect('ws://100.87.245.64:18789') as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=3)
        print('Recebido:', msg)

asyncio.run(test())
