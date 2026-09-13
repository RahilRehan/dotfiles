.PHONY: install stow brew lint help ai-sync micro-plugin

install: ## Full install (packages + stow + shell setup)
	bash install.sh

ai-sync: ## Generate MCP configs from ai/mcp/servers.json
	bash ai/bin/ai-sync

micro-plugin: ## Install the Micro preview plugin
	micro -plugin install preview

stow: ## Re-stow all packages
	@for package in zsh starship git bat mise micro; do \
		stow --restow --target="$$HOME" "$$package"; \
		echo "ok $$package"; \
	done

brew: ## Install/update Homebrew packages
	brew bundle --file=Brewfile

unstow: ## Remove all symlinks (reverse stow)
	@for package in zsh starship git bat mise micro; do \
		stow --delete --target="$$HOME" "$$package" 2>/dev/null; \
		echo "removed $$package"; \
	done

lint: ## Validate shell configs
	@echo "Checking zsh syntax..."
	@for f in zsh/.config/zsh/*.zsh; do zsh -n "$$f" && echo "ok $$f"; done
	@zsh -n zsh/.zshrc && echo "ok zsh/.zshrc"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
