import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, update, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, SearchQuery
from app.utils.auth import get_current_user
from app.utils.embeddings import get_embedding
from app.config import get_settings

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
settings = get_settings()


async def _index_embedding(task_id: uuid.UUID, text: str, db_url: str):
    """Background task: generate and store embedding after task creation."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    engine = create_async_engine(db_url)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        vec = get_embedding(text, settings.embedding_model)
        if vec is not None:
            await session.execute(
                update(Task).where(Task.id == task_id).values(embedding=vec)
            )
            await session.commit()
    await engine.dispose()


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Task).where(Task.owner_id == current_user.id)
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
    if priority_filter:
        stmt = stmt.where(Task.priority == priority_filter)
    stmt = stmt.order_by(Task.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Generate embedding in the background so the response is fast
    embed_text = f"{task.title} {task.description or ''} {task.tags or ''}".strip()
    background_tasks.add_task(
        _index_embedding, task.id, embed_text, settings.database_url
    )
    return task


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_owned_task(task_id, current_user.id, db)
    return task


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_owned_task(task_id, current_user.id, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    # Re-index embedding if text content changed
    if any(f in update_data for f in ("title", "description", "tags")):
        embed_text = f"{task.title} {task.description or ''} {task.tags or ''}".strip()
        background_tasks.add_task(
            _index_embedding, task.id, embed_text, settings.database_url
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await _get_owned_task(task_id, current_user.id, db)
    await db.delete(task)
    await db.commit()


@router.post("/search", response_model=list[TaskOut])
async def semantic_search(
    payload: SearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Natural-language semantic search using pgvector cosine similarity."""
    query_vec = get_embedding(payload.query, settings.embedding_model)

    if query_vec is None:
        # Fallback: basic keyword search when embedding model is unavailable
        keyword = f"%{payload.query}%"
        stmt = (
            select(Task)
            .where(Task.owner_id == current_user.id)
            .where(
                Task.title.ilike(keyword) | Task.description.ilike(keyword)
            )
            .limit(payload.limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    # pgvector cosine distance — lower is more similar
    stmt = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .where(Task.embedding.isnot(None))
        .order_by(Task.embedding.cosine_distance(query_vec))
        .limit(payload.limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def _get_owned_task(task_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> Task:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
