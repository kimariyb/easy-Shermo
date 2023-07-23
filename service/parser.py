import glob
import os
import re

from decimal import Decimal
from utils.config import Config


class ParserFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_parser(config: Config):
        if config.sp_file == 1:
            return GaussianParser()
        elif config.sp_file == 2:
            return OrcaParser()
        else:
            raise ValueError("Unknown sp file format")


class Parser:
    def __init__(self):
        pass

    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        raise NotImplementedError

    def process_files(self, file_pattern):
        """
        处理匹配给定文件模式的所有文件，并返回单点能
        """
        raise NotImplementedError

    def get_sp(self):
        """
        得到单点能
        :return: 单点能
        """
        raise NotImplementedError


class OrcaParser(Parser):
    def __init__(self):
        super().__init__()

    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        energy_regex = re.compile(r'FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)')
        energies = re.findall(energy_regex, contents)
        if energies:
            # 查找文件最后一个含有 FINAL SINGLE POINT ENERGY 后面的能量值
            energy = Decimal(energies[-1])
            return energy
        else:
            raise ValueError('No energy found')

    def process_files(self, file_pattern):
        """
        处理匹配给定文件模式的所有文件，并返回单点能
        """
        files = glob.glob(file_pattern)
        results = []

        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    contents = f.read()
                    energy = self.find_energy(contents)
                    results.append((os.path.basename(file), energy))
                    print(f'File: {file}, Energy: {energy}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results

    def get_sp(self):
        """
        获得 sp 目录下的所有 orca 文件的单点能
        :return: 所有文件的单点能量和文件名组成的列表
        """
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sp')
        return self.process_files(os.path.join(dir_path, '*.out'))


class GaussianParser(Parser):
    def __init__(self):
        super().__init__()

    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        mp2_regex = re.compile(r'MP2=\s*(-?\d+\.\d+)')
        hf_regex = re.compile(r'HF=\s*(-?\d+\.\d+)')

        mp2_matches = list(re.finditer(mp2_regex, contents))
        if mp2_matches:
            mp2_match = mp2_matches[-1]
            mp2_energy = Decimal(mp2_match.group(1))
            return mp2_energy
        else:
            hf_matches = list(re.finditer(hf_regex, contents))
            if hf_matches:
                hf_match = hf_matches[-1]
                hf_energy = Decimal(hf_match.group(1))
                return hf_energy
            else:
                raise ValueError('No energy found')

    def process_files(self, file_pattern):
        """
        处理匹配给定文件模式的所有文件，并返回单点能
        """
        files = glob.glob(file_pattern)
        results = []

        for file in files:
            try:
                with open(file, 'r', encoding="utf-8") as f:
                    contents = f.read().replace(' ', '').replace('\n', '')
                    energy = self.find_energy(contents)
                    results.append((os.path.basename(file), energy))
                    print(f'File: {file}, Energy: {energy}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results

    def get_sp(self):
        """
        处理 gaussian 单点任务产生的 out 文件，并且返回单点能
        :return: 所有文件的单点能量和文件名组成的列表
        """
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sp')
        return self.process_files(os.path.join(dir_path, '*.out'))
