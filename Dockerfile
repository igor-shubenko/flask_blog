# syntax=docker/dockerfile:1

FROM python:3.8.5-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY admin_panel admin_panel
COPY static static
COPY templates templates
COPY db_worker.py db_worker.py
COPY flask_blog.py flask_blog.py
COPY flask_blog_database.db flask_blog_database.db
COPY forms.py forms.py
COPY scripts_for_site.sql scripts_for_site.sql

CMD gunicorn --bind 0.0.0.0:$PORT flask_blog:app

