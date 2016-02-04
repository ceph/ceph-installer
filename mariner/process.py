import tempfile
import logging
from mariner.util import api_endpoint, which, get_playbook_path

logger = logging.getLogger(__name__)


def make_ansible_command(stderr, stdout, hosts_file, identifier, extra_vars='{}', tags=''):
    """
    This utility will compose the command needed to run ansible, capture its
    stdout and stderr to a file
    """
    playbook = get_playbook_path()
    ansible_path = which('ansible-playbook')
    url = api_endpoint('tasks', identifier, 'completed')
    command = '{ansible_path} -i {hosts_file} --extra-vars="{extra_vars}" --tags="{tags}" {playbook}'.format(
            ansible_path=ansible_path,
            hosts_file=hosts_file,
            extra_vars=extra_vars,
            tags=tags,
            playbook=playbook
    )

    redirect = '> {stdout} 2> {stderr};'.format(stdout=stdout, stderr=stderr)
    post = 'curl -X POST {url}'.format(url=url)
    return "{command} {redirect} {post}".format(command=command, redirect=redirect, post=post)


def temp_file(identifier, std):
    return tempfile.NamedTemporaryFile(
        prefix="{identifier}_{std}".format(
            identifier=identifier, std=std), delete=False
    ).name
