from click.testing import CliRunner


def test_simulate_poker_game_final_standings_no_play(capsys):
    # Avoid creating LLM players entirely; use only human player and skip play
    from llm_poker.environment import simulate_poker_game

    simulate_poker_game(
        model_names=[],
        rounds=1,
        elimination_count=1,  # alive <= elimination_count, so no hand played
        starting_stack=1000,
        human_player=True,
    )

    out = capsys.readouterr().out
    assert "FINAL STANDINGS" in out


def test_cli_runs_without_play(monkeypatch):
    # Monkeypatch simulate_poker_game to avoid creating LLM models
    from llm_poker import cli

    captured = {"called": False}

    def fake_simulate_poker_game(**kwargs):
        captured["called"] = True
        print("\n=== FINAL STANDINGS ===\n1. Dummy (Human): $1000")

    monkeypatch.setattr(cli, "simulate_poker_game", fake_simulate_poker_game)

    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            "--models",
            "gpt-5",  # value ignored by fake simulate
            "--rounds",
            "1",
            "--elimination-count",
            "1",
            "--stack",
            "1000",
            "--human-player",
        ],
    )
    assert result.exit_code == 0
    assert captured["called"] is True
    assert "FINAL STANDINGS" in result.output
