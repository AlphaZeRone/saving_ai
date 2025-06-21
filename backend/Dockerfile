<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

COPY src/ ./src
ENV PYTHONPATH=/app/src

=======
FROM python:3.11-slim

WORKDIR /app

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

COPY src/ ./src
ENV PYTHONPATH=/app/src

>>>>>>> 6563e49b59a03e0d73e2c4d2cec9abdc482d5ba5
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]