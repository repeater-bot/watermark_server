import asyncio
from uvicorn import Server, Config

class WatermarkServer:
    def __init__(self, config: Config):
        self.server = Server(config=config)
        self.config = config

    async def run_serve(self):
        await self.server.serve()

    async def shutdown(self):
        await self.server.shutdown()

    def run(self, debug: bool = False):
        runner = asyncio.Runner(
            debug = debug,
            loop_factory = self.config.get_loop_factory()
        )
        runner.run(
            coro = self.run_serve()
        )