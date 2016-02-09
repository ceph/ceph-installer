from mariner import hooks

# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'mariner.controllers.root.RootController',
    'modules': ['mariner'],
    'debug': False,
    'hooks': [hooks.SystemCheckHook()]
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'mariner': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False},
        'pecan': {'level': 'INFO', 'handlers': ['console'], 'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    # XXX Determine the right location for logs
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s]'
                       '[%(threadName)s] %(message)s'),
        '__force_dict__': True
        }
    }
}


sqlalchemy = {
    # XXX Determine the right location for the database
    'url': 'sqlite:////tmp/mariner.db',
    'echo':          True,
    'echo_pool':     True,
    'pool_recycle':  3600,
    'encoding':      'utf-8'
}
