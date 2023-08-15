import datetime

from easyShermo import run_all_shermo, ShermoConfig


def welcome():
    """
    主页面信息
    """
    # 定义版本信息
    version_info = {
        'version': 'v1.2.2',
        'release_date': 'Aug-3-2023',
        'developer': 'Kimariyb, Ryan Hsiun',
        'address': 'XiaMen University, School of Electronic Science and Engineering',
        'website': 'https://github.com/kimariyb/easy-shermo',
    }

    print(f"EasyShermo -- A python script to automate the use of Shermo")
    print(f"Version: {version_info['version']}, release date: {version_info['release_date']}")
    print(f"Developer: {version_info['developer']}")
    print(f"Address: {version_info['address']}")
    print(f"EasyShermo home website: {version_info['website']}\n")

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
    now = datetime.datetime.now().strftime("%b-%d-%Y, 00:45:%S")
    # 程序结束后提示版权信息和问候语
    print(f"Thank you for using our plotting tool! Have a great day!")
    print("Copyright © 2023 Kimariyb. All rights reserved.")
    print(f"Currently timeline: {now}")

if __name__ == '__main__':
    main()
