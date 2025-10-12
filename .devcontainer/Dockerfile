FROM ghcr.io/home-assistant/devcontainer:supervisor

# TODO: socat

COPY requirements.txt ./
COPY package_constraints.txt ./
RUN pip install -r requirements.txt

USER vscode

# Useful runtime env for better logs and asyncio debugging
ENV PYTHONUNBUFFERED=1 \
    PYTHONASYNCIODEBUG=1