FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV OPENAI_API_KEY "YOUR_OPENAI_API_KEY"

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN alembic upgrade head

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
