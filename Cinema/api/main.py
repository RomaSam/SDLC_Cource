from fastapi import FastAPI
from interfaces.routers.screenings import router as screenings_router


def create_app() -> FastAPI:
    app = FastAPI(title="Cinema API", version="1.0.0")
    app.include_router(screenings_router)
    return app


app = create_app()
