# -*- coding: utf-8 -*-
"""
EasyShermo — 全自动批处理 Shermo 的 Python 脚本。

本文件为旧版入口，建议改用:
    python -m easy_shermo
或安装后:
    easy-shermo

@author: Kimariyb (kimariyb@163.com)
@license: MIT
"""

import sys

# 确保能导入同级 easy_shermo 包
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from easy_shermo.cli import main

if __name__ == "__main__":
    main()
