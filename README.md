# EasyShermo

EasyShermo 是 Kimariyb 开发的一款全自动批处理 Shermo 的 Python 脚本。Easy Shermo 使用极其简单无脑，可以瞬间用 Shermo 批处理几十个量子化学计算的输出文件。

鉴于 Shermo 已经是一个功能十分强大的科学计算程序了，所以 EasyShermo 也只是提高了 Shermo 的使用效率，并没有做其他的工作。

由于 EasyShermo 开发者 Kimariyb 仅使用 Gaussian 和 Orca 作为计算单点的程序，尽管 Shermo 支持很多量化计算程序，但是 EasyShermo 也只支持 Orca 和 Gaussian 单点任务的自动化。

## 安装

本项目已经开源在 Github 上，您可以通过以下步骤安装 EasyShermo：

1. 首先，您需要确保已经安装了 Python 环境和 pip 包管理工具。如果您还没有安装它们，请先安装它们。

2. 下载 EasyShermo 源代码：
```shell
git clone https://github.com/kimariyb/easy-shermo.git
```

3. 进入 EasyShermo 目录并安装依赖：
```shell
cd easy-shermo
pip install -r requirements.txt
```

## 使用

1. EasyShermo 使用十分简单，在项目中存在一个 `settings.yaml`，使用 EasyShermo 之前，需要配置好 `settings.yaml`。
```yaml
# The path to the Shermo executable file.
shermo_path: "D:\\environment\\Shermo\\Shermo.exe"
# The program for performing a single point calculation task. 1. gaussian; 2. orca
sp_file: 1
# Treatment of low frequencies. 0: Harmonic. 1: Raising low frequencies. 2: Grimme's entropy interpolation
ilow_freq: 2
# Frequency scale factor for ZPE
scl_zpe: 0.9882
# Frequency scale factor for U(T)-U(0) (the same as that for H(T)-H(0))
scl_heat: 1.0062
# Frequency scale factor for S(T)
scl_s: 1.0104
# Frequency scale factor for heat capacity
scl_cv: 1.0
# in K. By specifying lower, upper limits and stepsize, e.g. 50,200,10, it can be scanned
temperature: 298.15
# in atm. By specifying lower, upper limits and stepsize, e.g. 0.5,20,0.1, it can be scanned
pressure: 1.0
```

2. 将 `shermo_path` 配置好以后，分别将单点任务和振动分析任务的输出文件放入 `sp` 和 `opt` 文件夹里。例如，本项目中自带的例子：
```yaml
- sp
  - H3O+_sp.out
  - reaction1_IN_sp.out
  - reaction1_react_sp.out
- opt
  - H3O+_opt.out
  - reaction1_IN_opt.out
  - reaction1_react_opt.out
```

3. 一切准备就绪之后，运行命令启动项目，然后回车。最后可以在 `output` 文件夹下找到输出的 txt 文件。
```shell
python main.py

[Enter]
```

这些 txt 文件名都是和 opt 文件夹里的 out 文件名一样，只是后缀不同。请按照约定分别将 `sp` 文件夹里的单点文件和 `opt` 文件夹里的振动分析文件的文件名设置为统一格式，以免出现莫名的 bug。

```txt
                           ===========================
                           ========== Total ==========
                           ===========================
 Total q(V=0):       1.247127E+032
 Total q(bot):       6.061469E+015
 Total q(V=0)/NA:    2.070903E+008
 Total q(bot)/NA:    1.006531E-008
 Total CV:      27.047 J/mol/K       6.464 cal/mol/K
 Total CP:      35.361 J/mol/K       8.452 cal/mol/K
 Total S:      192.883 J/mol/K      46.100 cal/mol/K    -TS:   -13.745 kcal/mol
 Zero point energy (ZPE):     92.018 kJ/mol     21.993 kcal/mol   0.035048 a.u.
 Thermal correction to U:     99.582 kJ/mol     23.801 kcal/mol   0.037929 a.u.
 Thermal correction to H:    102.061 kJ/mol     24.393 kcal/mol   0.038873 a.u.
 Thermal correction to G:     44.553 kJ/mol     10.648 kcal/mol   0.016969 a.u.
 Electronic energy:        -76.8121509 a.u.
 Sum of electronic energy and ZPE, namely U/H/G at 0 K:        -76.7771031 a.u.
 Sum of electronic energy and thermal correction to U:         -76.7742223 a.u.
 Sum of electronic energy and thermal correction to H:         -76.7732781 a.u.
 Sum of electronic energy and thermal correction to G:         -76.7951817 a.u.
```

**约定大于配置！** 例如，`H3O+_sp.out` 和 `H3O+_opt.out` 就算统一的格式，区别只是 `H3O+` 后面的 `_sp` 和 `_opt`。

## 有关 Shermo

Shermo 是 [Sobereva@北京科音](http://www.keinsci.com/) 开发的一个免费的可以独立运行的计算分子热力学数据的程序，需要从量子化学程序振动分析的输出文件里读取信息来进行计算，计算时基于理想气体假设。如果有对 Shermo 程序不熟悉的，可以浏览以下网址。

- Shermo 的官方网站：[Shermo](http://sobereva.com/soft/shermo/)
- Shermo 的中文教程：[使用Shermo结合量子化学程序方便地计算分子的各种热力学数据](http://sobereva.com/552)
- Shermo 程序的原文：[Shermo: A general code for calculating molecular thermochemistry properties](https://www.sciencedirect.com/science/article/abs/pii/S2210271X21001080)

## 许可证

EasyShermo 基于 MIT 许可证开源。这意味着您可以自由地使用、修改和分发代码。有关更多信息，请参见 LICENSE 文件。

