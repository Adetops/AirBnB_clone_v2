#!/usr/bin/python3
""" A module that creates a .tgz archive from the content of
        web_static
"""
from datetime import datetime
from fabric.api import local, task
import os


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
