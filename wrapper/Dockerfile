FROM python:3.12-slim

# Install system deps for Hermes installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash git && \
    rm -rf /var/lib/apt/lists/*

# Install Hermes Agent via official script
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Ensure hermes is on PATH
ENV PATH="/root/.local/bin:/root/.hermes/bin:${PATH}"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
