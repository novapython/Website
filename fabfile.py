from fabric.api import *
from fabric.contrib.console import confirm
from contextlib import contextmanager as _contextmanager

production_hosts = ['rday@ryanday.net']
production_user = 'rday'
production_branch = 'production'
staging_hosts = ['rday@172.18.2.13']
staging_user = 'rday'
staging_branch = 'staging'
repository = 'git://github.com/novapython/Website.git'

root_dir = '/var/www/novapython'
code_dir = '%s/src' % root_dir
virtualenv_dir = '%s/env' % root_dir
env.activate = 'source %s/bin/activate' % virtualenv_dir

@_contextmanager
def virtualenv():
    with cd(code_dir):
        with prefix(env.activate):
            yield

def production_deploy():
    env.user = production_user
    env.environment = 'production'
    env.hosts = production_hosts
    env.branch = production_branch
    execute(_deploy)


def staging_deploy():
    env.user = staging_user
    env.environment = 'staging'
    env.hosts = staging_hosts
    env.branch = staging_branch
    execute(_deploy)


def build_virtualenv():
    sudo('mkdir -p %s' % virtualenv_dir)
    sudo('chown -R %s.%s %s' % (env.user, env.user, virtualenv_dir))
    sudo('easy_install pip')
    sudo('yum -y install gcc mysql-devel python-devel mod_wsgi')
    run('virtualenv --no-site-packages %s' % virtualenv_dir)


def build_src():
    sudo('mkdir -p %s' % code_dir)
    sudo('chown -R %s.%s %s' % (env.user, env.user, code_dir))
    with cd(code_dir):
        run("git clone %s %s" % (repository, code_dir))
        run('mkdir %s/sessions' % code_dir)
        run('chmod 777 %s/sessions' % code_dir)


def _deploy():
    if local('test deploy_files/config-%s.py' % env.environment).failed:
        abort('No config file was found!')
    if local('test deploy_files/virtualhost-%s' % env.environment).failed:
        abort('No virtualhost file was found!')
    sudo('mkdir /var/run/wsgi')

    with settings(warn_only=True):
        if run('test -d %s' % virtualenv_dir).failed:
            execute(build_virtualenv)
        if run('test -d %s' % code_dir).failed:
            execute(build_src)
        with virtualenv():
            run('git pull origin %s' % env.branch)
            run('pip install -r %s/requirements.txt' % code_dir)
            put('deploy_files/config-%s.py' % env.environment, 'novaconfig.py')
            put('deploy_files/virtualhost-%s' % env.environment, 'virtualhost')
            if run('test -d /etc/apache/sites-enabled').failed:
                sudo('mkdir -p /etc/apache/sites-enabled')
            sudo('mv virtualhost /etc/apache/sites-enabled/014-novapy')
            sudo('apachectl restart')


def deploy():
    if confirm('Deploy to production?', default=False):
        production_deploy()
    else:
        staging_deploy()
