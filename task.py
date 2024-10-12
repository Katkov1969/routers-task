
from fastapi import APIRouter, Depends, status, HTTPException     # Сессия БД
from sqlalchemy.orm import Session                                # Функция подключения к БД
from backend.db_depends import get_db                         # Аннотации, Модели БД и Pydantic.
from typing import Annotated

from models.user import User
from models.task import Task
from schemas import CreateTask, UpdateTask, CreateUser

# Функции работы с записями.
from sqlalchemy import insert, select, update, delete

# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/")
async def all_task(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    if tasks is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no tasks'
        )
    return tasks

#----------------------------------------------------------------------------------------------
@router.get("/task_id")
async def get_task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(User).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    else:
        return task

#-------------------------------------------------------------------------------------------------
@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)],create_user: CreateUser, create_task: CreateTask, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(insert(Task).values(title=create_task.title, content=create_task.content,
                                   priority=create_task.priority, slug=slugify(create_task.title)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Succesful'
    }

#-------------------------------------------------------------------------------------------------
@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    db.execute(update(Task).where(Task.id == task_id).values(
        title = update_task.title,
        content=update_task.content,
        priority=update_task.priority,
        completed=update_task.completed,
        user_id=update_task.user_id,
        slug = slugify(update_task.title),
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is succesful!'
    }

#-------------------------------------------------------------------------------------------------
@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task deleted is succesful!'
    }

