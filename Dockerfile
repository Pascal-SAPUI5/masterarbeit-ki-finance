FROM python:3.10-slim

WORKDIR /app

# System-Abhängigkeiten mit Chrome/Chromium Support
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    # Chrome/Chromium Dependencies
    chromium \
    chromium-driver \
    # Virtual Display for Headless Operation
    xvfb \
    x11-utils \
    x11-xserver-utils \
    # Additional Dependencies for Browser Automation
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Configure pip for better SSL handling and retries
RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org download.pytorch.org" && \
    pip config set global.timeout 120 && \
    pip config set global.retries 5

# Install aiohttp for HTTP server
RUN pip install --upgrade pip && \
    pip install aiohttp

# Browser automation environment variables
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu --headless --remote-debugging-port=9222"

# Python-Abhängigkeiten with retry mechanism
COPY requirements.txt constraints.txt ./
# Install PyTorch CPU version first to avoid downloading GPU version
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.1.0+cpu torchvision==0.16.0+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --no-cache-dir -c constraints.txt -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir -c constraints.txt -r requirements.txt) || \
    (sleep 10 && pip install --no-cache-dir --index-url https://pypi.org/simple -c constraints.txt -r requirements.txt)

# Anwendungscode
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p /app/.claude_memory /app/research/q1-sources /app/output /app/writing/chapters /app/browser_data /app/cookies

# Copy and setup comprehensive entrypoint script
COPY scripts/docker_entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Port
EXPOSE 3000

# Starte MCP Server mit HTTP wrapper und Browser Support
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "mcp_server_http.py"]