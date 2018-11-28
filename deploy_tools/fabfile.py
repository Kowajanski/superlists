import random
from fabric2 import Connection, task
from patchwork.files import exists, append
from invoke.context import contextmanager
from invoke import run as lrun


#env.use_ssh_config=True

REPO_URL='https://github.com/Kowajanski/superlists.git'

@task
def deploy(c, username, sitename):
    site_folder = '/home/{}/sites/{}'.format(username, sitename)
#    print(site_folder)
    c.run('mkdir -p {}'.format(site_folder))
    with c.cd(site_folder ):
        _get_latest_source(c)
        _update_virtualenv(c)
        _create_or_update_dotenv(c)
        _update_static_files(c)
        _update_databases(c)

def _get_latest_source(c):
    c.run('pwd')
    if exists(c,'.git'):
        c.run('git fetch')
    else:
        c.run('git clone {} .'.format(REPO_URL))
    current_commit = lrun('git log -n 1 --format=%H', capture=True)
    c.run('git reset --hard {}'.format(current_commit))

def _update_virtualenv(c):
    if not exists(c,f'virtualenv/bin/pip'):
        c.run(f'python3.6 -m venv virtualenv')
    c.run(f'./virtualenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv(c):
    append(c, '.env', 'DJANGO_DEBUG_FALSE=y')
    append(c, '.env', f'SITENAME={env.host}')
    current_contents = c.run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append(c, '.env', 'DJANGO_SECRET_KEY={}'.format(new_secret))

def _update_static_files(c):
    c.run('./virtualenv/bin/python manage.py collectstatic --noinput')

def _update_databases(c):
    c.run('./virtualenv/bin/python manage.py migrate --noinput')
