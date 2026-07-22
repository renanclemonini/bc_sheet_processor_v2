FROM python:3.13.14-alpine3.24

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

ARG USERNAME=bcsheetprocessor
ENV POETRY_VERSION=2.4.1 \
    PATH="/home/${USERNAME}/.local/bin:$PATH"

RUN apk add curl=8.21.0-r0 su-exec \
    --no-cache && \
    rm -rf /var/cache/apk/* && \
    adduser -s /bin/ash -D ${USERNAME}

USER ${USERNAME}

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /home/${USERNAME}

COPY --chown=${USERNAME}:${USERNAME} pyproject.toml poetry.lock ./
RUN poetry install \
    --no-root \
    --no-ansi

COPY --chown=${USERNAME}:${USERNAME} . .

# Cria diretórios necessários
RUN mkdir -p uploads output templates/img

# Sobe para root para entrypoint poder corrigir permissões dos volumes
USER root
COPY --chown=${USERNAME}:${USERNAME} entrypoint.sh /entrypoint.sh
RUN sed -i "s/__USERNAME__/${USERNAME}/g" /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Expõe a porta (Render usa variável PORT)
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]