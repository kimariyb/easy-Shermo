"""
命令行接口。
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from easy_shermo import __version__, __website__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="easy_shermo",
        description="EasyShermo — 全自动批处理 Shermo 热力学计算",
        epilog=f"项目主页: {__website__}",
    )

    # 配置文件
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="配置文件路径 (默认: 当前目录下的 config.yaml)",
    )

    # 目录覆盖
    parser.add_argument(
        "--sp-dir",
        default=None,
        metavar="DIR",
        help="单点能文件目录 (覆盖 config.yaml 中的 spDir)",
    )
    parser.add_argument(
        "--opt-dir",
        default=None,
        metavar="DIR",
        help="振动分析文件目录 (覆盖 config.yaml 中的 optDir)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help="输出目录 (覆盖 config.yaml 中的 outputDir)",
    )

    # 信息
    parser.add_argument(
        "--version",
        action="store_true",
        help="显示版本信息并退出",
    )

    # 日志等级
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="输出调试日志",
    )

    return parser


def apply_cli_overrides(
    cfg: "ShermoConfig",  # noqa: F821  — 延迟导入避免循环
    args: argparse.Namespace,
) -> None:
    """用 CLI 参数覆盖配置对象中的字段。"""
    if args.sp_dir is not None:
        cfg.spDir = args.sp_dir
    if args.opt_dir is not None:
        cfg.optDir = args.opt_dir
    if args.output_dir is not None:
        cfg.outputDir = args.output_dir


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(f"EasyShermo {__version__}")
        sys.exit(0)

    setup_logging(args.verbose)

    # 延迟导入，使 --version 快速响应
    from easy_shermo.config import load_config
    from easy_shermo.engine import run_all

    logger = logging.getLogger(__name__)

    try:
        cfg = load_config(args.config)
    except FileNotFoundError as exc:
        logger.error(exc)
        sys.exit(1)
    except (ValueError, OSError) as exc:
        logger.error("配置加载失败: %s", exc)
        sys.exit(1)

    apply_cli_overrides(cfg, args)

    # 检测旧的 settings.ini 并提示迁移
    if os.path.isfile("settings.ini"):
        print("⚠️  检测到旧的 settings.ini，EasyShermo v2 现在使用 config.yaml 作为配置文件。")
        print("   请参考 config.yaml 示例创建新配置文件。")
        print()

    # 打印横幅信息
    print(f"EasyShermo {__version__}")
    print(f"配置文件: {cfg.config_path}")
    print(cfg)
    print()

    run_all(cfg)

    print()
    print("Copyright (C) 2023 Kimariyb. All rights reserved.")


if __name__ == "__main__":
    main()
