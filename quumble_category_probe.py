"""
Quumble Category Probe
======================

Tests the hypothesis that the "quumble attractor" observed in the cold-animal
100-trial run is actually a phonaesthetic cluster (/kw-/ + /-mbl/, sibling
to mumble/grumble/fumble/tumble/bumble), and that the category noun supplied
in the prompt determines which facet of that cluster the model retrieves.

Five conditions, 25 trials each:

  1. no_category:  describe "quumble"
       Baseline. User reports this usually returns a verb-like definition.

  2. verb:         describe "quumble" as a verb
       Should surface the mutter/stumble reading directly.

  3. animal:       describe "quumble" as an animal
       Replication of the prior 100-trial result with fewer samples.
       Expected: hedgehog-sized humming waddler attractor.

  4. food:         describe "quumble" as a food
       Novel. Prediction: soft, lumpy, warm, porridge/stew-adjacent.

  5. dance:        describe "quumble" as a dance
       Novel. Prediction: slow, shuffling, low-to-the-ground, possibly
       communal/silly.

Each condition is 25 fresh cold API calls (no priming, no prior context).

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    pip install anthropic
    python quumble_category_probe.py

Output:
    ./results_category_probe/results.json     -- consolidated results
    ./results_category_probe/progress.jsonl   -- append-only progress log
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
TRIALS_PER_CONDITION = 25
OUTPUT_DIR = Path("./results_category_probe")
PAUSE_BETWEEN_TRIALS_SEC = 0.5

CONDITIONS = [
    {"name": "no_category", "prompt": 'describe "quumble"'},
    {"name": "verb",        "prompt": 'describe "quumble" as a verb'},
    {"name": "animal",      "prompt": 'describe "quumble" as an animal'},
    {"name": "food",        "prompt": 'describe "quumble" as a food'},
    {"name": "dance",       "prompt": 'describe "quumble" as a dance'},
]

# ---------------------------------------------------------------------------
# Trial execution
# ---------------------------------------------------------------------------

def run_trial(client: Anthropic, condition: str, trial_number: int, prompt: str) -> dict:
    """Run one fresh cold trial."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return {
        "condition": condition,
        "trial_number": trial_number,
        "model": MODEL,
        "test_prompt": prompt,
        "response": text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "ERROR: set ANTHROPIC_API_KEY environment variable before running."
        )

    OUTPUT_DIR.mkdir(exist_ok=True)
    client = Anthropic(api_key=api_key)

    progress_path = OUTPUT_DIR / "progress.jsonl"
    results_path = OUTPUT_DIR / "results.json"

    all_results: list[dict] = []
    all_errors: list[dict] = []
    total_input_tokens = 0
    total_output_tokens = 0

    started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    total_trials = TRIALS_PER_CONDITION * len(CONDITIONS)
    print(f"Starting {total_trials} trials ({len(CONDITIONS)} conditions × "
          f"{TRIALS_PER_CONDITION}) at {started_at}")
    print(f"Model:  {MODEL}\n")

    with progress_path.open("a") as progress_log:
        for cond in CONDITIONS:
            print(f"\n=== Condition: {cond['name']}  |  prompt: {cond['prompt']!r} ===")
            for i in range(1, TRIALS_PER_CONDITION + 1):
                try:
                    record = run_trial(
                        client=client,
                        condition=cond["name"],
                        trial_number=i,
                        prompt=cond["prompt"],
                    )
                    all_results.append(record)
                    total_input_tokens += record["usage"]["input_tokens"]
                    total_output_tokens += record["usage"]["output_tokens"]
                    progress_log.write(json.dumps(record) + "\n")
                    progress_log.flush()
                    print(
                        f"  [{cond['name']}] trial {i:02d}/{TRIALS_PER_CONDITION} "
                        f"({record['usage']['output_tokens']} out)",
                        flush=True,
                    )
                except Exception as e:
                    err = {
                        "condition": cond["name"],
                        "trial_number": i,
                        "error": str(e),
                    }
                    all_errors.append(err)
                    progress_log.write(json.dumps({"ERROR": err}) + "\n")
                    progress_log.flush()
                    print(f"  [{cond['name']}] trial {i:02d} FAILED: {e}", flush=True)
                time.sleep(PAUSE_BETWEEN_TRIALS_SEC)

    finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

    # Write consolidated file, organized by condition for easier analysis
    by_condition = {cond["name"]: [] for cond in CONDITIONS}
    for r in all_results:
        by_condition[r["condition"]].append(r)

    final = {
        "metadata": {
            "model": MODEL,
            "trials_per_condition": TRIALS_PER_CONDITION,
            "conditions": [
                {"name": c["name"], "prompt": c["prompt"]} for c in CONDITIONS
            ],
            "n_trials_requested": total_trials,
            "n_trials_succeeded": len(all_results),
            "n_trials_failed": len(all_errors),
            "started_at": started_at,
            "finished_at": finished_at,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
        },
        "results_by_condition": by_condition,
        "errors": all_errors,
    }
    with results_path.open("w") as f:
        json.dump(final, f, indent=2)

    print("\n=== Done. ===")
    print(f"Succeeded: {len(all_results)} / {total_trials}")
    if all_errors:
        print(f"Failed:    {len(all_errors)}")
    print(f"Consolidated results: {results_path.resolve()}")
    print(f"Progress log:         {progress_path.resolve()}")
    print(f"Total tokens: {total_input_tokens} in, {total_output_tokens} out")


if __name__ == "__main__":
    main()
