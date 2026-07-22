FROM python:3.14-slim-trixie
RUN apt update && apt install -y wget
# wget is needed for the healthcheck

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD ["CMD-SHELL", "wget -qO- http://localhost:8000 | grep -q '^Hello World$' || exit 1"]

CMD ["fastapi", "run"]
