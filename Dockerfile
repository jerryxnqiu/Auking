# To use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye


# To set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# To set the working directory
WORKDIR /auking
EXPOSE 8000


# To install system dependencies
RUN apt-get update \
    && apt-get install -y \
        redis-tools \
        python3-venv \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential \
        supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update \
    && python -m venv /venv

# To activate virtual environment
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /auking/entrypoint.sh

ENTRYPOINT [ "/auking/entrypoint.sh" ]
