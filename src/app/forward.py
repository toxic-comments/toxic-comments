from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import text

from dependencies import get_connection

router = APIRouter()

@router.post("/forward")
def forward(conn = Depends(get_connection)):
    result = conn.execute(text("select 1;"))
    return result.cursor.fetchall()