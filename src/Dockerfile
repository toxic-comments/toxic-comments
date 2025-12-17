FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/* && \
    groupadd --system devops && useradd --system app

WORKDIR /toxic-comments-app
COPY --chown=app . .
RUN pip install --no-cache-dir -r requirements.txt

USER app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "./entrypoint.sh"]