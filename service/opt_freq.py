import codecs
import os
import re

from chardet import detect


class SinglePoint:
    def __init__(self):
        self.orca_sp = None
        self.gaussian_sp = None


def get_gaussian_sp():
    """
    获得 sp 目录下的所有 gaussian 文件的单点能
    :return:
    """
    pass