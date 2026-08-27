import os
from dotenv import load_dotenv
from langsmith import Client, evaluate
from app.chain import run_session_ledger
from app.schemas import SessionLedgerRequest

load_dotenv()
client = Client()

DATASET_NAME = "session-ledger-benchmark-v2"

# ---------------------------------------------------------
# 1. Comprehensive Benchmark Dataset (5 Diverse Cases)
# ---------------------------------------------------------
benchmark_data = [
    # Case 1: Standard Fantasy Narrative
    {
        "inputs": {
            "campaign_name": "Curse of the Sunken Spire",
            "game_system": "D&D 5e",
            "raw_notes": "Party met Eldon the Mage in Riverwood. Eldon gave them the Amulet of Dawn. They traveled north to the Weeping Caves and killed 2 Goblins. Eldon warned that Lord Morvath is seeking the amulet."
        },
        "outputs": {
            "expected_entities": ["Eldon", "Riverwood", "Amulet of Dawn", "Weeping Caves", "Lord Morvath"]
        }
    },
    # Case 2: Sci-Fi / Cyberpunk Shorthand
    {
        "inputs": {
            "campaign_name": "Neon Syndicate",
            "game_system": "Cyberpunk",
            "raw_notes": "Fixer named Vex contacted crew @ Club Neon. Infiltrate Arasaka Tower sub-level 4 -> steal Quantum Deck. Ambushed by Chrome Skulls gang on exit. Netrunner jacked out with 1 HP."
        },
        "outputs": {
            "expected_entities": ["Vex", "Club Neon", "Arasaka Tower", "Quantum Deck", "Chrome Skulls"]
        }
    },
    # Case 3: Horror / Investigation with Fragmented GM Notes
    {
        "inputs": {
            "campaign_name": "Whispers in the Dark",
            "game_system": "Call of Cthulhu",
            "raw_notes": "Investigated Blackwood Sanatorium. Met Dr. Henry Morris. Found a torn page from the Necronomicon inside office drawer. Cult of the Red Moon spotted outside the cemetery."
        },
        "outputs": {
            "expected_entities": ["Blackwood Sanatorium", "Dr. Henry Morris", "Necronomicon", "Cult of the Red Moon"]
        }
    },
    # Case 4: Disambiguation / Negation Test
    {
        "inputs": {
            "campaign_name": "Kingdoms of Iron",
            "game_system": "Tormenta20",
            "raw_notes": "Party decided NOT to travel to Valkaria. Instead went south to the Whispering Woods. Met the blacksmith Torvald at the Iron Forge. Bought 3 smoke grenades. Guild of Shadows watched them from the roof."
        },
        "outputs": {
            "expected_entities": ["Whispering Woods", "Torvald", "Iron Forge", "Guild of Shadows"]
        }
    },
    # Case 5: Minimal Notes (Negative Control / Hallucination Check)
    {
        "inputs": {
            "campaign_name": "Lost Caverns",
            "game_system": "D&D 5e",
            "raw_notes": "Short session: Party rested at the Silver Horseshoe Inn in Oakhaven. Spoke with Bartender Silas. No combat occurred."
        },
        "outputs": {
            "expected_entities": ["Silver Horseshoe Inn", "Oakhaven", "Silas"]
        }
    }
]

def setup_dataset():
    """Uploads benchmark examples ensuring the dataset contains rows."""
    if not client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Creating dataset '{DATASET_NAME}'...")
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Comprehensive benchmark suite for TTRPG session extraction."
        )
        for entry in benchmark_data:
            client.create_example(
                inputs=entry["inputs"],
                outputs=entry["outputs"],
                dataset_id=dataset.id
            )
        print("Dataset populated with 5 benchmark cases!")
    else:
        print(f"Dataset '{DATASET_NAME}' already exists. Reusing it.")

# ---------------------------------------------------------
# 2. Target Pipeline Adapter
# ---------------------------------------------------------
def target_pipeline(inputs: dict) -> dict:
    request_obj = SessionLedgerRequest(**inputs)
    result = run_session_ledger(request_obj)
    return result.model_dump()

# ---------------------------------------------------------
# 3. Custom Evaluators
# ---------------------------------------------------------
def evaluate_entity_recall(run, example) -> dict:
    """Measures the proportion of expected entities successfully captured."""
    expected_entities = example.outputs.get("expected_entities", [])
    extracted_entities = [
        item["name"].lower() for item in run.outputs.get("extracted_entities", [])
    ]
    
    if not expected_entities:
        return {"key": "entity_recall", "score": 1.0}

    hits = sum(
        1 for exp in expected_entities 
        if any(exp.lower() in ext for ext in extracted_entities)
    )
    recall_score = hits / len(expected_entities)
    return {"key": "entity_recall", "score": recall_score}

def evaluate_completeness(run, example) -> dict:
    """Verifies that all primary output fields are non-empty."""
    has_title = bool(run.outputs.get("title"))
    has_events = len(run.outputs.get("key_events", [])) > 0
    has_entities = len(run.outputs.get("extracted_entities", [])) > 0
    
    passed = has_title and has_events and has_entities
    return {"key": "completeness", "score": 1 if passed else 0}

# ---------------------------------------------------------
# 4. Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    setup_dataset()
    print("Executing evaluation experiment across 5 benchmark cases...")
    
    experiment_results = evaluate(
        target_pipeline,
        data=DATASET_NAME,
        evaluators=[evaluate_entity_recall, evaluate_completeness],
        experiment_prefix="session-ledger-v2-eval"
    )
    
    print("\nEvaluation complete! Check the scorecard in LangSmith.")