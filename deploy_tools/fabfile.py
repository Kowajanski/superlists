import random
from fabric2 import Connection, task
from patchwork.files import exists, append
from invoke.context import contextmanager
from invoke import run as lrun

REPO_URL='https://github.com/Kowajanski/superlists.git'

@task
def deploy(c, username, sitename):
    site_folder = '/home/{}/sites/{}'.format(username, sitename)
#    print(site_folder)
    c.run('mkdir -p {}'.format(site_folder))
    with c.cd(site_folder ):
        _get_latest_source(c)
        _update_virtualenv(c)
        _create_or_update_dotenv(c, sitename=sitename)
        _update_static_files(c)
        _update_databases(c)

def _get_latest_source(c):
    c.run('pwd')
    if exists(c,'.git'):
        c.run('git fetch')
    else:
        c.run('git clone {} .'.format(REPO_URL))
    current_commit = lrun('git log -n 1 --format=%H')
    c.run('git reset --hard {}'.format(current_commit.stdout.strip()))

def _update_virtualenv(c):
    if not exists(c,'virtualenv/bin/pip'):
        c.run('python3.6 -m venv virtualenv')
    c.run('./virtualenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv(c, sitename):
    append(c, '.env', 'DJANGO_DEBUG_FALSE=y')
    append(c, '.env', 'SITENAME={}'.format(sitename))
    current_contents = c.run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents.stdout.strip():
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append(c, '.env', 'DJANGO_SECRET_KEY={}'.format(new_secret))

def _update_static_files(c):
    c.run('./virtualenv/bin/python manage.py collectstatic --noinput')

def _update_databases(c):
    c.run('./virtualenv/bin/python manage.py migrate --noinput')
