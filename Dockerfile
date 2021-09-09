FROM tiangolo/uvicorn-gunicorn:python3.7

ENV PYTHONUNBUFFERED 1
ENV APP_MODULE be_volumetria.main:app

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.1.7 && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY src ./

EXPOSE 80 8000 8888 
