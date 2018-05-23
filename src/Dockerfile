FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev build-essential

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /rest/requirements.txt

WORKDIR /rest

RUN pip install -r requirements.txt

COPY . /rest

ENTRYPOINT [ "python" ]

CMD [ "rest.py" ]