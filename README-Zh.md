
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://repobeats.axiom.co/api/embed/d3eead8ca82e74af4f8831c245d4c2152553fbda.svg">
    <img src="https://repobeats.axiom.co/api/embed/d3eead8ca82e74af4f8831c245d4c2152553fbda.svg" width="100%" alt="仓库活动图">
  </picture>
</p>

# EasyShermo

> **全自动批处理 Shermo 热力学计算工具**

[🇬🇧 English Documentation](README.md)

EasyShermo 是由 **Kimariyb** 和 **Ryan Hsiun**（厦门大学电子科学与技术学院）开发的全自动批处理 [Shermo](http://sobereva.com/soft/shermo/) 的自动化工具。它可以瞬间用 Shermo 批量处理几十个量子化学计算的输出文件——自动提取单点能、与振动分析文件配对、批量调用 Shermo——全程无需人工干预。

---

## 目录

- [功能特性](#功能特性)
- [安装](#安装)
  - [Python 版本](#python-版本)
  - [Go 版本](#go-版本)
  - [预编译二进制文件](#预编译二进制文件)
- [配置文件](#配置文件)
- [使用](#使用)
  - [基本用法](#基本用法)
  - [命令行参数](#命令行参数)
  - [文件命名约定](#文件命名约定)
  - [温度和压强扫描](#温度和压强扫描)
  - [使用示例数据](#使用示例数据)
  - [能量提取优先级](#能量提取优先级)
- [项目结构](#项目结构)
- [测试](#测试)
- [故障排查](#故障排查)
- [关于 Shermo](#关于-shermo)
- [许可证](#许可证)

---

## 功能特性

- **🚀 全自动批处理** — 一条命令批处理数十个量子化学输出文件，无需逐个手动调用 Shermo。
- **🐍 Python + Go 双实现** — 可选择 Python 包（pip 安装）或独立的 Go 二进制文件（运行时零依赖）。
- **🔬 Gaussian 和 ORCA 支持** — 支持从 Gaussian（`.out`/`.log`）和 ORCA（`.out`）输出文件中智能提取单点能。
- **🧩 约定大于配置** — 通过文件名前缀自动配对文件（`CH4_sp.out` ↔ `CH4_opt.out`），无需手动配对。
- **🌡️ 温度和压强扫描** — 支持在温度/压强范围内自动计算热力学数据（如 `"50,200,10"` 表示 50 K 到 200 K，步长 10 K）。
- **⚙️ 完整的 Shermo 功能覆盖** — 所有 Shermo 参数通过单个 YAML 配置文件暴露：低频处理方法（RRHO、Truhlar、Grimme、Minenkov）、频率校正因子、浓度效应等。
- **📁 结构化输出** — 结果写入指定输出目录，文件命名清晰（`{前缀}.txt`），便于后续分析。

## 安装

### Python 版本

```bash
# 方式一：直接从源码运行（无需安装）
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
pip install pyyaml
python -m easy_shermo

# 方式二：安装到系统
pip install .
easy-shermo

# 方式三：开发模式安装（符号链接）
pip install -e .
```

安装后验证：

```bash
easy-shermo --version
# 输出: EasyShermo v2.0.0
```

### Go 版本

```bash
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
go build -o easyShermo ./easyShermo.go
./easyShermo --version
# 输出: EasyShermo v2.0.0
```

### 预编译二进制文件

Linux、macOS 和 Windows 的预编译二进制文件可在 [Releases 页面](https://github.com/kimariyb/easy-Shermo/releases) 下载。

| 平台 | 下载 |
|------|------|
| **macOS (Intel)** | `easyShermo-darwin-amd64` |
| **macOS (Apple Silicon)** | `easyShermo-darwin-arm64` |
| **Linux (amd64)** | `easyShermo-linux-amd64` |
| **Windows (amd64)** | `easyShermo.exe` |

下载后赋予执行权限并运行：

```bash
chmod +x easyShermo-darwin-arm64
./easyShermo-darwin-arm64 --sp-dir ./sp --opt-dir ./opt
```

## 配置文件

EasyShermo 使用 YAML 格式的配置文件（`config.yaml`），替换了旧版的 `settings.ini`。程序会依次在当前目录和脚本所在目录的父目录中查找。也可通过 `--config` 参数指定路径。

```yaml
# =============================================================================
# EasyShermo 配置文件 (YAML 格式)
# =============================================================================

# Shermo 可执行文件路径（必填）
shermoPath: /usr/local/bin/shermo

# 量子化学程序类型: 1 = Gaussian, 2 = ORCA
spFile: 1

# 目录配置（可通过 --sp-dir / --opt-dir / --output-dir 覆盖）
spDir: sp           # 单点能文件目录
optDir: opt         # 振动分析文件目录
outputDir: output   # 输出目录

# 振动贡献打印模式:
#   1  = 屏幕打印
#  -1  = 写入 vibcontri.txt
#   0  = 不打印
prtvib: 0

# 温度 (K)，支持扫描格式: "起始,结束,步长"
#   "298.15"      → 单温度
#   "50,200,10"   → 50, 60, 70, ..., 200 K
T: 298.15

# 压强 (atm)，支持扫描格式: "起始,结束,步长"
#   "1.0"         → 单压强
#   "0.5,20,0.1"  → 0.5, 0.6, 0.7, ..., 20 atm
P: 1.0

# 频率校正因子
sclZPE: 1.0       # ZPE 校正因子
sclheat: 1.0      # U(T)-U(0) 校正因子
sclS: 1.0         # S(T) 校正因子
sclCV: 1.0        # 热容校正因子

# 低频处理模式:
#   0 = 谐振近似 (RRHO)
#   1 = 提高低频 (Truhlar)
#   2 = 熵插值 (Grimme，推荐)
#   3 = 熵和内能插值 (Minenkov)
ilowfreq: 2

# ilowfreq=1 时将低频提升至此值 (cm⁻¹)
ravib: 100

# ilowfreq=2/3 时插值使用的频率阈值 (cm⁻¹)
intpvib: 100

# 绝对值小于此值 (cm⁻¹) 的虚频被视为实频
imagreal: 20

# 热力学计算模式:
#   0 = 考虑所有项（平动、转动、振动）
#   1 = 忽略平动和转动贡献
imode: 0

# 浓度变化引起的吉布斯自由能变
# 示例: "conc=1.5M", "conc=2.3atm"
conc: 0

# 加载 QC 输出文件后导出 .shm 文件:
#   1 = 导出, 0 = 不导出
outshm: 0

# 原子质量定义:
#   1 = 元素质量
#   2 = 最丰同位素质量
#   3 = 同输出文件
defmass: 3
```

## 使用

### 基本用法

```bash
# Python 版本（从源码运行）
python -m easy_shermo

# Python 版本（已安装）
easy-shermo

# Go 版本
./easyShermo
```

执行后 EasyShermo 会自动：
1. 读取当前目录下的 `config.yaml`
2. 扫描 `sp/` 目录中的单点能文件
3. 扫描 `opt/` 目录中的振动分析文件
4. 通过文件名前缀进行配对
5. 对每一对运行 Shermo
6. 将结果写入 `output/` 目录

### 命令行参数

```
用法: easy_shermo [选项]

选项:
  --config PATH         配置文件路径（默认: 当前或父目录下的 config.yaml）
  --sp-dir DIR          覆盖单点能文件目录
  --opt-dir DIR         覆盖振动分析文件目录
  --output-dir DIR      覆盖输出目录
  --version             显示版本信息并退出
  --verbose, -v         输出调试日志
```

**示例：**

```bash
# 指定配置文件
easy-shermo --config /path/to/custom/config.yaml

# 覆盖目录
easy-shermo --sp-dir ./my_sp --opt-dir ./my_opt --output-dir ./my_output

# 启用调试日志
easy-shermo --verbose

# Go 版本参数相同
./easyShermo --sp-dir ./sp --opt-dir ./opt --output-dir ./output --verbose
```

### 文件命名约定

EasyShermo 通过文件名前缀自动配对单点文件和振动分析文件：

```
sp/                     opt/
├── CH4_sp.out    ──→   ├── CH4_opt.out
├── C2H4_sp.out   ──→   ├── C2H4_opt.out
├── C2H2_sp.out   ──→   ├── C2H2_opt.out
├── C_sp.out      ──→   ├── C_opt.out
└── H2_sp.out     ──→   └── H2_opt.out
```

**命名规则：**
- 单点文件：`{前缀}_sp.{扩展名}`（如 `CH4_sp.out`、`water_sp.log`）
- 振动分析文件：`{前缀}_opt.{扩展名}`（如 `CH4_opt.out`、`water_opt.log`）
- 前缀是文件名中 `_sp` 或 `_opt` 之前的部分
- 文件扩展名不限（`.out`、`.log` 等均可）
- 配对**不依赖文件顺序**
- 未能配对的 sp 文件会触发警告，但不会停止执行

> **⚠️ 重要**：每个 opt 文件**必须**有同前缀的 sp 文件。如果存在 `CH4_opt.out` 但不存在 `CH4_sp.out`，EasyShermo 会报错。

### 温度和压强扫描

EasyShermo 支持使用紧凑格式扫描温度和压强范围：

```yaml
# 温度从 50 K 到 200 K，步长 10 K
T: "50,200,10"
# 生成：50, 60, 70, 80, ..., 190, 200 K

# 单温度
T: 298.15

# 压强从 0.5 atm 到 20 atm，步长 0.1 atm
P: "0.5,20,0.1"
# 生成：0.5, 0.6, 0.7, ..., 19.9, 20.0 atm

# 单压强
P: 1.0
```

Shermo 会为每个 (T, P) 组合计算热力学数据。

### 使用示例数据

仓库中包含了用于测试的示例数据：

```bash
# Python 版本
python -m easy_shermo --sp-dir sp/example --opt-dir opt/example --output-dir output/example

# Go 版本
./easyShermo --sp-dir sp/example --opt-dir opt/example --output-dir /tmp/output
```

这将对 5 个示例分子（C、H₂、CH₄、C₂H₄、C₂H₂）使用仓库中附带的 Gaussian 输出文件进行处理，展示完整的运行流程。

### 能量提取优先级

**Gaussian 输出文件** — 按优先级提取，取文件中的**最后一个**匹配值：

| 优先级 | 能量级别 | 正则表达式 |
|--------|---------|-----------|
| 1（最高） | CCSD(T) | `CCSD\(T\)\s*=\s*(-?\d+\.\d+)` |
| 2 | MP2 | `MP2\s*=\s*(-?\d+\.\d+)` |
| 3（回退） | HF | `HF\s*=\s*(-?\d+\.\d+)` |

匹配前会移除所有空白字符，以应对 Gaussian 多变的列格式。

Gaussian 输出示例：
```
 HF= -100.1234567
 MP2= -100.2345678
 CCSD(T)= -100.3456789     ← 提取此值
```

**ORCA 输出文件** — 提取 `FINAL SINGLE POINT ENERGY` 的最后一个值：

| 正则表达式 | 示例 |
|-----------|------|
| `FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)` | `FINAL SINGLE POINT ENERGY -100.1234567` |

## 项目结构

```
easy-shermo/
├── easy_shermo/          # Python 包
│   ├── __init__.py       # 版本信息 (v2.0.0)
│   ├── __main__.py       # python -m 入口
│   ├── cli.py            # 命令行接口
│   ├── config.py         # YAML 配置解析与校验
│   ├── engine.py         # Shermo 执行引擎
│   ├── utils.py          # 工具函数（文件配对等）
│   └── parsers/          # 单点能解析器
│       ├── __init__.py   # 解析器基类与工厂
│       ├── gaussian.py   # Gaussian 解析器
│       └── orca.py       # ORCA 解析器
├── easyShermo.go         # Go 实现（独立二进制）
├── config.yaml           # 默认配置文件
├── pyproject.toml        # Python 包元数据与构建配置
├── tests/
│   └── test_easy_shermo.py  # 单元测试 (pytest)
├── sp/                   # 单点能文件目录
│   └── example/          # 示例数据
├── opt/                  # 振动分析文件目录
│   └── example/          # 示例数据
└── output/               # Shermo 输出结果目录
    └── example/          # 示例输出
```

## 测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 运行指定测试类
pytest tests/test_easy_shermo.py::TestGaussianParser

# 运行指定测试
pytest tests/test_easy_shermo.py::TestGaussianParser::test_ccsd_t_energy

# 带覆盖率运行
pip install pytest-cov
pytest --cov=easy_shermo
```

## 故障排查

### "Shermo 可执行文件未找到" / shermoPath 为空

**错误：**
```
配置加载失败: shermoPath: 不能为空
```

**解决：** 在 `config.yaml` 中设置 Shermo 可执行文件的正确路径：
```yaml
shermoPath: /usr/local/bin/shermo   # macOS/Linux
shermoPath: C:\Shermo\Shermo.exe    # Windows
```

### Gaussian 文件"未找到单点能"

**错误：**
```
未找到 Gaussian 单点能（尝试了 CCSD(T)、MP2、HF）
```

**解决：** 确保 Gaussian 输出文件中包含以下之一：
- `CCSD(T)=`（耦合簇计算）
- `MP2=`（Møller-Plesset 微扰）
- `HF=`（Hartree-Fock）

DFT 计算只有 HF 能量可用，解析器会回退到 HF。

### "没有对应的 sp 文件"

**错误：**
```
ValueError: opt 文件 'CH4_opt.out' (前缀 'CH4') 没有对应的 sp 文件
```

**解决：** 确保每个 `xxx_opt.out` 文件在 `sp/` 目录中有对应的 `xxx_sp.out` 文件：
- ✅ `CH4_sp.out` ↔ `CH4_opt.out`
- ❌ `CH4_sp.out` ↔ `CH4-opt.out`（下划线 vs. 连字符）

### ORCA 文件"能量未找到"

**错误：**
```
未找到 ORCA 单点能（FINAL SINGLE POINT ENERGY）
```

**解决：** 确认是单点能计算（而非仅优化）、计算已成功完成、且文件为 ORCA 输出（设置 `spFile: 2`）。

### Shermo 执行失败

**错误：**
```
Shermo 执行失败 [...]: exit status 1
```

**解决：** 先单独执行 Shermo 验证：`shermo /path/to/opt.out`；确保 opt 文件中包含频率信息；使用 `--verbose` 查看详细日志。

### V2 从 settings.ini 迁移

**提示：**
```
⚠️ 检测到旧的 settings.ini，EasyShermo v2 现在使用 config.yaml 作为配置文件。
```

**解决：** EasyShermo v2 改用 YAML 格式的 `config.yaml`。请参考本页面中的配置示例创建新的配置文件。

## 关于 Shermo

[Shermo](http://sobereva.com/soft/shermo/) 是由 **北京科音自然科学研究中心** 的 **卢天 (Sobereva)** 开发的独立计算分子热力学数据的程序，在计算化学领域被广泛使用。

**相关资源：**
- [Shermo 官方网站](http://sobereva.com/soft/shermo/) — 下载最新版本
- [中文教程：使用 Shermo 结合量子化学程序计算分子热力学数据](http://sobereva.com/552) — 详细使用指南
- [Shermo 原文](https://www.sciencedirect.com/science/article/abs/pii/S2210271X21001080) — Tian Lu, Qinxue Chen, *Computational and Theoretical Chemistry*, 1200, 113249 (2021)

**引用 Shermo：**

> Tian Lu, Qinxue Chen, Shermo: A general code for calculating molecular thermodynamic properties, *Comput. Theor. Chem.*, 1200, 113249 (2021). DOI: [10.1016/j.comptc.2021.113249](https://doi.org/10.1016/j.comptc.2021.113249)

## 许可证

EasyShermo 基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

Copyright (c) 2023 Kimariyb. All rights reserved.
