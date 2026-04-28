from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependencies import verify_api_key, get_screening_repo
from infrastructure.screening_repository import IScreeningRepository
from interfaces.schemas.screening_request import CreateScreeningRequest, PatchScreeningRequest
from interfaces.schemas.screening_response import ScreeningResponse
from domain.screening import Screening

router = APIRouter(
    prefix="/screenings",
    tags=["screenings"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/", response_model=list[ScreeningResponse])
def list_screenings(
    genre: str | None = Query(default=None),
    date: str | None = Query(default=None),
    hall: str | None = Query(default=None),
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> list[ScreeningResponse]:
    return [ScreeningResponse.from_entity(s) for s in repo.list_all(genre, date, hall)]


@router.get("/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: int,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    s = repo.get_by_id(screening_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(s)


@router.post("/", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
def create_screening(
    body: CreateScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    entity = Screening(**body.model_dump())
    return ScreeningResponse.from_entity(repo.create(entity))


@router.put("/{screening_id}", response_model=ScreeningResponse)
def replace_screening(
    screening_id: int,
    body: CreateScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    entity = Screening(**body.model_dump())
    updated = repo.replace(screening_id, entity)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(updated)


@router.patch("/{screening_id}", response_model=ScreeningResponse)
def patch_screening(
    screening_id: int,
    body: PatchScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    # exclude_unset=True: skip fields the client didn't send at all.
    # Do NOT add exclude_none=True — that would silently swallow {"genre": null},
    # preventing clients from intentionally clearing the nullable genre field.
    data = body.model_dump(exclude_unset=True)
    updated = repo.patch(screening_id, data)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(updated)


@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> None:
    if not repo.delete(screening_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
