from fastapi import APIRouter

router = APIRouter()

@router.get("/history")
def get_history():
    return "ok"

@router.delete("/history")
def delete_history():
    return "ok"

@router.get("/history/stats")
def get_stats():
    return "ok"