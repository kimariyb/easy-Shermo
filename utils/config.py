import yaml


class Config:
    def __init__(self):
        self.shermo_path = ''
        self.sp_file = None
        self.ilow_freq = ''
        self.scl_zpe = ''

    def __str__(self):
        return 'Shermo path: {}\nSP file: {}\nilowfreq: {}'.format(
            self.shermo_path, self.sp_file, self.ilow_freq)

    def set_shermo_path(self, path):
        self.shermo_path = str(path)
        return self.shermo_path

    def set_sp_file(self, sp_file):
        self.sp_file = sp_file
        return self.sp_file

    def set_ilow_freq(self, ilow_freq):
        self.ilow_freq = str(ilow_freq)
        return self.ilow_freq

    def set_scl_zpe(self, scl_zpe):
        self.scl_zpe = str(scl_zpe)
        return self.scl_zpe


def read_config(file_path):
    """
    读取 YAML 文件并将其解析为 Python 字典。

    :param file_path: YAML 文件路径
    :return: Python 字典
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        yaml_data = yaml.safe_load(file)

    config = Config()
    config.set_shermo_path(yaml_data['shermo_path'])
    config.set_sp_file(yaml_data['sp_file'])
    config.set_ilow_freq(yaml_data['ilow_freq'])
    config.set_scl_zpe(yaml_data['scl_zpe'])

    return config
