import pytest
import logging
from pylastfm import LastFM
from six.moves.configparser import SafeConfigParser


LOG = logging.getLogger(__name__)


CONFIG_DEFAULTS = dict(
    lastfm=dict(
        api_key='api_key',
        api_secret='api_secret',
        username='username',
        password='password',
    ),
)


def pytest_addoption(parser):
    parser.addoption('--config', help='Test configuration YAML')

    parser.addoption('--api_key', help='API Key')
    parser.addoption('--api_secret', help='API Secret')
    parser.addoption('--username', help='Username')
    parser.addoption('--password', help='Password (may be MD5 hashed)')


@pytest.fixture(scope='session')
def config(request):
    path = request.config.getoption('--config')
    config = SafeConfigParser()
    for section, values in CONFIG_DEFAULTS.items():
        config.add_section(section)

        for key, value in values.items():
            config.set(section, key, value)

    if path:
        config.read([path])
        with open(path) as f:
            LOG.debug('Configuration:\n%s', f.read())

    return config


@pytest.fixture(scope='session')
def client(request, config):
    def getoption(key):
        return (
            request.config.getoption('--' + key) or
            config.get('lastfm', key)
        )

    return LastFM(
        getoption('api_key'),
        getoption('api_secret'),
        username=getoption('username'),
        password=getoption('password'),
    )
