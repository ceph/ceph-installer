import os
import pecan

from celery import Celery
from celery.signals import worker_init


@worker_init.connect
def bootstrap_pecan(signal, sender):
    try:
        config_path = os.environ['PECAN_CONFIG']
    except KeyError:
        here = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.abspath(os.path.join(here, '../config/config.py'))

    pecan.configuration.set_config(config_path, overwrite=True)


app = Celery('mariner.async', broker='amqp://guest@localhost//', include=['mariner.tasks'])
