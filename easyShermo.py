import glob
import os
import re
import subprocess
import configparser
import os.path

class ShermoConfig:
    def __init__(self):
        self.__settings_path = os.path.join(os.path.dirname(__file__), "settings.ini")
        # 创建 ini config 对象
        self.config = configparser.ConfigParser()
        # 设置注释前缀
        self.config.comment_prefixes = ';'
        # 读取 ini 文件的配置
        self.config.read(self.__settings_path)
        # 将配置返回成对象
        self.shermo_config = self.config['Shermo']
        # 获取配置项
        self.shermoPath = self.shermo_config.get('shermoPath')
        self.spFile = self.shermo_config.get('spFile')
        self.prtvib = self.config.get('Shermo', 'prtvib')
        self.T = self.config.get('Shermo', 'T')
        self.P = self.config.get('Shermo', 'P')
        self.sclZPE = self.config.get('Shermo', 'sclZPE')
        self.sclheat = self.config.get('Shermo', 'sclheat')
        self.sclS = self.config.get('Shermo', 'sclS')
        self.sclCV = self.config.get('Shermo', 'sclCV')
        self.ilowfreq = self.config.get('Shermo', 'ilowfreq')
        self.ravib = self.config.get('Shermo', 'ravib')
        self.imode = self.config.get('Shermo', 'imode')
        self.conc = self.config.get('Shermo', 'conc')
        self.outshm = self.config.get('Shermo', 'outshm')
        self.defmass = self.config.get('Shermo', 'defmass')

    def __str__(self):
        return f"The ShermoConfig is: shermoPath={self.shermoPath}, spFile={self.spFile}, prtvib={self.prtvib}, T={self.T}, " \
               f"P={self.P}, sclZPE={self.sclZPE}, sclheat={self.sclheat}, sclS={self.sclS}, sclCV={self.sclCV}, " \
               f"ilowfreq={self.ilowfreq}, ravib={self.ravib}, imode={self.imode}, conc={self.conc}, outshm={self.outshm}, " \
               f"defmass={self.defmass}"

class ParserFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_parser(shermo_config: ShermoConfig):
        """
        工厂方法，创建一个 Parser 对象
        :param shermo_config: 配置文件对象
        :return:
        """
        if shermo_config.spFile == "1":
            return GaussianParser()
        elif shermo_config.spFile == "2":
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
            energy = str(energies[-1])
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
        print()
        print('The single point energy: ')
        dir_path = os.path.join(os.getcwd(), 'sp')
        return self.process_files(os.path.join(dir_path, '*.out'))


class GaussianParser(Parser):
    def __init__(self):
        super().__init__()

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
        print()
        print('The single point energy: ')
        dir_path = os.path.join(os.getcwd(), 'sp')
        return self.process_files(os.path.join(dir_path, '*.out'))


def run_shermo(shermo_config: ShermoConfig, file_path, energy):
    """
    批量运行 Shermo，并生成 txt 文件记录内容
    :param shermo_config: Shermo 配置对象
    :param file_path: Shermo 运行文件
    :param energy: 单点能量
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


