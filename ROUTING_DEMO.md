# Routing Demo

Routine routing succeeded.

## Routing Trade-offs

| Factor | Favors routine_model | Favors reasoning_model |
|---|---|---|
| Speed | Low latency for clear, localized work | Slower, justified when a wrong answer costs more than the wait |
| Cost | Cheapest capable path (matches the routing policy) | Higher per-task cost, worth it for ambiguous or cross-cutting work |
| Reversibility | Edits that git or a re-run can undo | Irreversible or hard-to-undo actions |
| Security | No credentials, permissions, or external side effects | Secrets, auth, data access, or anything touching shared systems |

Speed and cost push toward the routine path. Reversibility and security are
constraints, not preferences: when they conflict with speed or cost, they win.

## Policy: Stop Before Destructive Commands

The router's recommendation selects a model. It never authorizes an action.
The agent must stop and get explicit user confirmation before running a command
that is destructive, irreversible, or has effects outside the working tree,
regardless of route, confidence, or difficulty score. Examples:

- Deleting or overwriting data: `rm -rf`, `git reset --hard`, `git clean`,
  force-push, dropping tables, truncating files.
- Changing shared state: pushing, publishing, deploying, modifying CI or
  permissions, sending messages.
- Handling secrets: printing, moving, or transmitting API keys or credentials.

Additional rules:

1. A `routine_model` route, even at high confidence, does not waive this stop.
2. Low route confidence, or a route and difficulty score that disagree, means
   escalate to `reasoning_model` or ask the user, not proceed.
3. Confirmation covers the specific command shown. It does not carry over to
   later or broader commands.
4. If the destructive step cannot be made reversible (backup, branch, dry run),
   say so in the confirmation request.
