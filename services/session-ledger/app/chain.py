from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client
from app.schemas import SessionSummaryOutput, SessionLedgerRequest

load_dotenv()

client = Client()
prompt_template = client.pull_prompt("session-ledger-prompt")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash",
    temperature=0.1,
    max_retries=5
)

structured_llm = llm.with_structured_output(SessionSummaryOutput)

ledger_chain = prompt_template | structured_llm

def run_session_ledger(payload: SessionLedgerRequest) -> SessionSummaryOutput:
    return ledger_chain.invoke({
        "campaign_name": payload.campaign_name,
        "game_system": payload.game_system,
        "raw_notes": payload.raw_notes
    })