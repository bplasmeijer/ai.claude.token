# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A single-file, stdlib-only Python smoke test that verifies a long-lived Claude Code OAuth token (from `claude setup-token`, see https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) can authenticate the `claude` CLI non-interactively.

## Commands

Uses `uv` (no dependencies; `pyproject.toml` sets `package = false`) driven by the `Makefile`:

```bash
make token         # runs `claude setup-token`, saves the token to .env (mode 600)
make check         # uv run python test_claude_token.py: PASS/FAIL, exit 0 ok / 1 auth or run failure / 2 token unset
make remove-token  # deletes .env (doesn't revoke the token)
python3 -m unittest -v test_claude_token   # unittest form; skips if the token is unset
```

`make token` runs `setup-token` under `script` (so the browser flow keeps a TTY, with `stty cols 2000` so the token isn't line-wrapped). It removes ANSI codes from the log and greps for `sk-ant-oat01-...`. Set `CLAUDE=/path/to/fake` to test it without a real login. The Makefile loads `.env` in Make syntax (`CLAUDE_CODE_OAUTH_TOKEN=...`, no quotes or `export`). An exported variable or `make check CLAUDE_CODE_OAUTH_TOKEN=...` also works. Requires `claude` on PATH.

## How the test isolates the token

`run_claude()` in `test_claude_token.py` shells out to `claude -p ... --output-format json` and parses the JSON (`is_error`, `result`). Two things make sure a pass really means the token is valid. Keep both if you change it:

- It removes env vars that outrank `CLAUDE_CODE_OAUTH_TOKEN` in Claude Code's auth precedence (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_PROFILE`, `CLAUDE_CODE_USE_*`).
- It sets `CLAUDE_CONFIG_DIR` to an empty temp dir, so stored `/login` credentials, settings, and `apiKeyHelper` in `~/.claude` can't act as a fallback.

Don't add `--bare`: bare mode doesn't read `CLAUDE_CODE_OAUTH_TOKEN`.
