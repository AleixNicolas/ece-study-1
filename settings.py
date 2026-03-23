from os import environ

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
    real_world_currency_per_point=1.00, 
    participation_fee=0.00, 
    doc=""
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

DEMO_PAGE_INTRO_HTML = """ """