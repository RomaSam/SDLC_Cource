from fastapi import Header, HTTPException, status
from config import settings
from infrastructure.screening_repository import IScreeningRepository, SQLiteScreeningRepository


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_screening_repo() -> IScreeningRepository:
    return SQLiteScreeningRepository()
