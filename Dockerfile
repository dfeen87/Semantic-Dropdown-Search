FROM python:3.12.11-slim-bookworm

RUN apt-get update \
    && apt-get install --yes --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 developer

WORKDIR /repro
COPY --chown=developer:developer . /repro

VOLUME ["/repro"]
USER developer
ENTRYPOINT ["make"]
