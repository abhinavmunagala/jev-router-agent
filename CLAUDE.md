# Jev Router Agent — AI Task Router with TypeSafe

This project uses Jev (TypeSafe's System One model) to recommend optimal model paths for tasks based on their routing requirements.

## Quick Start

```bash
# Make it executable (one-time)
chmod +x ./model-route

# Route a task
./model-route "your task description"
```

**Example:**
```bash
./model-route "Refactor a React component to use hooks"
```

## Configuration

**API Key:** Set in `~/.bashrc` or environment:

```bash
export TYPESAFE_API_KEY="your-key-here"
```

Or use `OPENROUTER_API_KEY` if available. The script automatically detects and uses whichever is set.

## Model Routing Workflow

Use Jev to recommend whether a task should go to:
- **routine_model**: localized, reversible work with clear requirements and low impact if wrong
- **reasoning_model**: ambiguous, cross-cutting, architecture-sensitive, or high-impact work

### Using the model-route Command

Simply invoke with your task:

```bash
curl -X POST https://openrouter.ai/api/alpha/decisions \
  -H "Authorization: Bearer ${TYPESAFE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "~typesafe/jev-latest",
    "state": {
      "task": "Your task description here",
      "routing_policy": "prefer the least expensive capable path"
    },
    "questions": {
      "route": {
        "type": "choice",
        "instructions": "Which destination should receive this task?",
        "criteria": {
          "routine_model": "localized, reversible work with clear requirements and low impact if wrong",
          "reasoning_model": "ambiguous, cross-cutting, architecture-sensitive, or high-impact work"
        }
      },
      "difficulty": {
        "type": "score",
        "instructions": "How much connected reasoning does this task require?",
        "levels": [
          "mechanical or obvious",
          "requires several connected judgments",
          "requires deep, cross-cutting reasoning"
        ]
      }
    }
  }'
```

### Interpret the Response

The response contains:
- `answers.route.choice`: The recommended destination (routine_model or reasoning_model)
- `answers.route.confidence`: How decisively the probabilities support the choice
- `answers.difficulty.score`: Task position on the difficulty scale (0-2)
- `answers.difficulty.confidence`: Strength of the difficulty assessment

## Example: Refactoring a React Component

**Task:** "Refactor a React component to use hooks instead of class syntax"

Expected routing:
- **route**: `routine_model` (clear, reversible change with test coverage)
- **difficulty**: ~0-1 (mechanical transformation with some judgment)

## Understanding the Output

The routing report shows:

**Routing Decision:**
- **Selected Path**: Which model type is recommended (routine_model or reasoning_model)
- **Confidence**: How certain Jev is (0-100%)
- **Probabilities**: Distribution across options

**Task Complexity:**
- **Difficulty Score**: 0=mechanical, 1=moderate, 2=deep reasoning required
- **Confidence**: Strength of this assessment

**Interpretation:**
Clear explanations of why the task routes to the selected path.

## Examples

### Routine Task → Lightweight Model
```bash
./model-route "Fix a JSON serialization bug when emoji are in the bio field"
# → routine_model (99% confidence, difficulty 0.56/2)
```

### Complex Task → Reasoning Model  
```bash
./model-route "Design auth system with OAuth, SAML, SOC 2 compliance, decoupled from monolith"
# → reasoning_model (100% confidence, difficulty 1.98/2)
```

## API Reference

The script uses:
- **OpenRouter** if TYPESAFE_API_KEY contains `YOUR-KEY-HERE` prefix
- **TypeSafe** otherwise
- Model: `~typesafe/jev-latest` (via OpenRouter)

Cost: ~$0.000019 per request

## Building with Jev Directly

For more advanced use cases, read the TypeSafe documentation:

```bash
/typesafe:typesafe-ai
```

Or inspect `model-route.py` for the API structure and adapt for custom workflows.
