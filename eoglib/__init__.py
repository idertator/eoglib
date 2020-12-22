import gettext
from os.path import join, abspath, dirname


def setup_i18n(lang='en'):
    LOCALE_PATH = join(abspath(dirname(dirname(__file__))), 'locales')

    tr = gettext.translation('eoglib', LOCALE_PATH, languages=[lang])
    tr.install('eoglib')
