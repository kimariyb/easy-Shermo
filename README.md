# EasyShermo

<img width="120%" src="https://repobeats.axiom.co/api/embed/d3eead8ca82e74af4f8831c245d4c2152553fbda.svg">

EasyShermo 是 Kimariyb 开发的一款全自动批处理 Shermo 的自动化工具。它可以瞬间用 Shermo 批量处理几十个量子化学计算的输出文件，支持 Python 和 Go 两种版本。

EasyShermo 支持 Gaussian 和 ORCA 两种量子化学程序单点任务的热力学数据批处理。

## 安装

### Python 版本

```shell
# 方式一：直接从源码运行
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
pip install pyyaml
python -m easy_shermo

# 方式二：安装到系统
pip install .
easy-shermo
```

### Go 版本

```shell
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
go build -o easyShermo ./easyShermo.go
./easyShermo
```

也可以前往 [Releases](https://github.com/kimariyb/easy-Shermo/releases) 下载预编译的二进制文件。

## 配置文件

EasyShermo 使用 YAML 格式的配置文件（`config.yaml`），替代了旧的 `settings.ini`。

```yaml
# Shermo 可执行文件路径（必填）
shermoPath: /usr/local/bin/shermo

# 量子化学程序类型: 1 = Gaussian, 2 = ORCA
spFile: 1

# 目录配置（可通过命令行 --sp-dir / --opt-dir / --output-dir 覆盖）
spDir: sp
optDir: opt
outputDir: output

# 温度 (K)，支持扫描格式如 "50,200,10"
T: 298.15

# 压强 (atm)，支持扫描格式如 "0.5,20,0.1"
P: 1.0

# 频率校正因子
sclZPE: 1.0
sclheat: 1.0
sclS: 1.0
sclCV: 1.0

# 低频处理: 0=谐振, 1=提高低频, 2=熵插值, 3=熵+内能插值
ilowfreq: 2

# ilowfreq=1 时低频提升到的值 (cm⁻¹)
ravib: 100

# 更多配置项参见完整 config.yaml
```

## 使用

### 基本用法

```shell
# Python 版本
python -m easy_shermo

# Go 版本
./easyShermo
```

### 命令行参数

```shell
# 指定配置文件
python -m easy_shermo --config /path/to/config.yaml

# 覆盖目录配置
python -m easy_shermo --sp-dir ./my_sp --opt-dir ./my_opt --output-dir ./my_output

# 显示调试日志
python -m easy_shermo --verbose

# 查看版本
python -m easy_shermo --version
```

Go 版本参数相同：

```shell
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

**约定大于配置**：请将单点文件命名为 `xxx_sp.out`，振动分析文件命名为 `xxx_opt.out`。配对基于前缀 `xxx`，**不依赖文件顺序**。

### 示例

```shell
# 使用示例数据测试（Python）
python -m easy_shermo --sp-dir sp/example --opt-dir opt/example --output-dir output/example

# 使用示例数据测试（Go）
./easyShermo --sp-dir sp/example --opt-dir opt/example --output-dir /tmp/output
```

`output` 目录中的输出内容与单独使用 Shermo 输出的内容一致：

```
                           ===========================
                           ========== Total ==========
                           ===========================
 Total q(V=0):       2.951881E+030
 Total q(bot):       2.951881E+030
 Total q(V=0)/NA:    4.901713E+006
 Total q(bot)/NA:    4.901713E+006
 Total CV:      12.472 J/mol/K       2.981 cal/mol/K
 Total CP:      20.786 J/mol/K       4.968 cal/mol/K
 Total S:      148.871 J/mol/K      35.581 cal/mol/K    -TS:   -10.609 kcal/mol
 Zero point energy (ZPE):      0.000 kJ/mol      0.000 kcal/mol   0.000000 a.u.
 Thermal correction to U:      3.718 kJ/mol      0.889 kcal/mol   0.001416 a.u.
 Thermal correction to H:      6.197 kJ/mol      1.481 kcal/mol   0.002360 a.u.
 Thermal correction to G:    -38.189 kJ/mol     -9.127 kcal/mol  -0.014545 a.u.
 Electronic energy:        -37.7865397 a.u.
 Sum of electronic energy and ZPE, namely U/H/G at 0 K:        -37.7865397 a.u.
 Sum of electronic energy and thermal correction to U:         -37.7851234 a.u.
 Sum of electronic energy and thermal correction to H:         -37.7841792 a.u.
 Sum of electronic energy and thermal correction to G:         -37.8010850 a.u.
```

## 有关 Shermo

Shermo 是 [Sobereva@北京科音](http://www.keinsci.com/) 开发的独立计算分子热力学数据的程序。更多信息：

- [Shermo 官方网站](http://sobereva.com/soft/shermo/)
- [中文教程：使用 Shermo 结合量子化学程序计算分子热力学数据](http://sobereva.com/552)
- [Shermo 原文](https://www.sciencedirect.com/science/article/abs/pii/S2210271X21001080)

## 项目结构

```
easy-shermo/
├── easy_shermo/          # Python 包
│   ├── __init__.py       # 版本信息
│   ├── __main__.py       # python -m 入口
│   ├── cli.py            # 命令行接口
│   ├── config.py         # YAML 配置解析
│   ├── engine.py         # Shermo 执行引擎
│   ├── utils.py          # 工具函数（文件配对等）
│   └── parsers/          # 单点能解析器
│       ├── __init__.py
│       ├── gaussian.py   # Gaussian 解析器
│       └── orca.py       # ORCA 解析器
├── easyShermo.go         # Go 版本
├── config.yaml           # 配置文件
├── pyproject.toml         # 项目元数据
├── tests/                # 测试
│   └── test_easy_shermo.py
├── sp/                   # 单点能文件目录
├── opt/                  # 振动分析文件目录
└── output/               # 输出目录
```

## 许可证

EasyShermo 基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。
