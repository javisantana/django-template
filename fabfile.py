# -*- encoding: utf-8 -*-

"""
deployement script
"""

from fabric.api import run, sudo, env
from fabric.context_managers import cd, show, settings
from fabric.contrib.project import upload_project
from fabric.contrib.files import exists


env.user = 'vagrant'
env.password = 'vagrant'
env.hosts = ['127.0.0.1:2222']
env.deploy_folder = '/home/vagrant/auto'
env.git_repo = 'https://github.com/javisantana/django-template'
env.git_repo = '/home/vagrant/repo/app'

def pkg_install(pkg):
    """ install pkg using apt-get """
    sudo("aptitude -y install %s" % pkg)

def install():
    """ install base system on ubuntu machine """
    # apt-get's
    sudo("aptitude -y update")
    pkgs = ['git-core', 'python-dev', 'build-essential', 'nginx', 'python-setuptools']
    pkg_install(' '.join(pkgs))

    # target folder
    run("mkdir -p %s" % env.deploy_folder)

    # install virtualenv
    sudo("easy_install virtualenv")
    sudo("easy_install pip")
    sudo("pip install supervisor")
    run("virtualenv %s/env" % env.deploy_folder)
    run("%s/env/bin/pip install -U pip" % env.deploy_folder)

    # clone repo
    if not exists(env.deploy_folder + "/app"):
        with cd(env.deploy_folder):
            run("git clone %s app" % env.git_repo)
    else:
        update_files()

    sudo("rm -rf /etc/nginx/nginx.conf")
    sudo("rm -rf /etc/supervisord.conf" % env)
    
    # configuration
    sudo("ln -s %(deploy_folder)s/app/deploy/nginx.conf /etc/nginx/nginx.conf" % env)
    sudo("ln -s %(deploy_folder)s/app/deploy/supervisord.conf /etc/supervisord.conf" % env)

    update_dependencies()


def update_files():
    with cd(env.deploy_folder + "/app"):
        run("git pull")

def deploy():
    """ deploy repo """
    update_files()
    update_dependencies()
    reload()

def reload():
    """ restart services """
    # start supervisord
    with settings(warn_only=True):
        sudo("supervisord")
    sudo("supervisorctl reload") # reload supervisor conf
    sudo("supervisorctl restart django")
    # nginx
    sudo("invoke-rc.d nginx restart")

def update_dependencies():
    """ update depencies from requirements """
    sudo("%(deploy_folder)s/env/bin/pip install -r %(deploy_folder)s/app/django-template/requirements.txt" % env)
    sudo("%(deploy_folder)s/env/bin/pip install -r %(deploy_folder)s/app/deploy/production_requirements.txt" % env)
    
