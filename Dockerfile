FROM jupyter/datascience-notebook:latest as jupyter

ENV JUPYTER_ENABLE_LAB=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=false

RUN pip install \
    jupyter-dash \
    jupyter-lsp \
    plotly \
    python-language-server[all]

RUN jupyter labextension install \
    @aquirdturtle/collapsible_headings \
    @ijmbarr/jupyterlab_spellchecker \
    @jupyter-widgets/jupyterlab-manager \
    @krassowski/jupyterlab-lsp \
    jupyterlab-plotly \
    plotlywidget


FROM python:3.10 as poetry

ENV MYPY_CACHE_DIR=/tmp/mypy-cache \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN mkdir /tmp/mypy-cache && pip install poetry


FROM poetry as build

ADD . /project

WORKDIR /project

RUN poetry install \
    --no-ansi \
    --no-interaction \
    --no-root \
    && poetry build \
    --format wheel \
    && pip install dist/*.whl \
    && mypy --install-types --non-interactive \
    && pytest


FROM jupyter as install

WORKDIR /home/jovyan/work

COPY --from=build /project/dist .

RUN pip install *.whl
