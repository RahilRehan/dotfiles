.PHONY: install stow brew lint help ai-sync

install: ## Full install (packages + stow + shell setup)
	bash install.sh

ai-sync: ## Sync MCP configs and stow ai package
	bash ai/bin/ai-sync
	@for rel in .cursor/mcp.json .claude/mcp.json .pi/agent/mcp.json; do \
		[ -f "$$HOME/$$rel" ] && [ ! -L "$$HOME/$$rel" ] && rm "$$HOME/$$rel"; \
	done
	stow --restow --target="$$HOME" ai

stow: ## Re-stow all packages
	@for dir in */; do \
		dir=$${dir%/}; \
		case "$$dir" in .git|docs|iterm2) continue ;; esac; \
		stow --restow --target="$$HOME" "$$dir"; \
		echo "ok $$dir"; \
	done

brew: ## Install/update Homebrew packages
	brew bundle --file=Brewfile

unstow: ## Remove all symlinks (reverse stow)
	@for dir in */; do \
		dir=$${dir%/}; \
		case "$$dir" in .git|docs|iterm2) continue ;; esac; \
		stow --delete --target="$$HOME" "$$dir" 2>/dev/null; \
		echo "removed $$dir"; \
	done

lint: ## Validate shell configs
	@echo "Checking zsh syntax..."
	@for f in zsh/.config/zsh/*.zsh; do zsh -n "$$f" && echo "ok $$f"; done
	@zsh -n zsh/.zshrc && echo "ok zsh/.zshrc"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
