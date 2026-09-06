from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from sqlalchemy.orm import selectinload

async def get_or_create_campaign(db: AsyncSession, name: str, system: str) -> models.Campaign:
    
    result = await db.execute(
        select(models.Campaign).where(models.Campaign.name == name)
    )
    campaign = result.scalars().first()
    
    if not campaign:
        campaign = models.Campaign(name=name, game_system=system)
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
    return campaign

async def save_session_data(
    db: AsyncSession, 
    campaign_id: int, 
    raw_notes: str, 
    llm_output: schemas.SessionSummaryOutput
) -> models.Session:
    
    db_session = models.Session(
        campaign_id=campaign_id,
        title=llm_output.title,
        raw_notes=raw_notes,
        unresolved_hooks=llm_output.unresolved_hooks
    )
    db.add(db_session)
    
    # Flush sends the insert to the DB to generate the ID, but doesn't commit the transaction yet
    await db.flush() 
    
    # Iterate through extracted entities and link them to the new session ID
    for entity in llm_output.extracted_entities:
        db_entity = models.Entity(
            session_id=db_session.id,
            name=entity.name,
            category=entity.category,
            status_or_detail=entity.status_or_detail
        )
        db.add(db_entity)
        
    #Commit everything together (if one fails, they all fail, preventing orphaned data)
    await db.commit()
    await db.refresh(db_session)
    
    return db_session


async def get_session_by_id(db: AsyncSession, session_id: int) -> models.Session | None:
    result = await db.execute(
        select(models.Session)
        .options(selectinload(models.Session.entities))
        .where(models.Session.id == session_id)
    )
    return result.scalars().first()

async def update_session(
    db: AsyncSession, 
    db_session: models.Session, 
    update_data: schemas.SessionUpdateRequest
) -> models.Session:
    if update_data.title is not None:
        db_session.title = update_data.title
    if update_data.unresolved_hooks is not None:
        db_session.unresolved_hooks = update_data.unresolved_hooks

    await db.commit()
    await db.refresh(db_session)
    return db_session

async def delete_session(db: AsyncSession, db_session: models.Session):
    await db.delete(db_session)
    await db.commit()