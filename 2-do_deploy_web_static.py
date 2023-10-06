#!/usr/bin/python3
""" A module that creates an .tgz archive from the content of
        web_static
"""
from datetime import datetime
from fabric.api import local, task, run, put, env
import os

env.hosts = ['54.162.80.16', '54.236.45.116']


@task
def do_pack():
    """ A method that creates the archive """
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
    """
    try:
        if not os.path.exists(archive_path):
            return False
        zip_file = os.path.basename(archive_path)
        _file = zip_file.split(".")[0]

        # putting the archive file in /tmp/ directory
        put(archive_path, "/tmp/")

        location = "/data/web_static/releases/"
        # replacing old file
        run("rm -rf {}{}".format(location, _file))
        run("mkdir -p {}{}".format(location, _file))

        # Uncompresaing archive file
        run("tar -xzf /tmp/{} -C {}{}".format(zip_file, location, _file))

        # removing archive from the server('/tmp/')
        run("rm -rf /tmp/{}".format(zip_file))

        # moving content of webstatic to parent directory
        run("mv {0}{1}/web_static/* {0}{1}".format(location, _file))

        # recreating smylink
        run("rm -rf /data/web_static/current")
        run("ln -s {}{} /data/web_static/current".format(location, _file))
        print('New version deployed!')
        return True

    except Exception:
        return False
