from pecan import expose, request, response
from webob.static import FileIter
from mariner.util import make_setup_script
from mariner import process
import os
from StringIO import StringIO


class SetupController(object):

    @expose(content_type='application/octet-stream')
    def index(self):
        script = make_setup_script(request.url)
        response.headers['Content-Disposition'] = 'attachment; filename=setup.sh'
        response.app_iter = FileIter(script)

    @expose(content_type='application/octet-stream')
    def key(self):
        """
        Serves the public SSH key for the user that own the current service
        """
        # look for the ssh key of the current user
        private_key_path = os.path.expanduser('~/.ssh/id_rsa')
        public_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')

        # if there isn't one create it
        if not os.path.exists(public_key_path):
            # create one
            command = [
                    'ssh-keygen', '-q', '-t', 'rsa',
                    '-N', '""',
                    '-f', private_key_path,
            ]
            process.run(command, send_input='y\n')

        # define the file to download
        response.headers['Content-Disposition'] = 'attachment; filename=id_rsa.pub'
        with open(public_key_path) as key_contents:
            key = StringIO()
            key.write(key_contents.read())
            key.seek(0)
        response.app_iter = FileIter(key)
