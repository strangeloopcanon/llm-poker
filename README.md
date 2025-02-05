# README.md
# llm-poker

A minimal Texas Hold’em environment that seats multiple **LLM-based players** (via the `llm` library) and manages everything from dealing hole cards to forced blinds, betting rounds, and a straightforward showdown.  

**Core features**:  
- **Blinds**: Each hand forces a small blind and a big blind, ensuring there’s money in the pot.  
- **Betting**: We query each LLM once per betting round, requesting an action in strict JSON form (`fold`, `call`, or `raise`).  
- **Local showdown logic**: The environment determines the best 5-card hand from each player’s 7 cards and awards the pot.  
- **Pydantic-based JSON validation**: The LLM responses are parsed and validated. If invalid, we retry.  
- **Optional CLI**: The `poker-eval` command can run multiple rounds using the specified LLMs.

-----

## Installation

1. **Clone** this repository or download the files.
2. **Install** the package (in editable mode) from the project root (where `setup.py` is located):
   ```bash
   pip install -e .
   ```
3. **Verify** You should see llm-poker installed
   ```bash
   pip list | grep llm-poker
   ```
You must also configure your llm library with the API keys for whichever LLM models you plan to use (e.g., gpt-4o, Anthropic, etc.). For example:

```bash
llm keys set openai
```

-----

## Quickstart Examples
1. Running the Sample run.py
```bash
python run.py
```
Deals up to 5 rounds between multiple players: gpt-4o, claude-3-5-haiku-latest, claude-3-5-sonnet-latest, deepseek-chat.
Uses elimination_count=0 so the game does not stop early (unless someone busts).
The minimum raise is 500 chips.
Logs each hand’s actions, culminating in a final standings table.

2. Using the CLI
If you installed with the included console script, you can do:

```bash
poker-eval --models gpt-4o --models claude-3-5-haiku-latest --rounds 5
```
This deals 5 rounds of heads-up between gpt-4o and claude-3-5-haiku-latest.


Once installed, you have access to:

```bash
poker-eval [OPTIONS]
```
--models/-m: Multiple model names or aliases recognized by llm (defaults to ["gpt-4o"]).
--rounds/-r: How many hands to deal (default 3).
--elimination-count/-e: Stop once only this many players remain (default 1).
--stack/-s: Starting chip stack (default 10000).

-----

## Known Limitations
- No side pots: Currently, if a player goes all-in, the environment doesn’t handle side pots.
- Manual environment checks: If the LLM returns “check” while facing a bet, the code interprets it as invalid and re-prompts.
- Fictitious ‘expert-level poker AI’: The LLM’s strategic brilliance is not guaranteed. This is more a demonstration environment than a truly advanced solver.