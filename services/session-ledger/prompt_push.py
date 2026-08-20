from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

load_dotenv()

# 1. Initialize LangSmith Client (automatically reads LANGCHAIN_API_KEY from .env)
client = Client()

# 2. Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a master archivist and chronicler for tabletop roleplaying games. "
            "Your role is to analyze messy, unorganized session notes and convert them into "
            "a clean, structured campaign chronicle.\n\n"
            "Guidelines:\n"
            "- Tailor terminology to the '{game_system}' ruleset.\n"
            "- Extract every named entity (NPCs, locations, important items, factions).\n"
            "- Distinguish clearly between resolved events and open quest hooks.\n"
            "- Do not invent facts not grounded in the provided notes."
        )
    ),
    (
        "human",
        (
            "Campaign: {campaign_name}\n"
            "Game System: {game_system}\n\n"
            "Raw Session Notes:\n"
            "'''\n{raw_notes}\n'''"
        )
    )
])

# 3. Push to LangSmith Hub
url = client.push_prompt("session-ledger-prompt", object=prompt)
print(f"Prompt successfully pushed! URL: {url}")