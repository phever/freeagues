# These are just the keys I hid. You can move any number.
# Currently looks for a 'settings_secrets.py' file
###
SECRET_KEY = 'a_really_long_string'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

### EMAIL STUFF
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'my_luggage'
# EMAIL_HOST_PASSWORD = '12345'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

### OR
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/mnt/project/emails' # change this to a proper location
