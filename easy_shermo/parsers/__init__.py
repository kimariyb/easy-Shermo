"""
解析器基类与工厂。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from easy_shermo.config import ShermoConfig


class Parser(ABC):
    """单点能解析器基类。"""

    @abstractmethod
    def find_energy(self, contents: str) -> str:
        """从文件内容中提取单点能。"""
        ...

    @abstractmethod
    def get_sp(self, sp_dir: str) -> list[tuple[str, str]]:
        """扫描 *sp_dir* 下所有文件，返回 (文件名, 能量) 列表。"""
        ...


def create_parser(cfg: ShermoConfig) -> Parser:
    """工厂方法 — 根据配置创建对应的解析器。"""
    if cfg.spFile == 1:
        from easy_shermo.parsers.gaussian import GaussianParser

        return GaussianParser()
    if cfg.spFile == 2:
        from easy_shermo.parsers.orca import OrcaParser

        return OrcaParser()
    raise ValueError(f"不支持的 spFile 值: {cfg.spFile}，请使用 1 (Gaussian) 或 2 (ORCA)")
