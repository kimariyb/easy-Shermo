"""
配置模块 — 读取并校验 config.yaml。
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, fields
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# 数据类
# ---------------------------------------------------------------------------


@dataclass
class ShermoConfig:
    """Shermo 配置项，字段名与 config.yaml 的 key 一一对应。"""

    shermoPath: str = ""
    spFile: int = 1
    spDir: str = "sp"
    optDir: str = "opt"
    outputDir: str = "output"
    prtvib: int = 0
    T: str = "298.15"
    P: str = "1.0"
    sclZPE: str = "1.0"
    sclheat: str = "1.0"
    sclS: str = "1.0"
    sclCV: str = "1.0"
    ilowfreq: int = 2
    ravib: str = "100"
    intpvib: str = "100"
    imagreal: str = "20"
    imode: int = 0
    conc: str = "0"
    outshm: int = 0
    defmass: int = 3

    # 内部字段（不由 YAML 直接填充）
    config_path: str = ""

    def __str__(self) -> str:
        parts = ", ".join(
            f"{f.name}={getattr(self, f.name)}"
            for f in fields(self)
            if f.name != "config_path"
        )
        return f"ShermoConfig({parts})"


# ---------------------------------------------------------------------------
# 类型校验表
# ---------------------------------------------------------------------------

_INT_FIELDS = frozenset(
    {
        "spFile",
        "prtvib",
        "ilowfreq",
        "imode",
        "outshm",
        "defmass",
    }
)

_STRING_FIELDS = frozenset(
    {
        "shermoPath",
        "spDir",
        "optDir",
        "outputDir",
        "T",
        "P",
        "sclZPE",
        "sclheat",
        "sclS",
        "sclCV",
        "ravib",
        "intpvib",
        "imagreal",
        "conc",
    }
)


def _coerce_and_validate(raw: dict[str, Any]) -> dict[str, Any]:
    """将原始 YAML 字典做类型转换并校验值域。"""
    errors: list[str] = []

    for key in _INT_FIELDS:
        val = raw.get(key)
        if val is None:
            continue
        try:
            raw[key] = int(val)
        except (ValueError, TypeError):
            errors.append(f"  {key}: 应为整数，收到 {val!r}")

    # string 字段 — 统一转 str
    for key in _STRING_FIELDS:
        val = raw.get(key)
        if val is not None:
            raw[key] = str(val)

    # 必填字段校验
    shermo_path = raw.get("shermoPath", "")
    if not shermo_path:
        errors.append("  shermoPath: 不能为空，请设置 Shermo 可执行文件路径")

    # 值域校验
    sp_file = raw.get("spFile")
    if sp_file is not None and sp_file not in (1, 2):
        errors.append(f"  spFile: 只能为 1 (Gaussian) 或 2 (ORCA)，收到 {sp_file}")

    prtvib = raw.get("prtvib")
    if prtvib is not None and prtvib not in (-1, 0, 1):
        errors.append(f"  prtvib: 只能为 -1、0 或 1，收到 {prtvib}")

    ilow = raw.get("ilowfreq")
    if ilow is not None and ilow not in (0, 1, 2, 3):
        errors.append(f"  ilowfreq: 只能为 0、1、2 或 3，收到 {ilow}")

    imode = raw.get("imode")
    if imode is not None and imode not in (0, 1):
        errors.append(f"  imode: 只能为 0 或 1，收到 {imode}")

    outshm = raw.get("outshm")
    if outshm is not None and outshm not in (0, 1):
        errors.append(f"  outshm: 只能为 0 或 1，收到 {outshm}")

    defmass = raw.get("defmass")
    if defmass is not None and defmass not in (1, 2, 3):
        errors.append(f"  defmass: 只能为 1、2 或 3，收到 {defmass}")

    if errors:
        msg = "配置文件校验失败:\n" + "\n".join(errors)
        raise ValueError(msg)

    return raw


# ---------------------------------------------------------------------------
# 公开 API
# ---------------------------------------------------------------------------

_CONFIG_FILENAMES = ("config.yaml",)


def find_config(path: str | None = None) -> str:
    """查找配置文件路径。

    优先使用 *path* 参数，其次搜索当前目录及父目录下的 config.yaml。
    """
    if path:
        if os.path.isfile(path):
            return path
        raise FileNotFoundError(f"指定的配置文件不存在: {path}")

    # 从 CWD 向上查找，同时检查脚本所在目录
    search_dirs = {os.getcwd(), os.path.dirname(os.path.dirname(__file__))}
    for parent in search_dirs:
        for name in _CONFIG_FILENAMES:
            candidate = os.path.join(parent, name)
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

    # 给出友好的错误提示
    hint = ""
    if os.path.isfile(os.path.join(os.getcwd(), "settings.ini")):
        hint = (
            "\n检测到旧的 settings.ini，EasyShermo v2 改用 YAML 格式。\n"
            "请参考 config.yaml 示例创建新配置文件。"
        )

    raise FileNotFoundError(
        f"在当前目录及上级目录中未找到 {'/'.join(_CONFIG_FILENAMES)}。{hint}\n"
        f"请创建 config.yaml 或通过 --config 指定路径。"
    )


def load_config(path: str | None = None) -> ShermoConfig:
    """读取并校验 YAML 配置文件，返回 ShermoConfig。"""
    config_path = find_config(path)

    with open(config_path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    raw = _coerce_and_validate(raw)

    cfg = ShermoConfig(**raw)
    cfg.config_path = config_path
    return cfg
