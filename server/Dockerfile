FROM python:3.10.0

WORKDIR /app

COPY pyproject.toml .
COPY ./src ./src
RUN pip3 install .

CMD [ "python3", "./src/socket_messenger/main.py" ]