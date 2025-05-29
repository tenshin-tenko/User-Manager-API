from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import Session

from ..db.database import get_session
from ..security import authenticate_user, create_token_by_role

auth_router = APIRouter()

@auth_router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Error 401: Credenciais inválidas")
    
    return create_token_by_role(user)
