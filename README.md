# README.md

# Game-Evals: Texas Hold’em with LLM Players

This repository hosts a minimal Texas Hold’em environment, with LLM-driven players, plus robust JSON parsing logic and straightforward or advanced showdown logic. You can run multi-hand simulations where two or more LLMs compete and produce valid moves.

## Project Structure

**Key files:**

1. **`environment.py`**  
   - Defines `PokerTable` (the environment).  
   - Manages blinds, dealing, betting, and the final showdown.  
   - Exports `simulate_poker_game(...)` as a convenience function.

2. **`llm_player.py`**  
   - A specialized player that queries an LLM for moves.  
   - Uses pydantic or similar validation for JSON responses.  
   - Has a built-in retry loop for malformed JSON or invalid actions.

3. **`run.py`**  
   - A sample driver script that configures logging and calls `simulate_poker_game`.

---

## Installation

1. **Clone or download** this repository.
2. **Activate** the virtual environment of your choice, or ensure you’re in a Python environment where you want to install the package.
3. From **the root folder** (where `setup.py` is), run:
   ```bash
   pip install -e .
   ```

If you plan to use the optional CLI (poker-eval ...), ensure cli.py is referenced in setup.py under the entry_points. Then you can do:
   ```bash
poker-eval --help
   ```


Example usage
-------------
Create a short script or interactive session:
```python
from poker_eval.game import simulate_poker_game

simulate_poker_game(
    model_names=["gpt-4o", "o1-pro", "claude-3.5-sonnet"],
    rounds=3,
    elimination_count=1
)
```

Check that you have configured your LLM keys properly using the llm CLI.

## Configuration
LLM Keys: You must configure your LLM provider keys for the llm library (e.g. Anthropic, OpenAI).
Example:
```bash
export OPENAI_API_KEY="sk-xxx"
llm keys set openai
or similarly for Anthropic.
```
Model Names: You can pass any recognized model alias from llm.models (e.g. gpt-4o, claude-3-5-haiku-latest).

Then just
```python
python run.py
```