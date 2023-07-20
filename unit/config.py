import yaml


class Config:
    def __init__(self):
        self.shermo_path = None
        self.freq_file = None
        self.sp_file = None


def read_config(file_path):
    """
    读取 YAML 文件并将其解析为 Python 字典。

    :param file_path: YAML 文件路径
    :return: Python 字典
    """
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    return yaml_data
