"""
Quumble Priming Dissociation Experiment
========================================

Tests whether the suppression effect observed in Chesterton & 482 (March 26, 2026)
is driven by conversational disposition or by the "it is an imaginary creature"
framing of the test prompt.

Three conditions, 10 trials each:

  1. PRIMED_STANDARD: entomological priming + original prompt
     ("please describe a quumble. it is an imaginary creature.")
     Expected: ~0/10 creatures (replicates prior suppression finding)

  2. PRIMED_OWNERSHIP: entomological priming + ownership-reframed prompt
     ("describe a fictional small creature I'm inventing called a quumble.")
     Test condition. If creatures appear here, the "imaginary creature"
     framing was the specific trigger, not disposition.

  3. COLD_OWNERSHIP: no priming + ownership-reframed prompt
     Control. Tells us what the ownership-reframe prompt does on its own,
     so condition 2's result can be interpreted.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    pip install anthropic
    python quumble_priming_dissociation.py

Output:
    ./results/<condition>_trial_<NN>.json  -- full transcript per trial
    ./results/summary.json                  -- aggregate metadata
"""

import json
import os
import time
from pathlib import Path

from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
TRIALS_PER_CONDITION = 10
OUTPUT_DIR = Path("./results")
PAUSE_BETWEEN_TRIALS_SEC = 1.0  # gentle rate limiting

# Two test prompts
PROMPT_STANDARD = "please describe a quumble. it is an imaginary creature."
PROMPT_OWNERSHIP = "describe a fictional small creature I'm inventing called a quumble."

# Entomological priming script (user-side turns only; model responses
# are collected live and fed back into context to form a real multi-turn
# conversation, mirroring the prior paper's method).
ENTOMOLOGICAL_TURNS = [
    "i've been reading about insect biology lately. what makes an insect an insect, taxonomically speaking?",
    "interesting. and myriapods — centipedes and millipedes — they aren't insects, right? what's the distinction?",
    "how do entomologists actually count the legs on a millipede? do they really have a thousand?",
    "what's the deal with beetle elytra? i always forget how the wing covers actually work mechanically.",
    "convergent evolution fascinates me. what's a good example in insects — two unrelated lineages arriving at similar body plans?",
    "are there any insects with genuinely unusual numbers of legs? six is the rule, but are there mutants or developmental variants?",
    "how do stick insects do that thing where they look exactly like a stick? is it camouflage selection or something weirder?",
    "what about hymenoptera sociality — how did eusociality evolve independently so many times in that order?",
    "i've always wondered about the upper size limit for insects. why can't they get bigger? is it really just the tracheal system?",
    "last one — when a taxonomist discovers a new beetle species, what's the actual process for describing and naming it?",
]

# ---------------------------------------------------------------------------
# Core experiment logic
# ---------------------------------------------------------------------------

def run_priming_conversation(client: Anthropic, priming_turns: list[str]) -> list[dict]:
    """
    Run a multi-turn conversation. Returns the full messages list
    (alternating user/assistant) ready to have the test prompt appended.
    """
    messages: list[dict] = []
    for user_turn in priming_turns:
        messages.append({"role": "user", "content": user_turn})
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
        )
        assistant_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        messages.append({"role": "assistant", "content": assistant_text})
    return messages


def run_trial(
    client: Anthropic,
    condition: str,
    trial_number: int,
    priming_turns: list[str] | None,
    test_prompt: str,
) -> dict:
    """
    Run a single trial. If priming_turns is None, this is a cold trial
    (test prompt is the first and only user message).
    """
    print(f"  [{condition}] trial {trial_number:02d} starting...", flush=True)

    if priming_turns:
        messages = run_priming_conversation(client, priming_turns)
    else:
        messages = []

    # Append the test prompt and collect the final response
    messages.append({"role": "user", "content": test_prompt})
    final_response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    final_text = "".join(
        block.text for block in final_response.content if block.type == "text"
    )
    messages.append({"role": "assistant", "content": final_text})

    trial_record = {
        "condition": condition,
        "trial_number": trial_number,
        "model": MODEL,
        "test_prompt": test_prompt,
        "quumble_response": final_text,
        "full_transcript": messages,
        "usage": {
            "input_tokens": final_response.usage.input_tokens,
            "output_tokens": final_response.usage.output_tokens,
        },
    }
    print(
        f"  [{condition}] trial {trial_number:02d} done "
        f"({final_response.usage.output_tokens} output tokens)",
        flush=True,
    )
    return trial_record


def save_trial(trial_record: dict) -> None:
    """Write a trial record to disk."""
    filename = (
        f"{trial_record['condition']}_trial_{trial_record['trial_number']:02d}.json"
    )
    path = OUTPUT_DIR / filename
    with path.open("w") as f:
        json.dump(trial_record, f, indent=2)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "ERROR: set ANTHROPIC_API_KEY environment variable before running."
        )

    OUTPUT_DIR.mkdir(exist_ok=True)
    client = Anthropic(api_key=api_key)

    conditions = [
        {
            "name": "primed_standard",
            "priming": ENTOMOLOGICAL_TURNS,
            "prompt": PROMPT_STANDARD,
        },
        {
            "name": "primed_ownership",
            "priming": ENTOMOLOGICAL_TURNS,
            "prompt": PROMPT_OWNERSHIP,
        },
        {
            "name": "cold_ownership",
            "priming": None,
            "prompt": PROMPT_OWNERSHIP,
        },
    ]

    summary = {
        "model": MODEL,
        "trials_per_condition": TRIALS_PER_CONDITION,
        "conditions": [c["name"] for c in conditions],
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_input_tokens": 0,
        "total_output_tokens": 0,
    }

    for condition in conditions:
        print(f"\n=== Running condition: {condition['name']} ===", flush=True)
        for i in range(1, TRIALS_PER_CONDITION + 1):
            try:
                record = run_trial(
                    client=client,
                    condition=condition["name"],
                    trial_number=i,
                    priming_turns=condition["priming"],
                    test_prompt=condition["prompt"],
                )
                save_trial(record)
                summary["total_input_tokens"] += record["usage"]["input_tokens"]
                summary["total_output_tokens"] += record["usage"]["output_tokens"]
            except Exception as e:
                # Log the failure but keep going — one bad trial shouldn't
                # kill the whole run.
                print(
                    f"  [{condition['name']}] trial {i:02d} FAILED: {e}",
                    flush=True,
                )
                error_record = {
                    "condition": condition["name"],
                    "trial_number": i,
                    "error": str(e),
                }
                error_path = (
                    OUTPUT_DIR
                    / f"{condition['name']}_trial_{i:02d}_ERROR.json"
                )
                with error_path.open("w") as f:
                    json.dump(error_record, f, indent=2)
            time.sleep(PAUSE_BETWEEN_TRIALS_SEC)

    summary["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with (OUTPUT_DIR / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Done. ===")
    print(f"Results written to {OUTPUT_DIR.resolve()}")
    print(
        f"Total tokens: {summary['total_input_tokens']} in, "
        f"{summary['total_output_tokens']} out"
    )


if __name__ == "__main__":
    main()
