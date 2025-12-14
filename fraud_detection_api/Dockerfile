FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all project files (Python, HTML, shell script, docs)
COPY . /app

# Install required Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard] networkx neo4j

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
