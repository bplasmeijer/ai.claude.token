# ai.claude.token

Check that a long-lived Claude Code OAuth token works from the command line. Use it before relying on the token in CI pipelines or scripts.

The token comes from `claude setup-token`. See the [Claude Code docs](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token).

## Requirements

- [Claude Code](https://code.claude.com) (`claude` on your PATH)
- A Claude Pro, Max, Ultra, Team or Enterprise plan
- [uv](https://docs.astral.sh/uv/) and `make` on Linux, macOS or WSL

## Usage

```bash
make token          # sign in through the browser; the token is saved to .env
make check          # prints PASS or FAIL
make remove-token   # deletes .env
```

A successful check looks like this:

```
PASS: PONG
      duration=1107ms cost=$0.0279
```

## How it works

`make check` runs `claude -p` and asks Claude to reply "PONG". It tests only the token:

- Credentials that would take priority over the token are removed for the test, such as `ANTHROPIC_API_KEY`.
- Claude runs with an empty, temporary config folder, so your normal `~/.claude` login can't stand in for a bad token.

## Notes

- **Storage:** the token is saved in `.env`, which only you can read and git ignores. Never commit it.
- **Other sources:** you can also export `CLAUDE_CODE_OAUTH_TOKEN` yourself, or pass it as `make check CLAUDE_CODE_OAUTH_TOKEN=...`.
- **Validity:** the token is valid for one year. `make remove-token` deletes only your local copy, so the token keeps working.
- **Limits:** the token can't use Remote Control or claude.ai connectors (local MCP servers still work), and `claude --bare` ignores it; use `ANTHROPIC_API_KEY` there instead.
