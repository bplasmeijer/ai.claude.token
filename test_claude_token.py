#!/usr/bin/env python3
"""Smoke test: verify a long-lived Claude Code OAuth token works from the CLI.

Generate the token with `claude setup-token`, then:

    export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
    python3 test_claude_token.py            # run as a script
    python3 -m unittest -v test_claude_token  # or via unittest

See https://code.claude.com/docs/en/authentication#generate-a-long-lived-token
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOKEN_VAR = "CLAUDE_CODE_OAUTH_TOKEN"
# Credentials that outrank CLAUDE_CODE_OAUTH_TOKEN in Claude Code's auth
# precedence. Removed so the test exercises the token, not something else.
OVERRIDING_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_PROFILE",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
)
PROMPT = "Reply with exactly the word PONG and nothing else."
TIMEOUT_S = 120


def run_claude(token: str) -> dict:
    """Run `claude -p` authenticated only by `token`; return the JSON result."""
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("`claude` CLI not found on PATH")

    env = {k: v for k, v in os.environ.items() if k not in OVERRIDING_VARS}
    env[TOKEN_VAR] = token
    # Empty config dir: no stored /login credentials, settings, or apiKeyHelper
    # can be used as a fallback, so success proves the token itself works.
    with tempfile.TemporaryDirectory(prefix="claude-token-test-") as cfg:
        env["CLAUDE_CONFIG_DIR"] = cfg
        proc = subprocess.run(
            [claude, "-p", PROMPT, "--output-format", "json"],
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
        )

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"claude exited {proc.returncode} without JSON output.\n"
            f"stdout: {proc.stdout.strip()}\nstderr: {proc.stderr.strip()}"
        )
    result["_returncode"] = proc.returncode
    return result


class TestClaudeOAuthToken(unittest.TestCase):
    def test_token_authenticates(self):
        token = os.environ.get(TOKEN_VAR, "").strip()
        if not token:
            self.skipTest(f"{TOKEN_VAR} is not set (run `claude setup-token`)")

        result = run_claude(token)

        self.assertFalse(
            result.get("is_error"), f"claude reported an error: {result.get('result')}"
        )
        self.assertEqual(result["_returncode"], 0)
        self.assertIn("PONG", result.get("result", "").upper())


def main() -> int:
    token = os.environ.get(TOKEN_VAR, "").strip()
    if not token:
        print(f"FAIL: {TOKEN_VAR} is not set. Run `make token`.")
        return 2
    try:
        result = run_claude(token)
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"FAIL: {e}")
        return 1

    ok = not result.get("is_error") and result["_returncode"] == 0
    print(f"{'PASS' if ok else 'FAIL'}: {result.get('result', '').strip()}")
    if ok and "total_cost_usd" in result:
        print(f"      duration={result.get('duration_ms')}ms "
              f"cost=${result['total_cost_usd']:.4f}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
