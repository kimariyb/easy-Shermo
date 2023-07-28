from config import ShermoConfig
from easyShermo import run_all_shermo


def welcome():
    """
    主页面信息
    """
    hello = """
EasyShermo: A python script to automate the use of Shermo
Version 1.2.0  Release date: 2023-Jul-28
Developer: Kimariyb (kimariyb@163.com)
Address: XiaMen University, School of Electronic Science and Engineering
Official website: https://github.com/kimariyb/easy-shermo
    """
    # 输出主页面信息
    print(hello)
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


if __name__ == '__main__':
    main()
