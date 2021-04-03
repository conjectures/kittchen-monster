from kittchen.settings.base import *

# Set debug true for development settings
# SECRET_KEY = 'p82n&_s9v33n1kvb!-p)2zu2940p%&+zeddkma-qp!qkk=3sm8'

# ALLOWED_HOSTS = ['*']
DEBUG = False


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
