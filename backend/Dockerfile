FROM python:3.12-slim

WORKDIR /app

# Dependencies only at build time — embedding weights download on first use at runtime
# (previously downloading here broke CI: disk/time limits on GitHub-hosted runners)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
