FROM ghcr.io/home-assistant/devcontainer:supervisor

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Useful runtime env for better logs and asyncio debugging
ENV PYTHONUNBUFFERED=1 \
    PYTHONASYNCIODEBUG=1