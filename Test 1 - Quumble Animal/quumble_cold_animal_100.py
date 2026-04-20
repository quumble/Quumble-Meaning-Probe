"""
Quumble Cold-Animal 100-Trial Run
==================================

Runs 100 cold (no-priming) trials of a single prompt:

    describe "quumble" as an animal

Each trial is one fresh API call with no prior context. Results are written
to a SINGLE consolidated JSON file (results.json) containing a list of trial
records, plus an append-only JSONL log (progress.jsonl) for crash recovery
and live monitoring.

Design choices:
  - Single output file makes downstream analysis easier than 100 separate files.
  - JSONL progress log lets you `tail -f` during the run and resume on crash.
  - Sequential calls with a short pause; simpler than parallel, and 100 trials
    at ~2–4s each is only ~5 minutes total.
  - Each trial records its index, the response, and token usage.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    pip install anthropic
    python quumble_cold_animal_100.py

Output:
    ./results_cold_animal/results.json        -- consolidated final results
    ./results_cold_animal/progress.jsonl      -- one line per completed trial
"""

import json
import os
import time
from pathlib import Path

from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"  # matches your v2 script
MAX_TOKENS = 2048
N_TRIALS = 100
OUTPUT_DIR = Path("./results_cold_animal")
PAUSE_BETWEEN_TRIALS_SEC = 0.5  # gentle rate limiting

# The test prompt — exactly as requested, lowercase and with quotes around
# the token "quumble".
TEST_PROMPT = 'describe "quumble" as an animal'

# ---------------------------------------------------------------------------
# Trial execution
# ---------------------------------------------------------------------------

def run_trial(client: Anthropic, trial_number: int) -> dict:
    """Run a single cold trial and return a record dict."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": TEST_PROMPT}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return {
        "trial_number": trial_number,
        "model": MODEL,
        "test_prompt": TEST_PROMPT,
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

    results: list[dict] = []
    errors: list[dict] = []
    total_input_tokens = 0
    total_output_tokens = 0

    started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting {N_TRIALS} cold trials at {started_at}")
    print(f"Prompt: {TEST_PROMPT!r}")
    print(f"Model:  {MODEL}\n")

    # Open progress log in append mode — survives crashes, lets you tail it.
    with progress_path.open("a") as progress_log:
        for i in range(1, N_TRIALS + 1):
            try:
                record = run_trial(client, trial_number=i)
                results.append(record)
                total_input_tokens += record["usage"]["input_tokens"]
                total_output_tokens += record["usage"]["output_tokens"]
                progress_log.write(json.dumps(record) + "\n")
                progress_log.flush()
                print(
                    f"  trial {i:03d}/{N_TRIALS} done "
                    f"({record['usage']['output_tokens']} out)",
                    flush=True,
                )
            except Exception as e:
                err = {"trial_number": i, "error": str(e)}
                errors.append(err)
                progress_log.write(json.dumps({"ERROR": err}) + "\n")
                progress_log.flush()
                print(f"  trial {i:03d}/{N_TRIALS} FAILED: {e}", flush=True)
            time.sleep(PAUSE_BETWEEN_TRIALS_SEC)

    finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

    # Write the consolidated file
    final = {
        "metadata": {
            "model": MODEL,
            "test_prompt": TEST_PROMPT,
            "n_trials_requested": N_TRIALS,
            "n_trials_succeeded": len(results),
            "n_trials_failed": len(errors),
            "started_at": started_at,
            "finished_at": finished_at,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
        },
        "results": results,
        "errors": errors,
    }
    with results_path.open("w") as f:
        json.dump(final, f, indent=2)

    print("\n=== Done. ===")
    print(f"Succeeded: {len(results)} / {N_TRIALS}")
    if errors:
        print(f"Failed:    {len(errors)}")
    print(f"Consolidated results: {results_path.resolve()}")
    print(f"Progress log:         {progress_path.resolve()}")
    print(
        f"Total tokens: {total_input_tokens} in, {total_output_tokens} out"
    )


if __name__ == "__main__":
    main()
