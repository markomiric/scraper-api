# FROM public.ecr.aws/sam/build-python3.13:latest
FROM ubuntu:22.04 AS builder

LABEL maintainer="Marko Miric"
LABEL description="Development environment with Python 3.13, Poetry 1.8.5 and Node.js 18"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common curl git build-essential && \
    add-apt-repository ppa:deadsnakes/ppa && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-venv python3.13-dev nodejs && \
    curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.5 python3.13 - && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

RUN useradd -m -s /bin/bash appuser

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

WORKDIR /app
USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["bash"]