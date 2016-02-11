import os
import pecan

from celery import Celery
from celery.signals import worker_init
from ceph_installer import models


@worker_init.connect
def bootstrap_pecan(signal, sender):
    try:
        config_path = os.environ['PECAN_CONFIG']
    except KeyError:
        here = os.path.abspath(os.path.dirname(__file__))
        # XXX this will not hold true when installing as a binary
        config_path = os.path.abspath(os.path.join(here, '../config/config.py'))

    pecan.configuration.set_config(config_path, overwrite=True)
    # Once configuration is set we need to initialize the models so that we can connect
    # to the DB wth a configured mapper.
    models.init_model()


app = Celery('ceph_installer.async', broker='amqp://guest@localhost//', include=['ceph_installer.tasks'])
