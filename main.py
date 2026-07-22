
import logging
import logging.handlers
import os

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


uvicorn_logger: logging.Logger = logging.getLogger("uvicorn")
uvicorn_access_logger: logging.Logger = logging.getLogger("uvicorn.access")
uvicorn_error_logger: logging.Logger = logging.getLogger("uvicorn.error")
logger: logging.Logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if uvicorn_logger.handlers:
    logger.handlers = uvicorn_logger.handlers
    logger.propagate = False
else:
    logging.basicConfig(level=logging.INFO)

if os.getenv("PRODUCTION"):
    if (syslog_host := os.getenv("SYSLOG_HOST")):
        syslog_handler = logging.handlers.SysLogHandler(
            (
                syslog_host, 
                int(os.getenv("SYSLOG_PORT", str(logging.handlers.SYSLOG_UDP_PORT)))
            )
        )
        syslog_handler.setFormatter(logging.Formatter('io.bbayu.meal_tracker_service.%(name)s: %(message)s'))

        logger.addHandler(syslog_handler)
        if uvicorn_logger.handlers:
            uvicorn_logger.addHandler(syslog_handler)
        if uvicorn_access_logger.handlers:
            uvicorn_access_logger.addHandler(syslog_handler)
        if uvicorn_error_logger.handlers:
            uvicorn_error_logger.addHandler(syslog_handler)

    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

del uvicorn_logger, uvicorn_access_logger, uvicorn_error_logger

app = FastAPI()

engine = create_engine("sqlite:///mydatabase.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)

def get_db():
    with SessionLocal() as db:
        yield db

@app.get("/", include_in_schema=False, response_class=PlainTextResponse)
async def get_root() -> str:
    return "Hello World"
