import yaml


class Config:
    def __init__(self):
        self.shermo_path = None
        self.freq_file = None
        self.sp_file = None

    def __str__(self):
        return 'Shermo path: {}\nFreq file: {}\nSP file: {}'.format(self.shermo_path, self.freq_file, self.sp_file)

    def set_shermo_path(self, path):
        self.shermo_path = path
        return self.shermo_path

    def set_freq_file(self, freq_file):
        self.freq_file = freq_file
        return self.freq_file

    def set_sp_file(self, sp_file):
        self.sp_file = sp_file
        return self.sp_file


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
    config.set_freq_file(yaml_data['freq_file'])
    config.set_sp_file(yaml_data['sp_file'])

    return config
