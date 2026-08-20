from pydantic import BaseModel, Field
from typing import List, Literal

class ExtractedEntity(BaseModel):
    name: str = Field(
        description="Name of the person, place, faction, or important item."
    )
    category: Literal["NPC", "LOCATION", "ITEM", "FACTION"] = Field(
        description="The classification type of the entity."
    )
    status_or_detail: str = Field(
        description="Current state or key development (e.g., 'Allied with party', 'Killed in combat', 'Stolen')."
    )

# LLM Output Schema
class SessionSummaryOutput(BaseModel):
    title: str = Field(
        description="A creative and evocative title for the session recap."
    )
    key_events: List[str] = Field(
        description="Sequential bullet points of major narrative events that occurred."
    )
    extracted_entities: List[ExtractedEntity] = Field(
        description="List of all NPCs, locations, factions, or items introduced or significantly modified."
    )
    unresolved_hooks: List[str] = Field(
        description="Open quest lines, unsolved mysteries, or immediate threats left hanging."
    )

class SessionLedgerRequest(BaseModel):
    campaign_name: str = Field(
        description="The overarching campaign title."
    )
    game_system: str = Field(
        default="D&D 5e",
        description="The game mechanics system (e.g., 'D&D 5e', 'Call of Cthulhu', 'Cyberpunk RED')."
    )
    raw_notes: str = Field(
        description="Unformatted GM notes or chat logs taken during the live session."
    )