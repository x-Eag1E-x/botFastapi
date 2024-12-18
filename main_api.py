from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uvicorn

app = FastAPI()

engine = create_async_engine('sqlite+aiosqlite:///tasks.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass
class TaskModel(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    date: Mapped[str]
@app.post('/setup_database')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return 200

class TaskAddSchema(BaseModel):
    name: str
    date: str

class TaskSchema(TaskAddSchema):
    id: int


@app.post('/task')
async def add_task(data: TaskAddSchema, session: SessionDep):
    new_task = TaskModel(
        name=data.name,
        date=data.date,
    )
    session.add(new_task)
    await session.commit()
    return 200

@app.get('/tasks')
async def get_books(session: SessionDep):
    query = select(TaskModel)
    result = await session.execute(query)
    return result.scalars().all()

@app.delete('/task/{task_id}')
async def del_taks(task_id: int, session: SessionDep):
    task = await session.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(task)
    await session.commit()
    return 200

if __name__ == "__main__":
    uvicorn.run("main_api:app", reload=True)