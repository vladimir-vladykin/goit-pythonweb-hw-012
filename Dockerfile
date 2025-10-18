FROM python:3.13
RUN pip install poetry

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .
RUN poetry install

EXPOSE 8000
CMD ["poetry", "run", "python",  "main.py"]