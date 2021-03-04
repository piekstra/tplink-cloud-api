import os
import pytest

try:
    from .local_env_vars import ENV_VARS
except ImportError:
    ENV_VARS = {}


@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():
    # Will be executed before the first test
    original_environ = dict(os.environ)
    merged_prefer_orig = dict(
        list(ENV_VARS.items()) + list(original_environ.items()))
    os.environ.update(merged_prefer_orig)

    yield
    # Will be executed after the last test
    os.environ.clear()
    os.environ.update(original_environ)
