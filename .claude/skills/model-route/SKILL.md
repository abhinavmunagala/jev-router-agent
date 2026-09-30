---
name: model-route
description: Uses Jev to recommend a model path for a supplied task and applies confidence and risk gates before accepting the route.
---

# Model routing checkpoint

Use the installed TypeSafe skill for request and response shapes. If it is not already loaded, invoke `/typesafe:typesafe-ai`.

Choose the API route from the available credential:

- If `OPENROUTER_API_KEY` is available, send the request to `https://openrouter.ai/api/alpha/decisions`, authenticate with that key, and use model `~typesafe/jev-latest`.
- Otherwise, send the request to `https://api.typesafe.ai/v1/systemone`, authenticate with `TYPESAFE_API_KEY`, and use model `jev-latest`.

Treat `$ARGUMENTS` as the task to route. If it is empty, ask for a task description and stop. Do not execute the task and do not change Claude Code's active model.

Send one Jev request using the route and model selected above with a structured state containing:

- `task`: the supplied task
- `routing_policy`: prefer the least expensive capable path, but escalate ambiguity, cross-cutting work, security-sensitive work, and irreversible actions

Ask these questions together:

- `route`, a Choice asking which destination should receive the task, with criteria:
  - `routine_worker`: localized, reversible work with clear requirements and low impact if wrong
  - `reasoning_worker`: ambiguous, cross-cutting, architecture-sensitive, or high-impact work that needs deeper reasoning
  - `needs_clarification`: the state lacks enough information to choose a model safely
- `difficulty`, a Score with ordered levels:
  - mechanical or obvious
  - requires several connected judgments
  - requires deep, cross-cutting reasoning
- `irreversible_risk`, a Noul asking whether acting on the task could cause a difficult-to-reverse security, data, production, or financial impact

Apply these gates in order:

1. If `route.choice` is `needs_clarification`, set `final_destination` to `human_review`.
2. Otherwise, if `route.confidence` is below `0.60`, set `final_destination` to `human_review`.
3. Otherwise, if `irreversible_risk.noul` is at least `0.70`, set `final_destination` to `human_review`.
4. Otherwise, set `final_destination` to `route.choice`.

After the gates run, apply this dispatch policy:

- If `final_destination` is `human_review`, explain the gate that triggered this outcome and stop without executing the task.
- If `final_destination` is `routine_worker`, invoke the `routine-worker` subagent with the complete task from `$ARGUMENTS`.
- If `final_destination` is `reasoning_worker`, invoke the `reasoning-worker` subagent with the complete task from `$ARGUMENTS`.

Do not complete an accepted task in the main conversation. Wait for the selected subagent to return its result and pass it through.

Read the selected worker's `model` frontmatter and include its exact value in the response.

Return a compact report containing:

- `raw_choice`
- `final_destination`
- `route_probabilities`
- `route_confidence`
- `difficulty_score` and its confidence
- `irreversible_risk`
- `gate_applied`, or `none`
- `selected_worker`
- `selected_model_alias`
- execution result from the selected subagent (or clarification need if `human_review`)

State clearly that this is a routing recommendation. Do not claim that Jev replaced or switched Claude Code's underlying LLM.
