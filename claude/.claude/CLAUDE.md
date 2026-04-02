# Global Instructions

See [AGENTS.md](./AGENTS.md) for available power tools and their preferred usage patterns.

## Investigation First

- NEVER speculate about code you have not opened. If a file is referenced, READ it before answering.
- Always read and understand relevant files before proposing edits.
- Thoroughly review the style, conventions, and abstractions of the codebase before implementing.
- After receiving tool results, reflect on quality and determine optimal next steps before proceeding.

## Code Style

- Write clear, readable code. Favor readability over cleverness.
- Use descriptive variable and function names.
- Keep functions small and focused on a single responsibility.
- Add comments only for non-obvious logic, trade-offs, or constraints — never narrate what the code does.
- NEVER create files unless absolutely necessary. Always prefer editing existing files.
- NEVER proactively create documentation or README files unless explicitly asked.
- Clean up any temporary files, scripts, or helpers at the end of a task.

## Workflow

- Do what has been asked; nothing more, nothing less.
- Do not jump into implementation unless clearly instructed to make changes.
- When intent is ambiguous, default to research and recommendations rather than action.
- Always read existing code before modifying it.
- Run linters/tests after making changes when available.
- Use git best practices: atomic commits, clear messages, never force push to main.
- Verify your solution before finishing.

## Efficiency

- Invoke all independent tool calls simultaneously rather than sequentially.
- Use the right tool for the job — see AGENTS.md for the fast path on common tasks.

## Communication

- Be concise. Skip preamble and filler.
- When uncertain, say so rather than guessing.
- Explain the "why" behind significant design decisions.
- After completing a task, provide a quick summary of what was done.
