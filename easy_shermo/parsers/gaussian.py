"""
Gaussian 输出文件解析器。
"""

from __future__ import annotations

import glob
import logging
import os
import re

from easy_shermo.parsers import Parser

logger = logging.getLogger(__name__)

# 按优先级排列的正则列表: (名称, 正则)
_ENERGY_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("CCSD(T)", re.compile(r"CCSD\(T\)\s*=\s*(-?\d+\.\d+)")),
    ("MP2", re.compile(r"MP2\s*=\s*(-?\d+\.\d+)")),
    ("HF", re.compile(r"HF\s*=\s*(-?\d+\.\d+)")),
]


class GaussianParser(Parser):
    """从 Gaussian .out / .log 文件中提取单点能。

    优先级: CCSD(T) > MP2 > HF，均取文件中的最后一个匹配。
    """

    def find_energy(self, contents: str) -> str:
        # 移除所有空白使正则更健壮（Gaussian 输出格式多变）
        compact = re.sub(r"\s+", "", contents)

        for name, pattern in _ENERGY_PATTERNS:
            matches = pattern.findall(compact)
            if matches:
                energy = matches[-1]
                logger.info("Gaussian 能量 [%s]: %s", name, energy)
                return energy

        raise ValueError("未找到 Gaussian 单点能（尝试了 CCSD(T)、MP2、HF）")

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
