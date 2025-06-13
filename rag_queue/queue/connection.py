# flake8: noqa

from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(host="valkey"))