"""
ORCA 输出文件解析器。
"""

from __future__ import annotations

import glob
import logging
import os
import re

from easy_shermo.parsers import Parser

logger = logging.getLogger(__name__)

_ENERGY_PATTERN = re.compile(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)")


class OrcaParser(Parser):
    """从 ORCA .out 文件中提取单点能。"""

    def find_energy(self, contents: str) -> str:
        matches = _ENERGY_PATTERN.findall(contents)
        if matches:
            energy = matches[-1]
            logger.info("ORCA 能量: %s", energy)
            return energy
        raise ValueError("未找到 ORCA 单点能（FINAL SINGLE POINT ENERGY）")

    def get_sp(self, sp_dir: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        pattern = os.path.join(sp_dir, "*")

        for filepath in sorted(glob.glob(pattern)):
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, encoding="utf-8", errors="replace") as f:
                    contents = f.read()
                energy = self.find_energy(contents)
                basename = os.path.basename(filepath)
                results.append((basename, energy))
                logger.info("  %s → %s", basename, energy)
            except ValueError as exc:
                logger.warning("  %s: %s", os.path.basename(filepath), exc)
            except OSError as exc:
                logger.warning("  读取失败 %s: %s", filepath, exc)

        return results
