FROM python:3.12-slim

WORKDIR /app

ENV PORT=8080
ENV WARDROBE_DIR=/app/Roupinhas
ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1

COPY project/server.py /app/server.py
COPY project/public /app/public

EXPOSE 8080

CMD ["python", "server.py"]
