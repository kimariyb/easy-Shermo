"""
工具函数。
"""

from __future__ import annotations

import logging
import os
import re

logger = logging.getLogger(__name__)

# 匹配文件名中的公共前缀: xxx_sp.ext / xxx_opt.ext
_SUFFIX_SP_RE = re.compile(r"^(.*?)_sp\.[^.]+$")
_SUFFIX_OPT_RE = re.compile(r"^(.*?)_opt\.[^.]+$")


def _stem(filename: str) -> str | None:
    """提取文件名中的公共前缀。

    例:
        "CH4_sp.out"  → "CH4"
        "CH4_opt.out" → "CH4"
        "README.md"   → None
    """
    for regex in (_SUFFIX_SP_RE, _SUFFIX_OPT_RE):
        m = regex.match(filename)
        if m:
            return m.group(1)
    return None


def match_files_by_prefix(
    sp_files: list[str], opt_files: list[str]
) -> list[tuple[str, str]]:
    """基于文件名前缀将 sp 文件和 opt 文件配对。

    Args:
        sp_files:  sp 目录下的文件名列表。
        opt_files: opt 目录下的文件名列表。

    Returns:
        列表，每项为 (opt文件名, sp文件名)。按 opt 文件名的字母序排列。

    Raises:
        ValueError: 存在无法配对的 sp 或 opt 文件。
    """
    # 构建前缀 → 文件名 索引
    sp_index: dict[str, str] = {}
    for f in sp_files:
        key = _stem(f)
        if key:
            sp_index[key] = f

    opt_index: dict[str, str] = {}
    for f in opt_files:
        key = _stem(f)
        if key:
            opt_index[key] = f

    # 按 opt 前缀顺序配对
    pairs: list[tuple[str, str]] = []
    for key in sorted(opt_index):
        opt_f = opt_index[key]
        sp_f = sp_index.get(key)
        if sp_f is None:
            raise ValueError(
                f"opt 文件 '{opt_f}' (前缀 '{key}') 没有对应的 sp 文件"
            )
        pairs.append((opt_f, sp_f))

    # 检查是否有未配对的 sp 文件
    sp_keys = set(sp_index)
    opt_keys = set(opt_index)
    orphan_sp = sp_keys - opt_keys
    if orphan_sp:
        orphan_names = [sp_index[k] for k in sorted(orphan_sp)]
        logger.warning("以下 sp 文件没有对应的 opt 文件，将被忽略: %s", orphan_names)

    return pairs


def ensure_dir(path: str) -> str:
    """确保目录存在，若不存在则创建。返回绝对路径。"""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)
