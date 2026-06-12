"""
执行引擎 — 调用 Shermo 并对每个 opt 文件运行热力学计算。
"""

from __future__ import annotations

import glob
import logging
import os
import subprocess

from easy_shermo.config import ShermoConfig
from easy_shermo.parsers import create_parser
from easy_shermo.utils import ensure_dir, match_files_by_prefix

logger = logging.getLogger(__name__)


def _build_shermo_args(cfg: ShermoConfig, opt_path: str, energy: str) -> list[str]:
    """构造 Shermo 命令行参数。"""
    return [
        cfg.shermoPath,
        os.path.abspath(opt_path),
        "-E",
        energy,
        "-prtvib",
        str(cfg.prtvib),
        "-T",
        cfg.T,
        "-P",
        cfg.P,
        "-sclZPE",
        cfg.sclZPE,
        "-sclheat",
        cfg.sclheat,
        "-sclS",
        cfg.sclS,
        "-sclCV",
        cfg.sclCV,
        "-ilowfreq",
        str(cfg.ilowfreq),
        "-ravib",
        cfg.ravib,
        "-intpvib",
        cfg.intpvib,
        "-imagreal",
        cfg.imagreal,
        "-imode",
        str(cfg.imode),
        "-conc",
        cfg.conc,
        "-outshm",
        str(cfg.outshm),
        "-defmass",
        str(cfg.defmass),
    ]


def run_shermo(cfg: ShermoConfig, opt_path: str, energy: str) -> None:
    """对单个 opt 文件调用 Shermo，输出写入 output 目录。"""
    basename = os.path.basename(opt_path)
    stem = os.path.splitext(basename)[0]

    args = _build_shermo_args(cfg, opt_path, energy)
    logger.info("运行: %s", subprocess.list2cmdline(args))

    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error("Shermo 执行失败 [%s]:\n%s", basename, result.stderr)
        return

    logger.info("Shermo 成功完成: %s", basename)

    out_dir = ensure_dir(cfg.outputDir)
    out_path = os.path.join(out_dir, f"{stem}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)
    logger.debug("输出写入: %s", out_path)


def run_all(cfg: ShermoConfig) -> None:
    """批量执行全流程。"""
    # 1. 解析单点能
    parser = create_parser(cfg)
    logger.info("正在扫描单点能文件: %s", cfg.spDir)

    sp_files = sorted(glob.glob(os.path.join(cfg.spDir, "*")))
    sp_files = [f for f in sp_files if os.path.isfile(f)]
    sp_basenames = [os.path.basename(f) for f in sp_files]

    # 用解析器读取能量，返回 (basename, energy)
    sp_energies = parser.get_sp(cfg.spDir)  # list of (basename, energy)
    sp_energy_map = dict(sp_energies)

    if not sp_energy_map:
        logger.error("未从 %s 中读取到任何单点能，终止。", cfg.spDir)
        return

    # 2. 扫描 opt 文件并配对
    opt_files = sorted(glob.glob(os.path.join(cfg.optDir, "*")))
    opt_files = [f for f in opt_files if os.path.isfile(f)]
    if not opt_files:
        logger.error("opt 目录为空: %s", cfg.optDir)
        return

    opt_basenames = [os.path.basename(f) for f in opt_files]
    pairs = match_files_by_prefix(sp_basenames, opt_basenames)

    # 3. 逐对调用 Shermo
    for opt_basename, sp_basename in pairs:
        energy = sp_energy_map.get(sp_basename)
        if energy is None:
            logger.warning("%s 的能量未找到，跳过", sp_basename)
            continue

        opt_path = os.path.join(cfg.optDir, opt_basename)
        if not os.path.isfile(opt_path):
            logger.warning("文件不存在: %s", opt_path)
            continue

        run_shermo(cfg, opt_path, energy)

    logger.info("全部任务完成。")
