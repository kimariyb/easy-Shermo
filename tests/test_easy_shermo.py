"""
EasyShermo 单元测试。
"""
import os
import re
import sys
import tempfile

import pytest
import yaml

# 确保能导入包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from easy_shermo.config import load_config, ShermoConfig, find_config
from easy_shermo.parsers import create_parser, Parser
from easy_shermo.parsers.gaussian import GaussianParser
from easy_shermo.parsers.orca import OrcaParser
from easy_shermo.utils import match_files_by_prefix, _stem, ensure_dir
from easy_shermo.cli import build_parser, apply_cli_overrides


# ===================================================================
# 配置测试
# ===================================================================

class TestConfig:
    def test_load_valid_yaml(self):
        """加载合法的 YAML 配置文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.yaml")
            with open(path, "w") as f:
                f.write("shermoPath: /usr/bin/shermo\nspFile: 1\n")
            cfg = load_config(path)
            assert cfg.shermoPath == "/usr/bin/shermo"
            assert cfg.spFile == 1

    def test_invalid_spfile(self):
        """spFile 不为 1 或 2 时应报错。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.yaml")
            with open(path, "w") as f:
                f.write("shermoPath: shermo\nspFile: 3\n")
            with pytest.raises(ValueError, match="spFile"):
                load_config(path)

    def test_missing_shermopath(self):
        """shermoPath 为空时应报错。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.yaml")
            with open(path, "w") as f:
                f.write("spFile: 1\n")
            with pytest.raises(ValueError, match="shermoPath"):
                load_config(path)

    def test_default_values(self):
        """未提供的字段应有合理的默认值。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.yaml")
            with open(path, "w") as f:
                f.write("shermoPath: shermo\nspFile: 2\n")
            cfg = load_config(path)
            assert cfg.optDir == "opt"
            assert cfg.ilowfreq == 2
            assert cfg.defmass == 3
            assert cfg.prtvib == 0

    def test_str_representation(self):
        """__str__ 应包含主要字段。"""
        cfg = ShermoConfig(shermoPath="/test")
        s = str(cfg)
        assert "shermoPath=/test" in s
        assert "spFile=" in s

    def test_find_config_not_found(self):
        """不存在的路径应抛出 FileNotFoundError。"""
        with pytest.raises(FileNotFoundError):
            find_config("/nonexistent/path/config.yaml")


# ===================================================================
# 解析器测试
# ===================================================================

class TestGaussianParser:
    @pytest.fixture
    def parser(self):
        return GaussianParser()

    def test_ccsd_t_energy(self, parser):
        """提取 CCSD(T) 能量。"""
        content = """
 HF= -100.1234567
 MP2= -100.2345678
 CCSD(T)= -100.3456789
        """
        energy = parser.find_energy(content)
        assert energy == "-100.3456789"

    def test_mp2_fallback(self, parser):
        """无 CCSD(T) 时回退到 MP2。"""
        content = " HF= -50.1  MP2= -50.2 "
        energy = parser.find_energy(content)
        assert energy == "-50.2"

    def test_hf_fallback(self, parser):
        """仅 HF 能量时使用 HF。"""
        content = " HF= -30.0 "
        energy = parser.find_energy(content)
        assert energy == "-30.0"

    def test_no_energy_found(self, parser):
        """无任何能量时抛出 ValueError。"""
        with pytest.raises(ValueError):
            parser.find_energy("no energy here")

    def test_last_match_used(self, parser):
        """多个匹配时取最后一个。"""
        content = """
 CCSD(T)= -100.1
 CCSD(T)= -200.2
        """
        energy = parser.find_energy(content)
        assert energy == "-200.2"

    def test_real_output_format(self, parser):
        """测试真实的 Gaussian 输出格式。"""
        content = """
 Gaussian output ...
 HF= -100.0
 MP2= -100.1
 CCSD(T)= -100.2
        """
        energy = parser.find_energy(content)
        assert energy == "-100.2"


class TestOrcaParser:
    @pytest.fixture
    def parser(self):
        return OrcaParser()

    def test_single_point_energy(self, parser):
        """提取 ORCA 单点能。"""
        content = """
                                ----------------
                FINAL SINGLE POINT ENERGY    -100.1234567
                                ----------------
        """
        energy = parser.find_energy(content)
        assert energy == "-100.1234567"

    def test_last_match(self, parser):
        """多个 FINAL SINGLE POINT ENERGY 时取最后一个。"""
        content = """
 FINAL SINGLE POINT ENERGY      -50.0
 FINAL SINGLE POINT ENERGY      -60.0
        """
        energy = parser.find_energy(content)
        assert energy == "-60.0"

    def test_no_energy(self, parser):
        """无能量时抛出 ValueError。"""
        with pytest.raises(ValueError):
            parser.find_energy("no energy here")


class TestParserFactory:
    def test_create_gaussian(self):
        """spFile=1 时创建 GaussianParser。"""
        cfg = ShermoConfig(shermoPath="/x", spFile=1)
        parser = create_parser(cfg)
        assert isinstance(parser, GaussianParser)

    def test_create_orca(self):
        """spFile=2 时创建 OrcaParser。"""
        cfg = ShermoConfig(shermoPath="/x", spFile=2)
        parser = create_parser(cfg)
        assert isinstance(parser, OrcaParser)

    def test_invalid(self):
        """不支持的 spFile 值应抛出 ValueError。"""
        cfg = ShermoConfig(shermoPath="/x", spFile=99)
        with pytest.raises(ValueError):
            create_parser(cfg)


# ===================================================================
# 工具函数测试
# ===================================================================

class TestUtils:
    def test_stem_sp(self):
        assert _stem("CH4_sp.out") == "CH4"
        assert _stem("C2H4_sp.out") == "C2H4"
        assert _stem("my_file_sp.log") == "my_file"

    def test_stem_opt(self):
        assert _stem("CH4_opt.out") == "CH4"
        assert _stem("C2H4_opt.out") == "C2H4"

    def test_stem_no_match(self):
        assert _stem("README.md") is None
        assert _stem("settings.ini") is None
        assert _stem("CH4.out") is None

    def test_match_files_by_prefix_basic(self):
        sp = ["C_sp.out", "C2H2_sp.out", "CH4_sp.out"]
        opt = ["C_opt.out", "CH4_opt.out", "C2H2_opt.out"]
        pairs = match_files_by_prefix(sp, opt)
        assert len(pairs) == 3
        # 按 opt 字母序排列
        assert pairs[0] == ("C_opt.out", "C_sp.out")
        assert pairs[1] == ("C2H2_opt.out", "C2H2_sp.out")
        assert pairs[2] == ("CH4_opt.out", "CH4_sp.out")

    def test_match_files_missing_opt(self):
        """opt 文件缺少对应 sp 文件时抛出 ValueError。"""
        sp = ["CH4_sp.out"]
        opt = ["CH4_opt.out", "C_opt.out"]
        with pytest.raises(ValueError, match="没有对应的 sp 文件"):
            match_files_by_prefix(sp, opt)

    def test_ensure_dir(self):
        """ensure_dir 应创建目录并返回绝对路径。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deep", "nested", "dir")
            result = ensure_dir(path)
            assert os.path.isdir(path)
            assert os.path.isabs(result)


# ===================================================================
# CLI 测试
# ===================================================================

class TestCLI:
    def test_version_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--version"])
        assert args.version is True

    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.config is None
        assert args.sp_dir is None
        assert args.opt_dir is None
        assert args.verbose is False

    def test_overrides(self):
        parser = build_parser()
        args = parser.parse_args(["--sp-dir", "./mysp", "--opt-dir", "./myopt", "--verbose"])
        assert args.sp_dir == "./mysp"
        assert args.opt_dir == "./myopt"
        assert args.verbose is True

    def test_apply_cli_overrides(self):
        cfg = ShermoConfig(shermoPath="/test")
        parser = build_parser()
        args = parser.parse_args(["--sp-dir", "./custom_sp", "--output-dir", "./custom_out"])
        apply_cli_overrides(cfg, args)
        assert cfg.spDir == "./custom_sp"
        assert cfg.outputDir == "./custom_out"
        # 未覆盖的字段保持不变
        assert cfg.optDir == "opt"
