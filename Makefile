SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help token check remove-token

CLAUDE ?= claude

# Load CLAUDE_CODE_OAUTH_TOKEN from .env if present (gitignored)
-include .env
export CLAUDE_CODE_OAUTH_TOKEN

help: ## Show available commands
	@grep -hE '^[a-z-]+:.*## ' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN{FS=":.*## "}{printf "  make \033[36m%-13s\033[0m %s\n",$$1,$$2}'

token: ## Create a token (browser login) and save it to .env
	@log=$$(mktemp); trap 'rm -f "$$log"' EXIT; \
	  script -qec "stty cols 2000 2>/dev/null; $(CLAUDE) setup-token" "$$log" || exit $$?; \
	  t=$$(sed -E 's/\x1b\[[0-9;?]*m//g; s/\x1b\[[0-9;?]*[A-Za-z]/\n/g' "$$log" | tr -d '\r' \
	    | grep -oE 'sk-ant-oat01-[A-Za-z0-9_-]+' | tail -1); \
	  if [ -z "$$t" ]; then echo "Could not read the token. Put it in .env as CLAUDE_CODE_OAUTH_TOKEN=<token>"; exit 1; fi; \
	  umask 077; printf 'CLAUDE_CODE_OAUTH_TOKEN=%s\n' "$$t" > .env; \
	  echo "Token saved to .env. Now run: make check"

check: ## Test that the saved token works (PASS/FAIL)
	@uv run python test_claude_token.py

remove-token: ## Delete the saved token (.env)
	@if [ -e .env ]; then rm -f .env && echo "Removed .env"; else echo "No saved token"; fi
