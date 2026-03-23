from os import environ

SESSION_CONFIGS = [
    dict(
        name='phase_1_intake',
        app_sequence=['phase_1'],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessfrom os import environ

SECRET_KEY = environ.get('OTREE_SECRET_KEY', '2003881942849')

SESSION_CONFIGS = [
    dict(
        name='phase_1_intake',
        display_name="Phase 1: Recruitment & Profiling",
        app_sequence=['phase_1'],
        num_demo_participants=3,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

ROOMS = [
    dict(name='Room_1', display_name='Room 1'),
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'password')
DEMO_PAGE_INTRO_HTML = """ """ed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# --- NEW ROOMS CONFIGURATION FOR TESTING ---
ROOMS = [
    dict(
        name='Room_1',
        display_name='Room 1'
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2003881942849'
