FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# install python iterpreter and package manager
RUN apt-get update && apt-get install -y python3.14 python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src .

CMD ["python3", "client_main.py"]
