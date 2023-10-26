#!/usr/bin/python3
""" A module that creates a .tgz archive from the content of
        web_static
"""
from datetime import datetime
from fabric.api import local, task, run, put, env, runs_once, lcd, cd
import os


env.hosts = ['54.157.188.93', '34.207.155.107']


@runs_once
def do_pack():
    """ A method that creates the archive
        Usage: fab -f 1-pack_web_static.py do_pack
    """
    time = datetime.now()
    dt = "{}{}{}{}{}{}".format(time.year,
                               time.month,
                               time.day,
                               time.hour,
                               time.minute,
                               time.second)
    path = "versions/web_static_{}.tgz".format(dt)
    print("Packing web_static to {}".format(path))

    local("mkdir -p versions")

    if local("tar -czvf {} web_static".format(path)).succeeded:
        return path
    return None


@task
def do_deploy(archive_path):
    """ Destribute an archive to my web servers
        Usage: fab -f 2-do_deploy_web_static.py\
        do_deploy:archive_path=versions/web_static_20170315003959.tgz\
        -i my_ssh_private_key -u ubuntu
    """
    try:
        if not os.path.exists(archive_path):
            return False
        zip_file = os.path.basename(archive_path)
        _file = zip_file.split(".")[0]

        # putting the archive file in /tmp/ directory
        put(archive_path, "/tmp/")

        location = "/data/web_static/releases/"

        # removing decompressed directory if exists
        run("rm -rf {}{}/".format(location, _file))

        # making necessary directory
        run("mkdir -p {}{}/".format(location, _file))

        # Uncompressing archive file
        run("tar -xzf /tmp/{} -C {}{}".format(zip_file, location, _file))

        # removing archive from the server('/tmp/')
        run("rm -rf /tmp/{}".format(zip_file))

        # moving content of webstatic to parent directory
        run("mv {0}{1}/web_static/* {0}{1}/".format(location, _file))

        # removing /data/web_static/releases/web_static
        run("rm -rf {}{}/web_static".format(location, _file))

        # recreating symlink
        run("rm -rf /data/web_static/current")
        run("ln -s {}{}/ /data/web_static/current".format(location, _file))
        print('New version deployed!')
        return True

    except Exception:
        return False


@task
def deploy():
    """ pack and deploy to server
        Ussage: fab -f 3-deploy_web_static.py deploy\
                -i my_ssh_private_key -u ubuntu
    """
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)


@task
def do_clean(number=0):
    """ Deletes out-of-date archives
        number:
            number of the archives, including the most
            recent, to keep
        Usage: fab -f 100-clean_web_static.py\
                do_clean:number=2 -i my_ssh_private_key\
                -u ubuntu > /dev/null 2>&1
    """
    number = 1 if int(number) == 0 else int(number)

    archives = sorted(os.listdir("versions"))

    [archives.pop() for i in range(number)]
    with lcd("versions"):
        [local("rm ./{}".format(archive)) for archive in archives]

    path = "/data/web_static/releases"
    with cd(path):
        archives = run("ls -tr").split()
        archives = [a for a in archives if "web_static_" in a]
        [archives.pop() for i in range(number)]
        [run("rm -rf ./{}".format(a)) for a in archives]
