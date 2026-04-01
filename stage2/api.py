from __future__ import annotations

import os
from fastapi import FastAPI
from pydantic import BaseModel

from .parser import parse_query
from .service import NavigationService

DETECTION_DIR = os.getenv("STAGE2_DETECTION_DIR", "detection_results")
DB_PATH = os.getenv("STAGE2_DB_PATH", "stage2_navigation.db")

service = NavigationService(DETECTION_DIR, DB_PATH)
service.initialize(rebuild=not os.path.exists(DB_PATH))

app = FastAPI(title="Stage II Indoor Navigation API", version="1.0.0")


class QueryPayload(BaseModel):
    query: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/parse")
def parse(payload: QueryPayload) -> dict:
    return parse_query(payload.query).model_dump()


@app.post("/query")
def query(payload: QueryPayload) -> dict:
    response = service.query(payload.query)
    return response.model_dump()
