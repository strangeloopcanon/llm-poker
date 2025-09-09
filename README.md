# llm_poker

A minimal Texas Hold’em environment that seats multiple LLM-based players (via the `llm` library) and manages everything from dealing hole cards to forced blinds, betting rounds, and a straightforward showdown.

Core features:
- Blinds: Each hand posts small and big blinds to seed the pot.
- Betting: Each LLM is queried once per betting round to return strict JSON (`fold`, `call`, or `raise`).
- Local showdown: The environment evaluates best 5-of-7 hands and awards the pot.
- JSON validation: LLM responses are parsed/validated; invalid responses trigger a retry.
- CLI: `llm_poker` can run multiple rounds with specified models.

-----

## Installation

1. Install the package:
   ```bash
   pip install llm-poker
   ```

2. Configure the `llm` library with API keys for the models you plan to use (e.g., OpenAI, Anthropic):
   ```bash
   llm keys set openai
   ```

-----

## Quickstart

1) Run the included script
```bash
python run.py
```
Runs 5 rounds among four players: gpt-5, claude-4-sonnet, gemini-2.5-pro, deepseek-reasoner.
Uses `elimination_count=0` so the game runs all rounds unless someone busts.
Default minimum raise is 500 chips; blinds 50/100.

2) Use the CLI
- Four-player example (like `run.py`):
  ```bash
  llm_poker --models "gpt-5 claude-4-sonnet gemini-2.5-pro deepseek-reasoner" \
            --rounds 5 --elimination-count 0 --stack 10000
  ```
- Heads-up example:
  ```bash
  llm_poker -m "gpt-5 claude-4-sonnet" -r 5
  ```
- Include a human player:
  ```bash
  llm_poker -m "gpt-5" -h -r 3
  ```

Once installed, you have access to:

```bash
llm_poker [OPTIONS]
```
Options:
- `--models, -m`: Space-separated model names or aliases recognized by `llm` (default: `"gpt-5"`).
- `--rounds, -r`: Number of hands to deal (default: `3`).
- `--elimination-count, -e`: Stop once only this many players remain (default: `1`).
- `--stack, -s`: Starting chip stack (default: `10000`).
- `--human-player, -h`: Include a local interactive human player.

-----

## Known Limitations
- No side pots: Currently, if a player goes all-in, the environment doesn’t handle side pots.
- Manual environment checks: If the LLM returns “check” while facing a bet, the code interprets it as invalid and re-prompts.
- Fictitious ‘expert-level poker AI’: The LLM’s strategic brilliance is not guaranteed. This is more a demonstration environment than a truly advanced solver.

