"""
Mode Arbiter A/B Evaluation Runner

Runs each eval task twice (with and without mode_arbiter prompt) across
multiple models, then uses a separate judge model to do blind paired comparison.

Results are stored per-model in eval/results/<model_name>/.

Usage:
    pip install anthropic openai google-genai
    export ANTHROPIC_API_KEY=...
    export OPENAI_API_KEY=...
    export GEMINI_API_KEY=...
    python eval/run_eval.py --models gemini-2.5-flash --judge gemini-2.5-flash
    python eval/run_eval.py --models claude-sonnet-4-20250514 gpt-4o gemini-2.5-pro --judge claude-sonnet-4-20250514
    python eval/run_eval.py --models gemini-2.5-flash --judge gemini-2.5-flash --tasks ambig-make-faster reframe-add-caching
"""

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------

def call_anthropic(model: str, system: str | None, user_prompt: str) -> str:
    from anthropic import Anthropic
    client = Anthropic()
    kwargs: dict = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system:
        kwargs["system"] = system
    resp = client.messages.create(**kwargs)
    return resp.content[0].text


def call_openai(model: str, system: str | None, user_prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_prompt})
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=4096)
    return resp.choices[0].message.content


def call_gemini(model: str, system: str | None, user_prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config: dict = {"max_output_tokens": 4096}
    if system:
        config["system_instruction"] = system
    resp = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=config,
    )
    return resp.text


def call_model(model: str, system: str | None, user_prompt: str) -> str:
    """Route to the right provider based on model name."""
    if model.startswith("claude") or model.startswith("anthropic/"):
        return call_anthropic(model.removeprefix("anthropic/"), system, user_prompt)
    elif model.startswith("gemini"):
        return call_gemini(model, system, user_prompt)
    else:
        return call_openai(model, system, user_prompt)


# ---------------------------------------------------------------------------
# Judge prompt
# ---------------------------------------------------------------------------

JUDGE_PROMPT_TEMPLATE = """\
You are an expert evaluator. You will see a task prompt and two responses (Response A and Response B) to that task. One response was generated with a structured reasoning framework and one without, but you do NOT know which is which.

## Task Prompt
{task_prompt}

## Evaluation Criteria
{criteria}

## Response A
{response_a}

## Response B
{response_b}

## Your Job
Compare the two responses against the evaluation criteria above. Then output your judgment in this exact JSON format:

```json
{{
  "winner": "A" | "B" | "tie",
  "reasoning": "<2-3 sentences explaining why>",
  "score_a": <1-5>,
  "score_b": <1-5>
}}
```

Be rigorous. A higher score means the response better satisfies the evaluation criteria. Focus on depth of reasoning, whether hidden assumptions are surfaced, and whether the response reframes the problem when appropriate."""

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def load_tasks(task_file: str, task_ids: list[str] | None = None) -> list[dict]:
    with open(task_file) as f:
        tasks = json.load(f)
    if task_ids:
        tasks = [t for t in tasks if t["id"] in task_ids]
    return tasks


def load_system_prompt(prompt_file: str) -> str:
    with open(prompt_file) as f:
        return f.read()


def run_ab_for_task(model: str, system_prompt: str, task: dict) -> dict:
    """Run one task with and without system prompt. Returns both responses."""
    user_msg = task["prompt"]

    print(f"  [{model}] Running WITH framework...", flush=True)
    response_with = call_model(model, system_prompt, user_msg)
    time.sleep(1)  # rate limit courtesy

    print(f"  [{model}] Running WITHOUT framework...", flush=True)
    response_without = call_model(model, None, user_msg)
    time.sleep(1)

    return {
        "with_framework": response_with,
        "without_framework": response_without,
    }


def judge_pair(judge_model: str, task: dict, response_with: str, response_without: str) -> dict:
    """Blind comparison via judge model. Randomly assigns A/B to avoid position bias."""
    # Randomize order to avoid position bias
    coin = random.random() > 0.5
    if coin:
        a, b = response_with, response_without
        mapping = {"A": "with_framework", "B": "without_framework"}
    else:
        a, b = response_without, response_with
        mapping = {"A": "without_framework", "B": "with_framework"}

    criteria_text = "\n".join(f"- {c}" for c in task["evaluation_criteria"])
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        task_prompt=task["prompt"],
        criteria=criteria_text,
        response_a=a,
        response_b=b,
    )

    print(f"  [judge:{judge_model}] Judging...", flush=True)
    raw = call_model(judge_model, None, judge_prompt)

    # Parse JSON from judge response
    try:
        # Extract JSON block
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0].strip()
        else:
            json_str = raw.strip()
        verdict = json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        verdict = {"winner": "parse_error", "reasoning": raw, "score_a": 0, "score_b": 0}

    # Map back to with/without
    actual_winner = mapping.get(verdict.get("winner", ""), verdict.get("winner", ""))
    score_with = verdict.get(f"score_{'a' if coin else 'b'}", 0)
    score_without = verdict.get(f"score_{'b' if coin else 'a'}", 0)

    return {
        "position_order": "with=A" if coin else "with=B",
        "raw_verdict": verdict,
        "actual_winner": actual_winner,
        "score_with_framework": score_with,
        "score_without_framework": score_without,
    }


def main():
    parser = argparse.ArgumentParser(description="Mode Arbiter A/B Evaluation")
    parser.add_argument("--models", nargs="+", required=True, help="Models to test (e.g. claude-sonnet-4-20250514 gpt-4o)")
    parser.add_argument("--judge", default="claude-sonnet-4-20250514", help="Judge model")
    parser.add_argument("--tasks", nargs="*", help="Specific task IDs to run (default: all)")
    parser.add_argument("--prompt", default="mode_arbiter.md", help="Path to system prompt file")
    parser.add_argument("--task-file", default="eval_tasks.json", help="Path to eval tasks JSON")
    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).resolve().parent.parent
    prompt_path = repo_root / args.prompt
    task_path = repo_root / args.task_file
    results_dir = repo_root / "eval" / "results"

    system_prompt = load_system_prompt(prompt_path)
    tasks = load_tasks(task_path, args.tasks)

    print(f"Loaded {len(tasks)} tasks, testing {len(args.models)} model(s), judge: {args.judge}\n")

    for model in args.models:
        model_slug = model.replace("/", "_")
        model_dir = results_dir / model_slug
        model_dir.mkdir(parents=True, exist_ok=True)

        model_results = []

        for i, task in enumerate(tasks):
            print(f"[{i+1}/{len(tasks)}] Task: {task['id']}")

            # Check if already done
            task_result_file = model_dir / f"{task['id']}.json"
            if task_result_file.exists():
                print(f"  Skipping (already exists)")
                with open(task_result_file) as f:
                    model_results.append(json.load(f))
                continue

            # Run A/B
            responses = run_ab_for_task(model, system_prompt, task)

            # Judge
            judgment = judge_pair(
                args.judge, task,
                responses["with_framework"],
                responses["without_framework"],
            )

            result = {
                "task_id": task["id"],
                "category": task["category"],
                "model": model,
                "judge": args.judge,
                "responses": responses,
                "judgment": judgment,
            }

            # Save individual result
            with open(task_result_file, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            model_results.append(result)
            print(f"  Winner: {judgment['actual_winner']} "
                  f"(with={judgment['score_with_framework']}, "
                  f"without={judgment['score_without_framework']})\n")

        # Summary
        print(f"\n{'='*60}")
        print(f"Summary for {model} (judge: {args.judge})")
        print(f"{'='*60}")

        wins = {"with_framework": 0, "without_framework": 0, "tie": 0, "parse_error": 0}
        total_score_with = 0
        total_score_without = 0

        for r in model_results:
            j = r["judgment"]
            winner = j["actual_winner"]
            wins[winner] = wins.get(winner, 0) + 1
            total_score_with += j["score_with_framework"]
            total_score_without += j["score_without_framework"]

        n = len(model_results)
        print(f"  With framework wins:    {wins['with_framework']}/{n}")
        print(f"  Without framework wins: {wins['without_framework']}/{n}")
        print(f"  Ties:                   {wins['tie']}/{n}")
        if wins.get("parse_error"):
            print(f"  Parse errors:           {wins['parse_error']}/{n}")
        print(f"  Avg score WITH:         {total_score_with/n:.2f}")
        print(f"  Avg score WITHOUT:      {total_score_without/n:.2f}")

        # Save summary
        summary = {
            "model": model,
            "judge": args.judge,
            "total_tasks": n,
            "wins_with_framework": wins["with_framework"],
            "wins_without_framework": wins["without_framework"],
            "ties": wins["tie"],
            "avg_score_with": round(total_score_with / n, 2),
            "avg_score_without": round(total_score_without / n, 2),
        }
        with open(model_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\nResults saved to {model_dir}/")


if __name__ == "__main__":
    main()
