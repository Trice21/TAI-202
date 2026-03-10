FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic email-validator python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv aiofiles

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]