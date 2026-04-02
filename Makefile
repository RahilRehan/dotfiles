.PHONY: install stow brew test clean

install: ## Full install (packages + stow + shell setup)
	bash install.sh

stow: ## Re-stow all packages
	@for dir in */; do \
		dir=$${dir%/}; \
		case "$$dir" in .git|docs|iterm2) continue ;; esac; \
		stow --restow --target="$$HOME" "$$dir"; \
		echo "ok $$dir"; \
	done

brew: ## Install/update Homebrew packages
	brew bundle --file=Brewfile

test: ## Build and run Docker test container
	docker build -t dotfiles-test .
	docker run -it --rm dotfiles-test

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

clean: ## Remove Docker test image
	docker rmi dotfiles-test 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
