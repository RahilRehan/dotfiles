FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG DELTA_VERSION=0.19.2
ARG LAZYGIT_VERSION=0.60.0
ARG YAZI_VERSION=v26.1.22

RUN apt-get update && apt-get install -y \
    sudo curl git zsh stow locales unzip \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

# Starship prompt (Phase 1)
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y

# Delta diff pager (Phase 2)
RUN ARCH=$(dpkg --print-architecture) \
    && curl -fsSL "https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION}_${ARCH}.deb" \
       -o /tmp/delta.deb \
    && dpkg -i /tmp/delta.deb && rm /tmp/delta.deb

# Phase 3-5, 8: apt-installable tools (batched for fewer layers)
# Phase 11 extras (dust, duf, just, etc.) are macOS/Homebrew only — not critical for testing
RUN apt-get update && apt-get install -y \
    bat eza zoxide fzf fd-find tmux direnv \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/batcat /usr/local/bin/bat \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd

# Phase 6: lazygit (not in Ubuntu repos, install from GitHub release)
RUN ARCH=$(dpkg --print-architecture) \
    && LG_ARCH=$([ "$ARCH" = "amd64" ] && echo "x86_64" || echo "$ARCH") \
    && curl -fsSL "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_${LG_ARCH}.tar.gz" \
       -o /tmp/lazygit.tar.gz \
    && tar xzf /tmp/lazygit.tar.gz -C /tmp lazygit \
    && install /tmp/lazygit /usr/local/bin/ && rm /tmp/lazygit /tmp/lazygit.tar.gz

# Phase 7: yazi file manager + optional preview deps
RUN apt-get update && apt-get install -y --no-install-recommends file jq ripgrep \
    && rm -rf /var/lib/apt/lists/*
RUN ARCH=$(dpkg --print-architecture) \
    && YZ_ARCH=$([ "$ARCH" = "amd64" ] && echo "x86_64" || echo "aarch64") \
    && curl -fsSL "https://github.com/sxyazi/yazi/releases/download/${YAZI_VERSION}/yazi-${YZ_ARCH}-unknown-linux-gnu.zip" \
       -o /tmp/yazi.zip \
    && unzip -o /tmp/yazi.zip -d /tmp/yazi \
    && install /tmp/yazi/yazi-${YZ_ARCH}-unknown-linux-gnu/yazi /usr/local/bin/ \
    && install /tmp/yazi/yazi-${YZ_ARCH}-unknown-linux-gnu/ya /usr/local/bin/ \
    && rm -rf /tmp/yazi /tmp/yazi.zip

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

RUN useradd -m -s /bin/zsh testuser \
    && echo "testuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER testuser

# Atuin (Phase 4) — install as testuser so it goes to ~/.atuin/bin
RUN curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh
ENV PATH="/home/testuser/.atuin/bin:${PATH}"

# mise (Phase 8) — install as testuser so it goes to ~/.local/bin
RUN curl https://mise.run | sh
ENV PATH="/home/testuser/.local/bin:${PATH}"
WORKDIR /home/testuser

COPY --chown=testuser:testuser . /home/testuser/dotfiles

RUN cd /home/testuser/dotfiles && bash install.sh

CMD ["zsh", "-il"]
