import codecs
import glob
import os
import re
from decimal import Decimal
import chardet


class SinglePoint:
    def __init__(self):
        self.orca_sp = None
        self.gaussian_sp = None


def get_orca_sp():
    """
    获得 sp 目录下的所有 orca 文件的单点能
    :return: 所有文件的单点能量和文件名组成的列表
    """
    # 定义寻找单点能量的正则表达式
    energy_regex = re.compile(r'FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)')

    # 获取 sp 目录中所有的 Orca 输出文件
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sp')
    files = glob.glob(os.path.join(dir_path, '*.out'))

    results = []
    # 循环遍历所有文件并查找单点能量
    for file in files:
        try:
            # 使用 chardet 库检测文件编码
            with open(file, 'rb') as f:
                contents = f.read()
                encoding = chardet.detect(contents)['encoding']

            # 使用 codecs 库打开文件并转换为 Python 可以处理的编码
            with codecs.open(file, 'r', encoding=encoding) as f:
                contents = f.read()

                # 查找单点能量
                energies = re.findall(energy_regex, contents)
                if energies:
                    # 只处理第一个单点能量
                    energy = Decimal(energies[0])
                    results.append((os.path.basename(file), energy))
                    print(f'File: {file}, Energy: {energy}')
                else:
                    print(f'Error: No energy found in {file}')
        except Exception as e:
            print(f'Error: Failed to read {file}: {e}')

    return results


def get_gaussian_sp():
    """
    获得 sp 目录下的所有 Gaussian 文件的单点能
    :return: 所有文件的单点能量和文件名组成的列表
    """
    pass
