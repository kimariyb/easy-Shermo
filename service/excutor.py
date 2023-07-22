import glob
import os
import subprocess

from service.parser import ParserFactory
from utils.config import read_config


def run_shermo(config, file_path, energy):
    # 获取文件名和输出文件夹路径
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = "../output"

    # 运行 Shermo 程序
    args = [
        config.shermo_path,
        file_path,
        "-E", str(energy),
        "-ilowfreq", config.ilow_freq,
        "-sclZPE", config.scl_zpe
    ]
    result = subprocess.run(args, capture_output=True, text=True)

    # 检查程序是否成功执行
    if result.returncode == 0:
        print(f"Shermo completed successfully on file {file_name}.")
        contents = result.stdout
        # 写入输出数据到文件
        output_file = os.path.join(output_dir, f"{file_name}.txt")
        with open(output_file, 'w') as f:
            f.write(contents)
    else:
        print(f"Shermo execution failed on file {file_name}.")
        print(result.stderr)


def create_files():
    # 获取基础配置信息和能量列表
    config = read_config('../settings.yaml')
    energies = ParserFactory().create_parser(config).get_sp()

    # 处理每个文件和能量的数据
    opt_dir = "../opt"
    for file_path in glob.glob(os.path.join(opt_dir, '*.out')):
        # 检查文件是否存在
        if os.path.isfile(file_path):
            for energy in energies:
                run_shermo(config, file_path, energy[1])
        else:
            print(f"Error: file {file_path} not found.")
