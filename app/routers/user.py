from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.orm import Session
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])

@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users

@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(user_id == User.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ! NEW CODE !
@router.get('/user_id/tasks')
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(user_id == User.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tasks = db.scalars(select(Task).where(user_id == Task.user_id)).all()
    return tasks
# ! NEW CODE !

@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create: CreateUser):
    db.execute(insert(User).values(username=create.username,
                                   firstname=create.firstname,
                                   lastname=create.lastname,
                                   age=create.age,
                                   slug=slugify(create.username)))

    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

@router.put('/update')
async def update_user(user_id: int, db: Annotated[Session, Depends(get_db)], upgrade: UpdateUser):
    user = db.scalars(select(User).where(user_id == User.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.execute(update(User).where(user_id == User.id).values(firstname=upgrade.firstname,
                                                             lastname=upgrade.lastname,
                                                             age=upgrade.age))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

## ! ATTENTION !
@router.delete('/delete')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(user_id == User.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.execute(delete(User).where(user_id == User.id))
    db.execute(delete(Task).where(user_id == Task.user_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
## ! ATTENTION !
