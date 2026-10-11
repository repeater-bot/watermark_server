from ..app import app
from .server_def import WatermarkServer
from environs import Env
from uvicorn import Config

env = Env()
env.read_env()

server = WatermarkServer(
    config = Config(
        app,
        host = env.str("HOST"),
        port = env.int("PORT"),
    )
)