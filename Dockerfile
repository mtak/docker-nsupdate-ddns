FROM python:alpine AS base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-build
RUN pip install pipenv

COPY Pipfile .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --python /usr/local/bin/python

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-build /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN mkdir /app
WORKDIR /app
COPY . /app/

ENTRYPOINT ["/app/main.py"]
