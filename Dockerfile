FROM python:3.10.11-alpine

RUN pip install \
  --no-cache-dir \
  praw=="7.7.0" \
  pushover-complete=="1.1.1" \
  toml=='0.10.2'

COPY reddify.py /app/

WORKDIR /app

CMD ["/usr/local/bin/python", "reddify.py"]
