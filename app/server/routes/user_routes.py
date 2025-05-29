from http import HTTPStatus
from sqlmodel import Session, select

from ..db.database import get_session
from ..schema.user_schema import UserModel, UserPublic, UserRole

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path
)

from ..security import (
    error_details,
    password_hashed,
    create_token_by_role,
    identify_user,
    oauth2_scheme
)

user_router = APIRouter()

# -- POSTS --

@user_router.post("/user/create", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserModel, session: Session = Depends(get_session)):
    try:
        token = create_token_by_role(user)
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password=password_hashed(user.password),
            role=user.role.strip(),
            token=token
        )
        
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return UserPublic(
            username=user.username,
            email=user.email,
            role=user.role
        )
    
    except Exception as e:
        error = error_details(e)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=error["error"]
        )
        
# -- DELETES --

@user_router.delete("/user/delete/{username}", status_code=HTTPStatus.OK)
def delete_user(
        username: str = Path(..., description="Username to delete"),
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
):
    current_user = identify_user(token, session)

    if current_user.role != UserRole.ADMIN and current_user.username != username:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You dont have permition to delete this user"
        )
    result = session.exec(select(UserModel).where(UserModel.username == username)).first() 
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="404: User not found"
        )
    
    try:
        session.delete(result)
        session.commit()
        return {"msg": f"User {username} delete with sucess"}
    except Exception as e:
        return error_details(e)