FROM python:3.9.6-slim-bullseye as base

ARG SERVICE_WORKDIR=/opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVICE_WORKDIR=${SERVICE_WORKDIR}

FROM base as compile

ARG PYTHON_VENV=/opt/.venv

RUN apt-get update \
     && apt-get install -y netcat-traditional gettext libpq-dev python-dev

COPY ./src/requirements.txt /requirements.txt

RUN python -m venv "${PYTHON_VENV}" \
    && "${PYTHON_VENV}/bin/python" -m pip install --no-cache-dir --upgrade pip \
    && "${PYTHON_VENV}/bin/pip" install --no-cache-dir -r /requirements.txt

ENV PATH="${PYTHON_VENV}/bin:${PATH}"

WORKDIR ${SERVICE_WORKDIR}

FROM compile as safe_user

ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}

RUN groupadd --gid ${GID} user \
      && useradd --uid ${UID} --gid user --shell /bin/bash --create-home user

COPY ./src/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT  [ "/entrypoint.sh" ]

EXPOSE 8000

RUN chown ${UID}:${GID} -R ${SERVICE_WORKDIR}
USER user

# Local stage
FROM safe_user as local

# Server stage
FROM safe_user as server
COPY ./src/ .

