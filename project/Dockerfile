FROM python:3.12-slim

WORKDIR /app

ENV PORT=8080
ENV WARDROBE_DIR=/app/roupinhas
ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY project/server.py /app/project/server.py
COPY project/public /app/project/public
COPY scripts /app/scripts

EXPOSE 8080

CMD ["python", "project/server.py"]
