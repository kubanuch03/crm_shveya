FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN pip install poetry

RUN poetry install --no-root

EXPOSE 8989

CMD ["bash", "entrypoint.sh"]