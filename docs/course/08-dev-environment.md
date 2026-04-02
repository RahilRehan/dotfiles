# Lesson 08 — Dev Environment

## mise — One Tool for All Runtimes

mise replaces nvm (Node), pyenv (Python), rbenv (Ruby), goenv (Go), tfenv (Terraform), and dozens more. One tool, one config format, automatic version switching when you `cd`.

### Global Defaults

```bash
bat ~/.config/mise/config.toml
```

Expected output:

```toml
[tools]
node = "lts"
python = "3.12"
```

These versions are available everywhere unless a project overrides them.

Install the global tools:

```bash
mise install
```

> **First run warning:** this downloads and compiles runtimes from source or fetches prebuilt binaries. Node LTS and Python 3.12 together can take **2–5 minutes** on first install depending on your connection and hardware. Subsequent runs are near-instant (already installed).

```bash
mise ls
```

Expected output (versions will vary):

```
Tool    Version         Source                          Requested
node    22.x.x          ~/.config/mise/config.toml      lts
python  3.12.x          ~/.config/mise/config.toml      3.12
```

Verify the tools work:

```bash
node --version
```

```
v22.x.x
```

```bash
python3 --version
```

```
Python 3.12.x
```

### Per-Project Versions

This is where mise shines — automatic version switching per directory.

```bash
cd /tmp && mkdir my-project && cd my-project

mise use node@20
mise use python@3.11
```

Expected output (for each command):

```
mise ~/tmp/my-project/.mise.toml tools: node@20.x.x, python@3.11.x
```

This created a `.mise.toml` in the project:

```bash
bat .mise.toml
```

Expected output:

```toml
[tools]
node = "20"
python = "3.11"
```

### mise trust

When you `cd` into a directory with a `.mise.toml` you didn't create (e.g., after cloning a repo), mise won't activate it automatically. This is a **security feature** — you don't want a random repo silently installing arbitrary tool versions on your machine.

```bash
cd /tmp/my-project

mise trust
```

Expected output:

```
mise trusted ~/tmp/my-project/.mise.toml
```

> **When is trust needed?** In the Docker playground, `mise trust` runs automatically for the global config. Configs you create yourself with `mise use` are trusted implicitly. You only need `mise trust` explicitly when you clone someone else's repo that already has a `.mise.toml`.

Install the project-specific versions:

```bash
mise install
```

> This downloads Node 20 and Python 3.11 if you don't already have them. Same **2–5 minute** wait applies on first install of each new version.

Verify:

```bash
node --version                # v20.x.x
python3 --version             # Python 3.11.x
```

Now leave the project and check again:

```bash
cd /tmp
node --version                # v22.x.x (back to global LTS)
python3 --version             # Python 3.12.x (back to global)
```

mise switches versions automatically based on your current directory. No manual `nvm use` or `pyenv local` needed.

### Common Commands

```bash
mise ls                       # list installed tool versions
mise ls --current             # show what's active in current directory
mise use node@22              # pin node 22 for current project
mise install                  # install everything in .mise.toml
mise outdated                 # check for newer versions
mise upgrade                  # upgrade tools to latest matching versions
mise ls-remote node           # see all available Node versions
```

### Compatibility

mise reads `.tool-versions` (asdf format) and `.nvmrc` / `.node-version` / `.python-version` files. If your team uses asdf, mise works as a drop-in replacement — no config changes needed.

## direnv — Per-Directory Environment Variables

direnv automatically loads and unloads environment variables when you `cd` into/out of a directory.

### Try It

```bash
cd /tmp && mkdir api-project && cd api-project

echo 'export DATABASE_URL="postgres://localhost:5432/mydb"' > .envrc
echo 'export NODE_ENV="development"' >> .envrc
```

direnv blocks untrusted `.envrc` files immediately:

```
direnv: error /tmp/api-project/.envrc is blocked. Run `direnv allow` to approve.
```

Approve it:

```bash
direnv allow
```

Expected output:

```
direnv: loading /tmp/api-project/.envrc
direnv: export +DATABASE_URL +NODE_ENV
```

Now the variables are loaded:

```bash
echo $DATABASE_URL            # postgres://localhost:5432/mydb
echo $NODE_ENV                # development
```

Leave the directory — variables are unloaded:

```bash
cd /tmp
echo $DATABASE_URL            # (empty)
echo $NODE_ENV                # (empty)
```

Come back — variables are loaded again:

```bash
cd api-project
echo $DATABASE_URL            # postgres://localhost:5432/mydb
```

### Best Practices

```bash
# Always gitignore .envrc (it may contain secrets):
echo ".envrc" >> .gitignore

# Provide a template for the team:
cat > .envrc.example << 'EOF'
# Copy to .envrc and fill in values
export DATABASE_URL="postgres://..."
export API_KEY=""
EOF
```

### Combining mise + direnv

When you `cd` into a project:

1. **mise** activates the correct Node/Python/Go versions (from `.mise.toml`)
2. **direnv** loads environment variables (from `.envrc`)

Zero manual switching. Every developer on the team gets the exact same setup.

## Next

[Lesson 09 — System & Containers →](09-system-and-containers.md)
