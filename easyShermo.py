# -*- coding: utf-8 -*-
"""
easyShermo.py
Briefly describe the functionality and purpose of the file.

This is a Main function file!

This file is part of EasyShermo.
EasyShermo is a Python script that automate the use of Shermo

@author:
Kimariyb (kimariyb@163.com)

@license:
Licensed under the MIT License.
For details, see the LICENSE file.

@Data:
2023-09-12
"""
import glob
import os
import re
import subprocess
import configparser
import os.path

from datetime import datetime

# 获取当前文件被修改的最后一次时间
time_last = os.path.getmtime(os.path.abspath(__file__))
# 全局的静态变量
__version__ = "v1.2.3"
__developer__ = "Kimariyb, Ryan Hsiun"
__address__ = "XiaMen University, School of Electronic Science and Engineering"
__website__ = "https://github.com/kimariyb/easy-shermo"
__release__ = str(datetime.fromtimestamp(time_last).strftime("%b-%d-%Y"))


class ShermoConfig:
    """
    用于解析 settings.ini 文件的配置类

    Attributes:
        shermoPath: The path to the Shermo executable file.
        spFile: The program for performing a single point calculation task.
            1. Gaussian
            2. Orca
        prtvib: Printing contribution of each vibrational mode.
            -1: Printing to vibcontri.txt.
            1: Printing contribution of each vibrational mode.
            0: Do not print
        T: Temperature in K.
        P: Pressure in atm.
        sclZPE: Frequency scale factor for ZPE
        sclheat: Frequency scale factor for U(T)-U(0)
        sclS: Frequency scale factor for S(T)
        sclCV: Frequency scale factor for heat capacity
        ilowfreq: Treatment of low frequencies.
            0: Harmonic.
            1: Raising low frequencies.
            2: Entropy interpolation.
            3: Entropy and internal energy interpolations
        ravib: Raising lower frequencies to this value (cm^-1) when ilowfreq=1
        imode: Mode of evaluating thermodynamic quantities.
            0: Consider all terms.
            1: Ignore translation and rotation
        conc: If not 0, will calculate variation of Gibbs free energy due to concentration change from present state
        to the specific state.
        outshm: Exporting .shm file after loading QC program output file.
            1: Exporting .shm file after loading QC program output file.
            0: Do not export
        defmass: Default atomic masses used during reading QC program output file.
            1: Element mass.
            2: Most abundant isotope.
            3: Same as the output file
    """

    def __init__(self):
        self.__settings_path = os.path.join(os.path.dirname(__file__), "settings.ini")
        # 创建 ini config 对象
        self.config = configparser.ConfigParser()
        # 设置注释前缀
        self.config.comment_prefixes = ';'

        # 添加一个虚拟的section头部
        self.config.read_string('[DEFAULT]\n' + open(self.__settings_path).read())

        # 获取配置项
        self.shermoPath = self.config.get('DEFAULT', 'shermoPath')
        self.spFile = self.config.get('DEFAULT', 'spFile')
        self.prtvib = self.config.get('DEFAULT', 'prtvib')
        self.T = self.config.get('DEFAULT', 'T')
        self.P = self.config.get('DEFAULT', 'P')
        self.sclZPE = self.config.get('DEFAULT', 'sclZPE')
        self.sclheat = self.config.get('DEFAULT', 'sclheat')
        self.sclS = self.config.get('DEFAULT', 'sclS')
        self.sclCV = self.config.get('DEFAULT', 'sclCV')
        self.ilowfreq = self.config.get('DEFAULT', 'ilowfreq')
        self.ravib = self.config.get('DEFAULT', 'ravib')
        self.imode = self.config.get('DEFAULT', 'imode')
        self.conc = self.config.get('DEFAULT', 'conc')
        self.outshm = self.config.get('DEFAULT', 'outshm')
        self.defmass = self.config.get('DEFAULT', 'defmass')

    def __str__(self):
        return f"The ShermoConfig is: shermoPath={self.shermoPath}, spFile={self.spFile}, prtvib={self.prtvib}, T={self.T}, " \
               f"P={self.P}, sclZPE={self.sclZPE}, sclheat={self.sclheat}, sclS={self.sclS}, sclCV={self.sclCV}, " \
               f"ilowfreq={self.ilowfreq}, ravib={self.ravib}, imode={self.imode}, conc={self.conc}, outshm={self.outshm}, " \
               f"defmass={self.defmass}"


# 使用工厂模式创建相关的 Parser
class ParserFactory:
    @staticmethod
    def create_parser(shermo_config: ShermoConfig):
        """
        工厂方法，创建一个 Parser 对象

        Args:
            shermo_config(ShermoConfig): Shermo 配置类

        Returns:
            GaussianParser 或者 OrcaParser
        """
        if shermo_config.spFile == "1":
            return GaussianParser()
        elif shermo_config.spFile == "2":
            return OrcaParser()
        else:
            raise ValueError("Unknown sp file format")


class Parser:
    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        raise NotImplementedError

    def get_sp(self):
        """
        得到单点能
        :return: 单点能
        """
        raise NotImplementedError


class OrcaParser(Parser):
    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        energy_regex = re.compile(r'FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)')
        energies = re.findall(energy_regex, contents)
        if energies:
            # 查找文件最后一个含有 FINAL SINGLE POINT ENERGY 后面的能量值
            energy = str(energies[-1])
            return energy
        else:
            raise ValueError('No energy found')

    def get_sp(self):
        """
        获得 sp 目录下的所有 orca 文件的单点能
        :return: 所有文件的单点能量和文件名组成的列表
        """
        print()
        print('The single point energy: ')
        # 得到当前文件夹下的 sp 文件夹下的所有 .out 文件
        dir_path = os.path.join(os.getcwd(), 'sp', "*.out")
        sp_files = glob.glob(dir_path)
        results = []
        # 遍历 sp files 得到每一个 sp 文件中的单点能
        for file in sp_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    contents = f.read()
                    energy = self.find_energy(contents)
                    results.append((os.path.basename(file), energy))
                    print(f'File: {file}, Energy: {energy}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results


class GaussianParser(Parser):
    def find_energy(self, contents):
        """
        在文件内容中查找能量值
        """
        ccsd_t_regex = re.compile(r'CCSD\(T\)=\s*(-?\d+\.\d+)')
        mp2_regex = re.compile(r'MP2=\s*(-?\d+\.\d+)')
        hf_regex = re.compile(r'HF=\s*(-?\d+\.\d+)')

        ccsd_t_matches = list(re.finditer(ccsd_t_regex, contents))
        if ccsd_t_matches:
            ccsd_t_match = ccsd_t_matches[-1]
            ccsd_t_energy = str(ccsd_t_match.group(1))
            return ccsd_t_energy
        else:
            mp2_matches = list(re.finditer(mp2_regex, contents))
            if mp2_matches:
                mp2_match = mp2_matches[-1]
                mp2_energy = str(mp2_match.group(1))
                return mp2_energy
            else:
                hf_matches = list(re.finditer(hf_regex, contents))
                if hf_matches:
                    hf_match = hf_matches[-1]
                    hf_energy = str(hf_match.group(1))
                    return hf_energy
                else:
                    raise ValueError('No energy found')

    def get_sp(self):
        """
        处理 gaussian 单点任务产生的 out 文件，并且返回单点能

        Returns:
            results: 所有文件的单点能量和文件名组成的列表
        """
        print()
        print('The single point energy: ')
        # 得到当前文件夹下的 sp 文件夹下的所有 .out 文件
        dir_path = os.path.join(os.getcwd(), 'sp', '*.out')
        sp_files = glob.glob(dir_path)
        results = []
        # 遍历 sp files 得到每一个 sp 文件中的单点能
        for file in sp_files:
            try:
                with open(file, 'r', encoding="utf-8") as f:
                    contents = f.read().replace(' ', '').replace('\n', '')
                    energy = self.find_energy(contents)
                    results.append((os.path.basename(file), energy))
                    print(f'File: {file}, Energy: {energy}')
            except Exception as e:
                print(f'Error: Failed to read {file}: {e}')

        return results


def run_shermo(shermo_config: ShermoConfig, file_path, energy):
    """
    批量运行 Shermo，并生成 txt 文件记录内容

    Args:
        shermo_config(ShermoConfig): Shermo 配置对象
        file_path(str): Shermo 运行文件
        energy(str): 单点能量
    """
    # 获取文件名和输出文件夹路径
    file = os.path.basename(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.join(os.getcwd(), 'output')

    # 运行 Shermo 程序所需要的参数
    args = [
        shermo_config.shermoPath,
        file_path,
        "-E", energy,
        "-prtvib", shermo_config.prtvib,
        "-T", shermo_config.T,
        "-P", shermo_config.P,
        "-sclZPE", shermo_config.sclZPE,
        "-sclheat", shermo_config.sclheat,
        "-sclS", shermo_config.sclS,
        "-sclCV", shermo_config.sclCV,
        "-ilowfreq", shermo_config.ilowfreq,
        "-ravib", shermo_config.ravib,
        "-imode", shermo_config.imode,
        "-conc", shermo_config.conc,
        "-outshm", shermo_config.outshm,
        "-defmass", shermo_config.defmass,
    ]
    # 同时输出命令
    print(subprocess.list2cmdline(args))
    # 通过命令行运行 Shermo
    result = subprocess.run(args, capture_output=True, text=True)

    # 检查程序是否成功执行
    if result.returncode == 0:
        print(f"Hint: Shermo completed successfully on file {file}.")
        print()
        contents = result.stdout
        # 写入输出数据到文件
        output_file = os.path.join(output_dir, f"{file_name}.txt")
        with open(output_file, 'w') as f:
            f.write(contents)
    else:
        print(f"Hint: Shermo execution failed on file {file}.")
        print(result.stderr)


def run_all_shermo(shermo_config: ShermoConfig):
    """
    批量调用 Shermo

    Args:
        shermo_config(ShermoConfig): Shermo 配置类
    """
    # 获取基础配置信息和能量列表
    energies = ParserFactory().create_parser(shermo_config).get_sp()
    print()
    # 注册输入文件夹
    opt_dir = os.path.join(os.getcwd(), 'opt')
    # 注册输入文件夹里所有的 out 文件
    files = glob.glob(os.path.join(opt_dir, '*.out'))
    # 循环
    for file, energy in zip(files, energies):
        # 检查文件是否存在
        if os.path.isfile(file):
            run_shermo(shermo_config, file, energy[1])
        else:
            print(f"Error: file {file} not found.")


def welcome():
    """
    主页面信息
    """

    print(f"EasyShermo -- A python script to automate the use of Shermo")
    print(f"Version: {__version__}, release date: {__release__}")
    print(f"Developer: {__developer__}")
    print(f"Address: {__address__}")
    print(f"EasyShermo home website: {__website__}\n")

    # 在启动时就读取 settings.ini 并返回对象
    shermo_config = ShermoConfig()
    # 打印配置文件信息
    print(shermo_config)
    return shermo_config


def main():
    # 主页面
    shermo_config = welcome()
    # 运行主程序
    run_all_shermo(shermo_config)
    # 获取当前日期和时间
    now = datetime.now().strftime("%b-%d-%Y, %H:%M:%S")
    # 程序结束后提示版权信息和问候语
    print(f"Thank you for using our plotting tool! Have a great day!")
    print("Copyright (C) 2023 Kimariyb. All rights reserved.")
    print(f"Currently timeline: {now}")


if __name__ == '__main__':
    main()
