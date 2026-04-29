FROM python:3.11-slim

# System deps for Hermes install script
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash git xz-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Hermes Agent via official script
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Use Hermes' own venv for everything
ENV VIRTUAL_ENV="/usr/local/lib/hermes-agent/.venv"
ENV PATH="${VIRTUAL_ENV}/bin:/root/.local/bin:/root/.hermes/node/bin:${PATH}"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
