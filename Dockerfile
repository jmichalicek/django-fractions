FROM python:3.8.5-buster AS dev
LABEL maintainer="Justin Michalicek <jmichalicek@gmail.com>"
ENV PYTHONUNBUFFERED 1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
  inotify-tools \
  software-properties-common \
  sudo \
  vim \
  telnet \
  postgresql-client \
  && apt-get autoremove && apt-get clean

RUN pip install pip==20.2.2
RUN useradd -ms /bin/bash -d /django django && echo "django ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER django
ENV HOME=/django PATH=/django/bash-shell.net/.venv/bin:/django/.local/bin:$PATH LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8
EXPOSE 8000
