# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/info.log',
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/error.log',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.cart': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'core.shop': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'core.products': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
