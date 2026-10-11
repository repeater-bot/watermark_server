from .root_router import root_router
from fastapi.responses import PlainTextResponse

@root_router.get("/alived", tags=["alive"])
def alived():
    return PlainTextResponse(
        content = "OK"
    )