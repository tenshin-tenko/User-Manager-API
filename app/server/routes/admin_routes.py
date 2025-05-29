from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.params import Depends

from sqlmodel import Session, select
from http import HTTPStatus

from ..db.database import create_db_and_tables, get_session
from ..schema.user_schema import UserModel
from ..security import (
    error_details,
    oauth2_scheme,
    identify_admin
)

admin_router = APIRouter()

@admin_router.get("/admin/list-users")
def list_all_users(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
):
    identify_admin(token, session)
    try:
        result = session.exec(select(UserModel)).all()
        return result
    except Exception as e:
        error_details(e)

# -- POSTS --
@admin_router.post("/admin/create-table")
def create_table():
    try:
        create_db_and_tables()
        return {'msg': 'Tabela criado com sucesso'}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail='Error 500: Internal Server Error')

# -- DELETES --
@admin_router.delete("/admin/delete-user/{user_id}")
def delete_user_by_id(
        user_id: int,
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
):
    identify_admin(token, session)
    try:
        user = session.get(UserModel, user_id)
        if not user:
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"error": "Usuário não encontrado"})

        session.delete(user)
        session.commit()
        return {"msg": "Usuário deletado com sucesso"}

    except Exception as e:
        error_details(e)
