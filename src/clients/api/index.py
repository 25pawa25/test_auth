from fastapi import APIRouter, status

router = APIRouter(tags=["Test route"])


@router.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
)
def healthcheck():
    return
