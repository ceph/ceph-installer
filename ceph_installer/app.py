import os
from pecan import make_app
from ceph_installer import models, process
from ceph_installer.util import mkdir


def ensure_ssh_keys():
    """
    This helper is mostly duplicated from the ``/setup/key`` controller, it
    exists here so that ssh keys can be ensure as early as possible to avoid
    race conditions because ssh-keygen might take a bit too long to complete.
    It is safe to keep the duplication on ``/setup/key`` so that it can still
    ensure keys if that ever happens. This version of the helper does not use
    logging because it is too early in running the application and no logging
    has been configured yet.
    """
    # look for the ssh key of the current user
    private_key_path = os.path.expanduser('~/.ssh/id_rsa')
    public_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')
    ssh_dir = os.path.dirname(public_key_path)

    if not os.path.isdir(ssh_dir):
        mkdir(ssh_dir)

    # if there isn't one create it
    if not os.path.exists(public_key_path):
        # create one
        command = [
                'ssh-keygen', '-q', '-t', 'rsa',
                '-N', '',
                '-f', private_key_path,
        ]
        out, err, code = process.run(command, send_input='y\n')
        if code != 0:
            raise RuntimeError('ssh-keygen failed: %s %s' % (out, err))


def setup_app(config):
    ensure_ssh_keys()
    models.init_model()
    app_conf = dict(config.app)

    return make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )
