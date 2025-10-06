FROM ghcr.io/home-assistant/devcontainer:supervisor

USER vscode

COPY requirements.txt ./
COPY package_constraints.txt ./
RUN uv pip install -r requirements.txt

# Useful runtime env for better logs and asyncio debugging
ENV PYTHONUNBUFFERED=1 \
    PYTHONASYNCIODEBUG=1