import codecs
import glob
import os
import re
import chardet

from decimal import Decimal
from unit.config import read_config


class ParserFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_parser():
        config_file_path = os.path.join("..", "settings.yaml")
        config = read_config(config_file_path)
        if config.sp_file == 1:
            return GaussianParser()
        elif config.sp_file == 2:
            return OrcaParser()
        else:
            raise ValueError("Unknown sp file format")


class Parser:
    def __init__(self):
        pass

    def get_sp(self):
        """
        得到单点能
        :return: 单点能
        """
        raise NotImplementedError


class OrcaParser(Parser):
    def __init__(self):
        super().__init__()

    def get_sp(self):
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
                        # 查找文件最后一个含有 FINAL SINGLE POINT ENERGY 后面的能量值
                        energy = Decimal(energies[-1])
                        results.append((os.path.basename(file), energy))
                        print(f'File: {file}, Energy: {energy}')
                    else:
                        print(f'Error: No energy found in {file}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results


class GaussianParser(Parser):
    def __init__(self):
        super().__init__()

    def get_sp(self):
        """
        处理 gaussian 单点任务产生的 out 文件，并且返回单点能
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
                        # 查找文件最后一个含有 FINAL SINGLE POINT ENERGY 后面的能量值
                        energy = Decimal(energies[-1])
                        results.append((os.path.basename(file), energy))
                        print(f'File: {file}, Energy: {energy}')
                    else:
                        print(f'Error: No energy found in {file}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results
