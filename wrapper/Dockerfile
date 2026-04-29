FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Hermes source will be mounted at /opt/hermes-agent
# Its venv site-packages will be added to PYTHONPATH
ENV PYTHONPATH="/opt/hermes-agent:/opt/hermes-agent/venv/lib/python3.11/site-packages"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
