FROM python:3.10-slim

WORKDIR /app

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p /app/.claude_memory /app/research/q1-sources /app/output /app/writing/chapters

# Port
EXPOSE 3000

# Starte MCP Server
CMD ["python", "mcp_server_claude.py"]