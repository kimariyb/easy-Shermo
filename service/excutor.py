import os
import subprocess


def run_shermo(shermo_path):
    """
    批量运行 Shermo 可执行程序，将输入文件夹中的所有 ".out" 文件转换为 Shermo 格式，并输出到输出文件夹中。
    :param shermo_path: Shermo 可执行程序的路径。
    :return 一个 shermo 对象
    """
    # 循环遍历输入文件夹下的所有文件
    input_dir = '../opt'
    output_dir = '../output'
    for filename in os.listdir(input_dir):
        # 检查文件扩展名是否为 ".out"
        if filename.endswith(".out"):
            # 构造 Shermo 命令行参数
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{filename}.shermo")
            args = [shermo_path, input_path, "-E", output_path]
            # 调用 Shermo 可执行程序
            result = subprocess.run(args, capture_output=True, text=True)
            # 检查程序是否成功执行
            if result.returncode == 0:
                print(f"{filename}: Shermo completed successfully.")
            else:
                print(f"{filename}: Shermo execution failed.")
                print(result.stderr)



