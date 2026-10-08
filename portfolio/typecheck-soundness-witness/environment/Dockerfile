FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
WORKDIR /app
COPY language.py checker.py interpreter.py evaluate.py LANGUAGE.md witness.json /app/
RUN useradd --create-home --uid 1000 agent && chown -R agent:agent /app && mkdir -p /tests /solution && chmod 700 /tests && chmod 755 /solution
USER agent
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
