import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from interfaces.routers.screenings import router as screenings_router


def create_app() -> FastAPI:
    app = FastAPI(title="Cinema API", version="1.0.0")
    app.include_router(screenings_router)

    @app.exception_handler(sqlite3.Error)
    async def sqlite_error_handler(request: Request, exc: sqlite3.Error) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "A database error occurred. Please try again later."},
        )

    return app


app = create_app()
