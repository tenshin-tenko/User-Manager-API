from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from fastapi.params import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

import jwt
from pwdlib import PasswordHash, exceptions
from sqlmodel import Session, select
from http import HTTPStatus

from .config import Token
from .db.database import get_session
from .schema.user_schema import UserModel, UserRole

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def error_details(detail):
    return {'error': str(detail)}

def password_hashed(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except exceptions.UnknownHashError:
        # Hash inválido, considerar senha inválida
        return False

def create_acess_token(user: UserModel, data: dict):
    try:
        to_encode = data.copy()
        if user.role == UserRole.ADMIN:
            Token.ACESS_TOKEN_EXPIRE_MINUTES = 99999999
        
        expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            minutes = Token.ACESS_TOKEN_EXPIRE_MINUTES
        )
        
        to_encode.update({
            "sub": user.username,
            "exp": expire,
            "user_id": user.id
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            Token.SECRET_KEY,
            algorithm=Token.ALGORITHM
        )
        return encoded_jwt

    except Exception as e:
        return error_details(e)

def create_token_by_role(user: UserModel):
    try:
        data = {"role": user.role}
        return create_acess_token(user, data)
    except Exception as e:
        return error_details(e)

def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
    try:
        statement = select(UserModel).where(UserModel.username == username)
        user = session.exec(statement).first()

        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    except Exception as e:
        raise e

def identify_admin(token: str, session: Session):
    statement = select(UserModel).where(UserModel.token == token)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Error 404: TOKEN NOT FOUND"
        )
    else:
        if result.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=HTTPStatus.NOT_ACCEPTABLE,
                detail="Error 401: NOT ACCEPTABLE"
            )
    return result

def identify_user(token: str, session: Session):
    statement = select(UserModel).where(UserModel.token == token)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Error 404: TOKEN NOT FOUND"
        )
    else:
        if result.role != UserRole.USER:
            raise HTTPException(
                status_code=HTTPStatus.NOT_ACCEPTABLE,
                detail="Error 401: NOT ACCEPTABLE"
            )
    return result