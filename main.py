import logging
import logging.handlers
import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src import repos, schemas

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
    if syslog_host := os.getenv("SYSLOG_HOST"):
        syslog_handler = logging.handlers.SysLogHandler(
            (syslog_host, int(os.getenv("SYSLOG_PORT", str(logging.handlers.SYSLOG_UDP_PORT))))
        )
        syslog_handler.setFormatter(logging.Formatter("io.bbayu.meal_tracker_service.%(name)s: %(message)s"))

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


@app.get("/brand", tags=["Brand"], response_model=list[schemas.BrandResponse])
async def get_brands(db: Annotated[Session, Depends(get_db)]):
    repo = repos.BrandRepo(db)
    brands = repo.get_all()
    return repo.to_response(brands)


@app.get("/brand/{id}", tags=["Brand"], response_model=schemas.BrandResponse)
async def get_brand(
    id: Annotated[UUID, Path(description="The ID of the brand")], db: Annotated[Session, Depends(get_db)]
):
    repo = repos.BrandRepo(db)
    brand = repo.get_one(id)
    if brand is None:
        raise HTTPException(404, detail="Brand not found")
    else:
        return repo.to_response(brand)


@app.post("/brand", tags=["Brand"], status_code=201, response_model=schemas.BrandResponse)
async def create_brand(brand_req: schemas.BrandRequest, db: Annotated[Session, Depends(get_db)]):
    repo = repos.BrandRepo(db)
    try:
        brand = repo.create(brand_req)
        return repo.to_response(brand)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@app.delete("/brand/{id}", tags=["Brand"], status_code=204)
async def delete_brand(
    id: Annotated[UUID, Path(description="The ID of the brand")], db: Annotated[Session, Depends(get_db)]
):
    repo = repos.BrandRepo(db)
    try:
        repo.delete(id)
    except ValueError:
        raise HTTPException(404, detail="Brand not found")


@app.patch("/brand/{id}/alias/{name}", tags=["Brand"], response_model=schemas.BrandResponse)
async def add_brand_alias(
    id: Annotated[UUID, Path(description="The ID of the brand")],
    name: Annotated[str, Path(description="The new alias to be added")],
    db: Annotated[Session, Depends(get_db)],
):
    repo = repos.BrandRepo(db)
    try:
        brand = repo.add_alias(id, name)
        if brand is None:
            raise HTTPException(404, detail="Brand not found")
        else:
            return repo.to_response(brand)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@app.delete("/brand/{id}/alias/{name}", tags=["Brand"], response_model=schemas.BrandResponse)
async def remove_brand_alias(
    id: Annotated[UUID, Path(description="The ID of the brand")],
    name: Annotated[str, Path(description="The alias to be removed from this brand")],
    db: Annotated[Session, Depends(get_db)],
):
    repo = repos.BrandRepo(db)
    try:
        brand = repo.remove_alias(id, name)
        if brand is None:
            raise HTTPException(404, detail="Brand not found")
        else:
            return repo.to_response(brand)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@app.post("/brand/{idKeep}/mergeWith/{idRemove}", tags=["Brand"], response_model=schemas.BrandResponse)
async def merge_brands(
    id_keep: Annotated[UUID, Path(description="The ID of the brand to be kept", alias="idKeep")],
    id_remove: Annotated[UUID, Query(description="The ID of the brand to be removed", alias="idRemove")],
    db: Annotated[Session, Depends(get_db)],
):
    repo = repos.BrandRepo(db)
    try:
        brand_keep = repo.merge(id_keep=id_keep, id_remove=id_remove)
        return repo.to_response(brand_keep)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
