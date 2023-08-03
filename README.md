# EasyShermo

EasyShermo 是 Kimariyb 开发的一款全自动批处理 Shermo 的 Python 脚本。EasyShermo 使用极其简单无脑，可以瞬间用 Shermo 批处理几十个量子化学计算的输出文件。

鉴于 Shermo 已经是一个功能十分强大的科学计算程序了，所以 EasyShermo 也只是提高了 Shermo 的使用效率，并没有做其他的工作。 EasyShermo 开发者 Kimariyb 仅使用 Gaussian 和 Orca 作为计算单点的程序，尽管 Shermo 支持很多量化计算程序，但是 EasyShermo 也只支持 Orca 和 Gaussian 单点任务的自动化。

<img width="120%" src="https://repobeats.axiom.co/api/embed/d3eead8ca82e74af4f8831c245d4c2152553fbda.svg">

## 安装

本项目已经开源在 Github 上，您可以通过以下步骤安装 EasyShermo：

1. 首先，您需要确保已经安装了 Python 环境和 pip 包管理工具。如果您还没有安装它们，请先安装它们。

2. 下载 EasyShermo 源代码：
```shell
git clone https://github.com/kimariyb/easy-shermo.git
```

## 使用

1. 在使用 EasyShermo 之前，可以根据自己的需要配置好 `settings.ini`，`settings.ini` 中大部分的配置选项和 Shermo 的 `settings.ini` 一致。在使用 EasyShermo 前，必须配置 `settings.ini` 中的 `shermoPath`。

```ini
[Shermo]
; The path to the Shermo executable file.
shermoPath = D:\\environment\\Shermo\\Shermo.exe

; The program for performing a single point calculation task.
; 1. Gaussian
; 2. Orca
spFile = 1

; Printing contribution of each vibrational mode.
; 1: Printing contribution of each vibrational mode.
; -1: Printing to vibcontri.txt.
; 0: Do not print
prtvib = 0

; Temperature in K.
; By specifying lower, upper limits and stepsize, e.g. 50,200,10, it can be scanned
T = 298.15

; Pressure in atm.
; By specifying lower, upper limits and stepsize, e.g. 0.5,20,0.1, it can be scanned
P = 1.0

; Frequency scale factor for ZPE
sclZPE = 1.0

; Frequency scale factor for U(T)-U(0) (the same as that for H(T)-H(0))
sclheat = 1.0

; Frequency scale factor for S(T)
sclS = 1.0

; Frequency scale factor for heat capacity
sclCV = 1.0

; Treatment of low frequencies.
; 0: Harmonic.
; 1: Raising low frequencies.
; 2: Entropy interpolation.
; 3: Entropy and internal energy interpolations
ilowfreq = 2

; Raising lower frequencies to this value (cm^-1) when ilowfreq=1
ravib = 100

; Mode of evaluating thermodynamic quantities.
; 0: Consider all terms.
; 1: Ignore translation and rotation
imode = 0

; If not 0, will calculate variation of Gibbs free energy due to concentration change from present state to the specific state.
; e.g. "conc= 1.5M" and "conc= 2.3atm"
conc = 0

; Exporting .shm file after loading QC program output file.
; 1: Exporting .shm file after loading QC program output file.
; 0: Do not export
outshm = 0

; Default atomic masses used during reading QC program output file.
; 1: Element mass.
; 2: Most abundant isotope.
; 3: Same as the output file
defmass = 3
```

2. 在配置文件中将 `shermoPath` 配置好以后，分别将单点任务和振动分析任务的输出文件放入 `sp` 和 `opt` 文件夹里。同时，根据计算单点使用的程序是 Gaussian 还是 Orca 配置 `spFile` 选项。下面是 EasyShermo 测试文件的示例（单点、优化以及输出文件分别在 `sp/example`、`opt/example` 和 `output/example` 中）

```yaml
- sp
  - C_sp.out
  - C2H2_sp.out
  - C2H4_sp.out
  - CH4_sp.out
  - H2_sp.out
- opt
  - C_opt.out
  - C2H2_opt.out
  - C2H4_opt.out
  - CH4_opt.out
  - H2_opt.out
```

3. 一切准备就绪之后，运行命令启动项目。EasyShermo 首先会扫描 `sp` 目录下的所有文件，并得到单点能。之后通过命令行批量调用 Shermo 执行 `opt` 目录下的文件。最后将 Shermo 输出内容写入到 `output` 文件夹的文本文件中，文件名与 `opt` 中的文件相同。

```shell
python main.py
```

`output` 文件夹里的所有文件的内容，都和单独使用 Shermo 输出的内容一致。

```text
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

**约定**：为了避免出现 `sp` 文件和 `opt` 文件顺序不一致导致的问题，请按照约定分别将单点文件和优化文件的文件名该为 `xxx_sp.out` 和 `xxx_opt.out`。**约定大于配置**！ 


## 有关 Shermo

Shermo 是 [Sobereva@北京科音](http://www.keinsci.com/) 开发的一个免费的可以独立运行的计算分子热力学数据的程序，需要从量子化学程序振动分析的输出文件里读取信息来进行计算，计算时基于理想气体假设。如果有对 Shermo 程序不熟悉的，可以浏览以下网址。

- Shermo 的官方网站：[Shermo](http://sobereva.com/soft/shermo/)
- Shermo 的中文教程：[使用Shermo结合量子化学程序方便地计算分子的各种热力学数据](http://sobereva.com/552)
- Shermo 程序的原文：[Shermo: A general code for calculating molecular thermochemistry properties](https://www.sciencedirect.com/science/article/abs/pii/S2210271X21001080)

## 许可证

EasyShermo 基于 MIT 许可证开源。这意味着您可以自由地使用、修改和分发代码。有关更多信息，请参见 LICENSE 文件。

