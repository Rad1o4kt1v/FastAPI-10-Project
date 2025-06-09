from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from .models import Note
from .schemas import NoteCreate

async def create_note(note_data: NoteCreate, session: AsyncSession) -> Note:
    note = Note(text=note_data.text)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note

async def get_all_notes(session: AsyncSession) -> list[Note]:
    result = await session.execute(select(Note))
    return result.scalars().all()
