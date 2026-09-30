#!/usr/bin/env python3
"""
Model Route: Use Jev to recommend optimal model paths for tasks.

Usage:
    python model-route.py "your task description"
"""

import sys
import os
import json
import requests
from typing import Optional, Dict, Any

def get_api_credentials() -> tuple[str, str]:
    """Determine which API to use and get credentials."""
    typesafe_key = os.getenv("TYPESAFE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    # Prefer TYPESAFE_API_KEY if it's an OpenRouter key (sk-or-v1-* format)
    if typesafe_key and typesafe_key.startswith("sk-or-v1-"):
        return "openrouter", typesafe_key
    elif typesafe_key:
        return "typesafe", typesafe_key
    elif openrouter_key:
        return "openrouter", openrouter_key
    else:
        raise ValueError(
            "No API key found. Set either OPENROUTER_API_KEY or TYPESAFE_API_KEY"
        )

def route_task(task: str) -> Dict[str, Any]:
    """Send task to Jev for routing recommendation."""
    api_type, api_key = get_api_credentials()

    if api_type == "openrouter":
        return _route_via_openrouter(task, api_key)
    else:
        return _route_via_typesafe(task, api_key)

def _route_via_openrouter(task: str, api_key: str) -> Dict[str, Any]:
    """Send routing request to OpenRouter."""
    url = "https://openrouter.ai/api/alpha/decisions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "~typesafe/jev-latest",
        "state": {
            "task": task,
            "routing_policy": "prefer the least expensive capable path"
        },
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "Which destination should receive this task?",
                "criteria": {
                    "routine_model": "localized, reversible work with clear requirements and low impact if wrong",
                    "reasoning_model": "ambiguous, cross-cutting, architecture-sensitive, or high-impact work that needs deeper reasoning"
                }
            },
            "difficulty": {
                "type": "score",
                "instructions": "How much connected reasoning does this task require?",
                "criteria": [
                    "mechanical or obvious",
                    "requires several connected judgments",
                    "requires deep, cross-cutting reasoning"
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def _route_via_typesafe(task: str, api_key: str) -> Dict[str, Any]:
    """Send routing request to TypeSafe API."""
    url = "https://api.typesafe.ai/v1/systemone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "jev-latest",
        "state": {
            "task": task,
            "routing_policy": "prefer the least expensive capable path"
        },
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "Which destination should receive this task?",
                "criteria": {
                    "routine_model": "localized, reversible work with clear requirements and low impact if wrong",
                    "reasoning_model": "ambiguous, cross-cutting, architecture-sensitive, or high-impact work that needs deeper reasoning"
                }
            },
            "difficulty": {
                "type": "score",
                "instructions": "How much connected reasoning does this task require?",
                "criteria": [
                    "mechanical or obvious",
                    "requires several connected judgments",
                    "requires deep, cross-cutting reasoning"
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def format_report(response: Dict[str, Any], task: str) -> str:
    """Format the Jev response as a readable report."""
    try:
        answers = response.get("answers", {})
        route_answer = answers.get("route", {})
        difficulty_answer = answers.get("difficulty", {})

        choice = route_answer.get("choice", "unknown")
        route_confidence = route_answer.get("confidence", 0)
        difficulty_score = difficulty_answer.get("score", -1)
        difficulty_confidence = difficulty_answer.get("confidence", 0)

        # Extract probabilities if available
        route_probs = route_answer.get("probabilities", route_answer.get("choice_distribution", {}))

        report = f"""
╔════════════════════════════════════════════════════════════╗
║          TASK ROUTING RECOMMENDATION (via Jev)             ║
╚════════════════════════════════════════════════════════════╝

Task: {task}

ROUTING DECISION
────────────────
Selected Path: {choice.upper()}
Confidence:   {route_confidence * 100:.1f}%

Route Breakdown:
  • routine_model:  {route_probs.get('routine_model', 0):.1%}
  • reasoning_model: {route_probs.get('reasoning_model', 0):.1%}

TASK COMPLEXITY
───────────────
Difficulty Score: {difficulty_score}/2
  (0=mechanical, 1=moderate, 2=deep reasoning required)
Confidence:       {difficulty_confidence * 100:.1f}%

INTERPRETATION
──────────────
"""

        if choice == "routine_model":
            report += """This task is well-suited for a lightweight, efficient model.
• Clear requirements with low risk
• Localized, reversible changes
• Standard patterns and well-known solutions
"""
        else:
            report += """This task requires deeper reasoning capabilities.
• Ambiguous requirements or cross-cutting concerns
• Architecture-sensitive decisions
• High impact if done incorrectly
• Complex tradeoffs to evaluate
"""

        report += f"""
API USAGE
─────────
Provider:      {response.get('provider', 'Unknown')}
Input Tokens:  {response.get('usage', {}).get('input_tokens', 'N/A')}
Output Tokens: {response.get('usage', {}).get('output_tokens', 'N/A')}
Cost:          ${response.get('usage', {}).get('cost', 0):.6f}
Request ID:    {response.get('id', 'N/A')}

═══════════════════════════════════════════════════════════════

Note: This is a routing recommendation. Jev analyzes task
characteristics to suggest an optimal path. The recommendation
does not replace or change Claude Code's underlying LLM.
"""

        return report
    except Exception as e:
        return f"Error formatting report: {e}\n\nRaw response:\n{json.dumps(response, indent=2)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python model-route.py \"your task description\"")
        print("\nExample:")
        print('  python model-route.py "Refactor a React component to use hooks"')
        sys.exit(1)

    task = " ".join(sys.argv[1:])

    try:
        print("🔄 Sending task to Jev for routing analysis...")
        response = route_task(task)
        report = format_report(response, task)
        print(report)
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
