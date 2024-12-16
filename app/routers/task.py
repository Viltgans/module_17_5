from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.orm import Session
from app.models import User, Task
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])

@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
     tasks = db.scalars(select(Task)).all()
     return tasks

@router.get('/task_id')
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
     task = db.scalar(select(Task).where(task_id == Task.id))
     if task is None:
          raise HTTPException(status_code=404, detail="User not found")
     return task

## ! ATTENTION !
@router.post('/create')
async def create_task(user_id: int, db: Annotated[Session, Depends(get_db)], create: CreateTask):
     user = db.scalar(select(User).where(user_id == User.id))
     if user is None:
          raise HTTPException(status_code=404, detail="User not found")
     db.execute(insert(Task).values(title=create.title,
                                    content=create.content,
                                    priority = create.priority,
                                    user_id=user_id,
                                    slug = slugify(create.title)))
     db.commit()
     return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
## ! ATTENTION !

@router.put('/update')
async def update_task(user_id: int, db: Annotated[Session, Depends(get_db)], upgrade: UpdateTask):
     task = db.scalars(select(Task).where(user_id == Task.id))
     if task is None:
          raise HTTPException(status_code=404, detail="User not found")
     db.execute(update(Task).where(user_id == Task.id).values(title=upgrade.title,
                                                              content=upgrade.content,
                                                              priority=upgrade.priority))
     db.commit()
     return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

@router.delete('/delete')
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
     task = db.scalars(select(Task).where(task_id == Task.id))
     if task is None:
          raise HTTPException(status_code=404, detail="User not found")
     db.execute(delete(Task).where(task_id == Task.id))
     db.commit()
     return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}