FROM python:3.6-slim

LABEL maintainer=jakejrc
LABEL description=DataViz Lab - Data visualization teaching system

WORKDIR /app

RUN pip install --no-cache-dir \
    flask==1.1.4 \
    numpy==1.18.5 \
    pandas==1.1.5 \
    matplotlib==3.3.4 \
    seaborn==0.11.1 \
    wordcloud==1.8.1 \
    jinja2==2.11.3

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

CMD [python, app.py]
