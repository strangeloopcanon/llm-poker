# README.md
# llm_poker

A minimal Texas Hold’em environment that seats multiple **LLM-based players** (via the `llm` library) and manages everything from dealing hole cards to forced blinds, betting rounds, and a straightforward showdown.  

**Core features**:  
- **Blinds**: Each hand forces a small blind and a big blind, ensuring there’s money in the pot.  
- **Betting**: We query each LLM once per betting round, requesting an action in strict JSON form (`fold`, `call`, or `raise`).  
- **Local showdown logic**: The environment determines the best 5-card hand from each player’s 7 cards and awards the pot.  
- **Pydantic-based JSON validation**: The LLM responses are parsed and validated. If invalid, we retry.  
- **Optional CLI**: The `llm_poker` command can run multiple rounds using the specified LLMs.

-----

## Installation

1. **Install** the package:
   ```bash
   pip install llm_poker
   ```

You must also configure your llm library with the API keys for whichever LLM models you plan to use (e.g., gpt-4o, Anthropic, etc.). For example:

```bash
llm keys set openai
```

-----

## Quickstart Examples
1. Just run run.py
```bash
python run.py
```
Deals up to 5 rounds between multiple players: gpt-5, claude-4-sonnet, gemini-2.5-pro, deepseek-reasoner.
Uses elimination_count=0 so the game does not stop early (unless someone busts).
The minimum raise is 500 chips.
Logs each hand’s actions, culminating in a final standings table.

2. Using the CLI
If you installed with the included console script, you can do:

```bash
llm_poker --models "gpt-5 claude-4-sonnet gemini-2.5-pro deepseek-reasoner" --elimination-count 0 --stack 10000

```
This deals 5 rounds of heads-up between gpt-5 and claude-4-sonnet.


Once installed, you have access to:

```bash
llm_poker [OPTIONS]
```
--models/-m: Multiple model names or aliases recognized by llm (defaults to "gpt-5").
--rounds/-r: How many hands to deal (default 3).
--elimination-count/-e: Stop once only this many players remain (default 1).
--stack/-s: Starting chip stack (default 10000).

-----

## Known Limitations
- No side pots: Currently, if a player goes all-in, the environment doesn’t handle side pots.
- Manual environment checks: If the LLM returns “check” while facing a bet, the code interprets it as invalid and re-prompts.
- Fictitious ‘expert-level poker AI’: The LLM’s strategic brilliance is not guaranteed. This is more a demonstration environment than a truly advanced solver.
