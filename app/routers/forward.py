from fastapi import APIRouter

router = APIRouter()

@router.post("/forward")
def forward():
    return "ok"