from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import get_user_id
from backend.db.session import get_connection
from backend.models import QuestionAnswerBody
from backend.services import question_service

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
def list_questions(product_count: int = 1, offset: int = 0):
    return {"questions": question_service.list_questions(product_count, offset)}


@router.post("/answer")
def answer_question(body: QuestionAnswerBody, user_id: str = Depends(get_user_id)):
    conn = get_connection()
    try:
        return question_service.answer_question(
            conn,
            user_id,
            body.question_id,
            product_id=body.product_id,
            product_ids=body.product_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()
