import sys

try:
    from django.conf import settings
    from django.test.utils import get_runner

    settings.configure(
        SECRET_KEY='fakesecretkey',
        # Disable some system checks during tests for now
        # Django 1.11 appears to have gotten more strict about these
        # and now tests do not run, but since some older, supported
        # versions do not enforce them with the systemcheck system
        # there are tests which specifically make these mistakes and ensure
        # that the correct exceptions are raised.
        # fields.E130 = must define decimal_places
        # fields.E132 = must define max_digits
        SILENCED_SYSTEM_CHECKS = ['fields.E130', 'fields.E132'],
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "djfractions",
            "tests",
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(),
        TEMPLATES = [
            {'BACKEND': 'django.template.backends.django.DjangoTemplates',
             'DIRS': [],
             'APP_DIRS': True,
             'OPTIONS': {
                 'context_processors': []
             }
            }
        ],
        DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    #if failures:
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
