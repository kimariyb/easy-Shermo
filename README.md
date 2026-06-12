
# EasyShermo

[🇨🇳 中文文档 → README-Zh.md](README-Zh.md)

> **Automated Batch Processing Tool for Shermo Thermochemistry Calculations**

EasyShermo is a fully-automated batch processing wrapper for [Shermo](http://sobereva.com/soft/shermo/), a thermochemistry data calculator developed by [Sobereva@Beijing Kein Research Center](http://www.keinsci.com/). It instantly processes dozens of quantum chemistry output files through Shermo — extracting single-point energies, pairing them with vibrational frequency analysis files, and running Shermo in batch — all with zero manual intervention.

The project is developed and maintained by **Kimariyb** at **Xiamen University, School of Electronic Science and Engineering**.

---

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Python Version](#python-version)
  - [Go Version](#go-version)
  - [Pre-built Binaries](#pre-built-binaries)
- [Configuration](#configuration)
  - [Configuration File Reference](#configuration-file-reference)
  - [Quick Start Config](#quick-start-config)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Command-Line Interface](#command-line-interface)
  - [File Naming Convention](#file-naming-convention)
  - [Temperature/Pressure Scanning](#temperaturepressure-scanning)
  - [Running with Example Data](#running-with-example-data)
- [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Data Flow](#data-flow)
  - [File Pairing Algorithm](#file-pairing-algorithm)
  - [Energy Extraction Priority](#energy-extraction-priority)
- [Output](#output)
- [Thermochemistry Reference](#thermochemistry-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [About Shermo](#about-shermo)
- [License](#license)

---

## Key Features

- **🚀 Fully Automated Batch Processing** — Process dozens of quantum chemistry output files through Shermo in a single command. No manual per-file invocation.
- **🐍 Python + Go Dual Implementation** — Choose between a Python package (installable via pip) or a standalone Go binary (zero dependencies at runtime).
- **🔬 Gaussian & ORCA Support** — Parse single-point energies from both Gaussian (`.out`/`.log`) and ORCA (`.out`) output files with intelligent extraction strategies.
- **🧩 Convention over Configuration** — Files are auto-paired via filename prefixes (`CH4_sp.out` ↔ `CH4_opt.out`). No manual pairing needed.
- **🌡️ Temperature & Pressure Scanning** — Automatically compute thermochemistry data across a range of temperatures and pressures (e.g., `"50,200,10"` for 50 K to 200 K in 10 K steps).
- **⚙️ Full Shermo Feature Coverage** — All Shermo parameters exposed in a single YAML config file: low-frequency treatments (RRHO, Truhlar, Grimme, Minenkov), frequency scaling factors, concentration effects, and more.
- **📁 Structured Output** — Results are written to a designated output directory with clear file naming (`{stem}.txt`), ready for downstream analysis.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language (Python)** | Python ≥ 3.10 |
| **Language (Go)** | Go 1.22+ |
| **Config Format** | YAML |
| **Python Dependencies** | `pyyaml` |
| **Go Dependencies** | `gopkg.in/yaml.v3` |
| **QC Programs Supported** | Gaussian (via `.out` / `.log`), ORCA (via `.out`) |
| **Thermochemistry Engine** | [Shermo](http://sobereva.com/soft/shermo/) (external) |
| **Testing** | pytest (Python), Go standard testing |
| **Packaging** | setuptools (Python), native binary (Go) |

## How It Works

EasyShermo follows a three-step pipeline:

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  1. Extract      │     │  2. Pair &        │     │  3. Batch          │
│  Single-Point     │ ──→ │  Match            │ ──→ │  Invoke Shermo     │
│  Energies        │     │  Files            │     │                    │
├─────────────────┤     ├──────────────────┤     ├────────────────────┤
│ Scan sp/ dir     │     │ xxx_sp.out  ──→   │     │ For each pair:     │
│ Gaussian:        │     │   xxx_opt.out     │     │   shermo opt.out   │
│  CCSD(T) > MP2   │     │                   │     │   -E energy        │
│  > HF            │     │ Prefix-based      │     │   <all config      │
│ ORCA:            │     │ matching, no      │     │   flags>           │
│  FINAL SINGLE    │     │ order dependency  │     │                    │
│  POINT ENERGY    │     │                   │     │ Output → output/   │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

**Step 1 — Energy Extraction**: Scans all files in the single-point (`sp/`) directory. For Gaussian output, it searches for the highest-level energy in priority order: **CCSD(T)** → **MP2** → **HF**, taking the last occurrence of each. For ORCA output, it extracts `FINAL SINGLE POINT ENERGY`.

**Step 2 — File Pairing**: Scans the vibrational analysis (`opt/`) directory. Matches `xxx_sp.out` ↔ `xxx_opt.out` by extracting the common prefix `xxx`. This is order-independent — files are sorted alphabetically by the opt prefix for deterministic output.

**Step 3 — Batch Shermo Invocation**: For each matched pair, constructs and executes the Shermo command with all parameters from `config.yaml`, then writes the output to `output/{stem}.txt`.

## Prerequisites

Before using EasyShermo, ensure you have the following:

### Required

- **Shermo executable** — Download from the [official Shermo website](http://sobereva.com/soft/shermo/). Add it to your `PATH` or set its path in `config.yaml`.

### For the Python Version

- **Python ≥ 3.10** — With `pip` installed.
- **Quantum Chemistry Output Files** — Completed Gaussian (`.out` / `.log`) or ORCA (`.out`) calculations:
  - **Single-point energy calculations** (put in `sp/` directory)
  - **Vibrational frequency / optimization calculations** (put in `opt/` directory)

### For the Go Version

- **Go 1.22+** (only if building from source)
- **Or just download** the pre-compiled binary from [Releases](https://github.com/kimariyb/easy-Shermo/releases).

### Optional but Recommended

- **Docker** (if you don't want to install Shermo natively — run it via a container)

## Installation

### Python Version

```bash
# Option 1: Run directly from source (no install required)
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
pip install pyyaml
python -m easy_shermo

# Option 2: Install as a system-wide command
pip install .
easy-shermo

# Option 3: Install with symlink (for development)
pip install -e .
```

After installation, verify it works:

```bash
easy-shermo --version
# Output: EasyShermo v2.0.0
```

### Go Version

```bash
git clone https://github.com/kimariyb/easy-shermo.git
cd easy-shermo
go build -o easyShermo ./easyShermo.go
./easyShermo --version
# Output: EasyShermo v2.0.0
```

### Pre-built Binaries

Pre-compiled binaries for Linux, macOS, and Windows are available on the [Releases page](https://github.com/kimariyb/easy-Shermo/releases).

| Platform | Download |
|----------|----------|
| **macOS (Intel)** | `easyShermo-darwin-amd64` |
| **macOS (Apple Silicon)** | `easyShermo-darwin-arm64` |
| **Linux (amd64)** | `easyShermo-linux-amd64` |
| **Windows (amd64)** | `easyShermo.exe` |

Download, make executable (on Unix), and run:

```bash
chmod +x easyShermo-darwin-arm64
./easyShermo-darwin-arm64 --sp-dir ./sp --opt-dir ./opt
```

## Configuration

EasyShermo uses a **YAML** configuration file (`config.yaml`) in the project root. The configuration is found by searching the current working directory and the script's parent directory. You can also specify a custom path with `--config`.

### Configuration File Reference

```yaml
# =============================================================================
# EasyShermo Configuration File (YAML)
# =============================================================================

# Shermo executable path (REQUIRED)
shermoPath: /usr/local/bin/shermo

# Quantum chemistry program type:
#   1 = Gaussian
#   2 = ORCA
spFile: 1

# Directory configuration (can be overridden via --sp-dir / --opt-dir / --output-dir)
spDir: sp          # Directory containing single-point energy files
optDir: opt        # Directory containing vibrational frequency analysis files
outputDir: output  # Directory where Shermo results will be written

# Vibrational contribution printing mode:
#   1  = print to screen
#  -1  = write to vibcontri.txt
#   0  = do not print
prtvib: 0

# Temperature (K) — supports scanning format: "start,end,step"
#   "298.15"      → single temperature
#   "50,200,10"   → 50, 60, 70, ..., 200 K
T: 298.15

# Pressure (atm) — supports scanning format: "start,end,step"
#   "1.0"         → single pressure
#   "0.5,20,0.1"  → 0.5, 0.6, 0.7, ..., 20 atm
P: 1.0

# Frequency scaling factors
sclZPE: 1.0       # Scaling factor for zero-point energy
sclheat: 1.0      # Scaling factor for thermal correction U(T)-U(0)
sclS: 1.0         # Scaling factor for entropy S(T)
sclCV: 1.0        # Scaling factor for heat capacity

# Low-frequency treatment mode:
#   0 = RRHO (rigid rotor-harmonic oscillator approximation)
#   1 = Truhlar's method (raise low frequencies)
#   2 = Grimme's entropy interpolation (recommended)
#   3 = Minenkov's entropy + internal energy interpolation
ilowfreq: 2

# Frequency to which low modes are raised when ilowfreq=1 (cm⁻¹)
ravib: 100

# Frequency threshold for interpolation when ilowfreq=2 or 3 (cm⁻¹)
intpvib: 100

# Imaginary frequencies with absolute value below this threshold (cm⁻¹)
# are treated as real frequencies
imagreal: 20

# Thermochemistry calculation mode:
#   0 = consider all contributions (translational, rotational, vibrational)
#   1 = ignore translational and rotational contributions
imode: 0

# Concentration change for Gibbs free energy correction
# Examples: "conc=1.5M", "conc=2.3atm"
conc: 0

# Export .shm file after loading QC output:
#   1 = export
#   0 = do not export
outshm: 0

# Atomic mass definition:
#   1 = element mass
#   2 = most abundant isotope mass
#   3 = same as the output file
defmass: 3
```

### Quick Start Config

Minimal configuration to get started:

```yaml
shermoPath: /path/to/shermo
spFile: 1               # 1 for Gaussian, 2 for ORCA
```

All other fields use sensible defaults. Override directories via CLI flags.

## Usage

### Basic Usage

```bash
# Python version (from source)
python -m easy_shermo

# Python version (installed)
easy-shermo

# Go version
./easyShermo
```

That's it — EasyShermo will:
1. Read `config.yaml` from the current directory
2. Scan `sp/` for single-point files
3. Scan `opt/` for vibrational analysis files
4. Pair them by filename prefix
5. Run Shermo for each pair
6. Write results to `output/`

### Command-Line Interface

```
Usage: easy_shermo [OPTIONS]

Options:
  --config PATH         Path to configuration file (default: config.yaml in
                        current or parent directory)
  --sp-dir DIR          Override single-point file directory
  --opt-dir DIR         Override vibrational analysis file directory
  --output-dir DIR      Override output directory
  --version             Show version information and exit
  --verbose, -v         Enable debug logging
```

**Examples:**

```bash
# Use a custom config file
easy-shermo --config /path/to/custom/config.yaml

# Override directories (useful for project-specific runs)
easy-shermo --sp-dir ./my_sp --opt-dir ./my_opt --output-dir ./my_output

# Enable verbose debug logging
easy-shermo --verbose

# Go version — identical flags
./easyShermo --sp-dir ./sp --opt-dir ./opt --output-dir ./output --verbose
```

### File Naming Convention

EasyShermo uses a **convention over configuration** approach for file pairing. Files are matched automatically by extracting a common **prefix** from the filename.

```
sp/                         opt/
├── CH4_sp.out      ──→     ├── CH4_opt.out
├── C2H4_sp.out     ──→     ├── C2H4_opt.out
├── C2H2_sp.out     ──→     ├── C2H2_opt.out
├── C_sp.out        ──→     ├── C_opt.out
└── H2_sp.out       ──→     └── H2_opt.out
```

**Naming Rules:**
- Single-point files: `{prefix}_sp.{ext}` (e.g., `CH4_sp.out`, `water_sp.log`)
- Vibrational analysis files: `{prefix}_opt.{ext}` (e.g., `CH4_opt.out`, `water_opt.log`)
- The prefix is **everything before `_sp` or `_opt`**
- File extension doesn't matter (`.out`, `.log`, etc. all work)
- Pairing is **order-independent** — files can be in any order within their directories
- Unpaired files trigger warnings but do not stop execution

> **⚠️ Important**: Each opt file **must** have a corresponding sp file with the same prefix. If a file is named `CH4_opt.out` but no `CH4_sp.out` exists, EasyShermo will raise an error.

### Temperature/Pressure Scanning

EasyShermo supports scanning across a range of temperatures and pressures using a compact format:

```yaml
# Scan temperature from 50 K to 200 K in 10 K steps
T: "50,200,10"
# This generates: 50, 60, 70, 80, ..., 190, 200 K

# Single temperature
T: 298.15

# Scan pressure from 0.5 atm to 20 atm in 0.1 atm steps
P: "0.5,20,0.1"
# This generates: 0.5, 0.6, 0.7, ..., 19.9, 20.0 atm

# Single pressure
P: 1.0
```

Shermo will compute thermochemistry data at every combination, producing results for each (T, P) point.

### Running with Example Data

The repository includes example files for testing:

```bash
# Python version — use example data
python -m easy_shermo --sp-dir sp/example --opt-dir opt/example --output-dir output/example

# Go version
./easyShermo --sp-dir sp/example --opt-dir opt/example --output-dir /tmp/output
```

This processes 5 example molecules (C, H₂, CH₄, C₂H₄, C₂H₂) using Gaussian output files included in the repository, demonstrating the full pipeline.

## Architecture

### Project Structure

```
easy-shermo/
├── easy_shermo/                    # Python package
│   ├── __init__.py                 # Version info (v2.0.0)
│   ├── __main__.py                 # Entry point for `python -m easy_shermo`
│   ├── cli.py                      # Argument parser & CLI entry point
│   ├── config.py                   # YAML configuration loader & validator
│   ├── engine.py                   # Shermo execution engine (builds args, runs)
│   ├── utils.py                    # Utility functions (file matching, directory ops)
│   └── parsers/                    # Single-point energy parsers
│       ├── __init__.py             # Parser ABC & factory (create_parser)
│       ├── gaussian.py             # Gaussian output parser (CCSD(T) > MP2 > HF)
│       └── orca.py                 # ORCA output parser (FINAL SINGLE POINT ENERGY)
├── easyShermo.go                   # Go implementation (standalone binary)
├── config.yaml                     # Default configuration file
├── pyproject.toml                  # Python package metadata & build config
├── tests/
│   └── test_easy_shermo.py         # Unit tests (pytest)
├── sp/                             # Single-point energy files directory
├── opt/                            # Vibrational frequency analysis directory
└── output/                         # Shermo output results directory
```

### Data Flow

```
┌─────────────┐     ┌────────────────────┐     ┌──────────────────────┐
│   User      │     │   Config System    │     │   Execution Engine   │
│             │     │                    │     │                      │
│  config.yaml│────→│  load_config()     │     │  run_all()           │
│  CLI flags  │────→│  apply_overrides() │────→│                      │
└─────────────┘     └────────────────────┘     │  1. Scan sp/ dir     │
                                               │  2. Extract energies │
                    ┌────────────────────┐     │  3. Scan opt/ dir    │
                    │   File Matcher     │     │  4. Pair by prefix   │
                    │                    │     │  5. Run Shermo each  │
                    │  match_by_prefix() │←────│  6. Write output/    │
                    │  _stem()           │     │                      │
                    └────────────────────┘     └──────────────────────┘
                                                          │
                                               ┌──────────▼──────────┐
                                               │   Shermo (external) │
                                               │                     │
                                               │  shermo opt.out     │
                                               │  -E energy          │
                                               │  <config params>    │
                                               └─────────────────────┘
```

### File Pairing Algorithm

The pairing logic is implemented identically in both Python and Go:

1. **Extract stem**: For each filename, apply regex `^(.*?)_sp\.[^.]+$` or `^(.*?)_opt\.[^.]+$`. If matched, the captured group `(.*?)` is the stem (prefix).
2. **Build index**: Create a `{stem → filename}` dictionary for both `sp/` and `opt/` files.
3. **Match**: Iterate over sorted opt stems. For each, look up the corresponding sp stem. If found, create a pair. If not found, raise an error.
4. **Warn**: Any unmatched sp files are logged as warnings but don't stop execution.

```
Input:
  sp/ = [C_sp.out, CH4_sp.out, C2H2_sp.out]
  opt/ = [CH4_opt.out, C2H2_opt.out, C_opt.out]

Step 1 (extract stems):
  sp index:  {C → C_sp.out, CH4 → CH4_sp.out, C2H2 → C2H2_sp.out}
  opt index: {CH4 → CH4_opt.out, C2H2 → C2H2_opt.out, C → C_opt.out}

Step 2 (match by sorted opt stems):
  C     → C_sp.out           → pair (C_opt.out, C_sp.out)
  C2H2  → C2H2_sp.out        → pair (C2H2_opt.out, C2H2_sp.out)
  CH4   → CH4_sp.out         → pair (CH4_opt.out, CH4_sp.out)

Output: [(C_opt.out, C_sp.out), (C2H2_opt.out, C2H2_sp.out), (CH4_opt.out, CH4_sp.out)]
```

### Energy Extraction Priority

**Gaussian:** The parser searches for energies in priority order, taking the **last** occurrence of each level:

| Priority | Energy Level | Regex Pattern |
|----------|-------------|---------------|
| 1 (highest) | CCSD(T) | `CCSD\(T\)\s*=\s*(-?\d+\.\d+)` |
| 2 | MP2 | `MP2\s*=\s*(-?\d+\.\d+)` |
| 3 (fallback) | HF | `HF\s*=\s*(-?\d+\.\d+)` |

All whitespace is removed before matching to handle Gaussian's variable column formatting.

Example Gaussian output snippet:
```
 HF= -100.1234567
 MP2= -100.2345678
 CCSD(T)= -100.3456789     ← This value is extracted
```

**ORCA:** The parser extracts `FINAL SINGLE POINT ENERGY`, also taking the last occurrence:

| Pattern | Example |
|---------|---------|
| `FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)` | `FINAL SINGLE POINT ENERGY -100.1234567` |

## Output

For each processed molecule, EasyShermo writes a `{prefix}.txt` file to the output directory containing Shermo's full output. Here's an example for CH₄:

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

Each output file contains the full Shermo calculation, including:
- **Molecular information** (atoms, masses, point group, rotational constants)
- **Vibrational frequencies** with IR intensities
- **Thermochemistry contributions** (translational, rotational, vibrational, electronic)
- **Sum totals** for internal energy (U), enthalpy (H), Gibbs free energy (G)
- **Heat capacities** (Cᵥ, Cₚ) and **entropy** (S), with correction factors applied

## Thermochemistry Reference

The following thermodynamic quantities are computed by Shermo for each molecule:

| Quantity | Symbol | Units (SI) | Units (cal) | Description |
|----------|--------|-----------|-------------|-------------|
| Zero-Point Energy | ZPE | kJ/mol | kcal/mol | Vibrational zero-point energy |
| Thermal Correction to U | ΔU | kJ/mol | kcal/mol | Internal energy correction |
| Thermal Correction to H | ΔH | kJ/mol | kcal/mol | Enthalpy correction (ΔU + RT) |
| Thermal Correction to G | ΔG | kJ/mol | kcal/mol | Gibbs free energy correction (ΔH - TΔS) |
| Heat Capacity (const V) | Cᵥ | J/(mol·K) | cal/(mol·K) | Isochoric heat capacity |
| Heat Capacity (const P) | Cₚ | J/(mol·K) | cal/(mol·K) | Isobaric heat capacity |
| Entropy | S | J/(mol·K) | cal/(mol·K) | Total entropy |
| Partition Function | q | — | — | Molecular partition function |

## Testing

### Python Version

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test class
pytest tests/test_easy_shermo.py::TestGaussianParser

# Run a specific test
pytest tests/test_easy_shermo.py::TestGaussianParser::test_ccsd_t_energy

# Run with coverage
pip install pytest-cov
pytest --cov=easy_shermo
```

### Go Version

```bash
go test ./...
```

### Test Coverage Areas

| Test Suite | What's Tested |
|-----------|---------------|
| `TestConfig` | YAML loading, validation (spFile, shermoPath), default values, `find_config` |
| `TestGaussianParser` | CCSD(T) extraction, MP2/HF fallback, last-match behavior, real output format |
| `TestOrcaParser` | FINAL SINGLE POINT ENERGY extraction, last-match, no-energy error |
| `TestParserFactory` | Correct parser creation for spFile=1/2, invalid value error |
| `TestUtils` | `_stem()` matching, `match_files_by_prefix()`, orphaned file warnings, `ensure_dir()` |
| `TestCLI` | `--version` flag, argument parsing, CLI overrides |

## Troubleshooting

### "Shermo executable not found" / Empty shermoPath

**Error:**
```
配置加载失败: shermoPath: 不能为空
```

**Solution:** Set the correct path to the Shermo executable in `config.yaml`:
```yaml
shermoPath: /usr/local/bin/shermo   # macOS/Linux
shermoPath: C:\Shermo\Shermo.exe    # Windows
```

Alternatively, add Shermo to your `PATH` and use the full path in the config.

### "No single-point energy found" for Gaussian files

**Error:**
```
未找到 Gaussian 单点能（尝试了 CCSD(T)、MP2、HF）
```

**Solution:** Ensure your Gaussian output file contains one of:
- `CCSD(T)=` (coupled cluster calculation)
- `MP2=` (Møller-Plesset perturbation)
- `HF=` (Hartree-Fock)

If your calculation uses a different method (e.g., DFT/B3LYP), only the HF energy will be available. The parser will try HF as a fallback — verify the output contains `HF=`. For DFT calculations, consider adding custom patterns to the parser.

### "No corresponding sp file" for an opt file

**Error:**
```
ValueError: opt 文件 'CH4_opt.out' (前缀 'CH4') 没有对应的 sp 文件
```

**Solution:** Ensure every `xxx_opt.out` file has a matching `xxx_sp.out` file in the `sp/` directory. Check for typos:
- ✅ `CH4_sp.out` ↔ `CH4_opt.out`
- ❌ `CH4_sp.out` ↔ `CH4-opt.out` (underscore vs. hyphen)
- ❌ `CH4_sp.out` ↔ `CH4_opt.log` (still OK — extension doesn't matter)
- ❌ `CH4_SP.OUT` ↔ `CH4_opt.out` (wrong case convention)

### "Energy not found" for ORCA files

**Error:**
```
未找到 ORCA 单点能（FINAL SINGLE POINT ENERGY）
```

**Solution:** ORCA output must contain `FINAL SINGLE POINT ENERGY`. Check that:
1. The calculation is a single-point energy calculation (not just optimization)
2. The calculation completed successfully
3. You are using ORCA output files, not Gaussian files (set `spFile: 2`)

### Shermo execution fails

**Error:**
```
Shermo 执行失败 [...]: exit status 1
```

**Solution:**
1. Verify Shermo works standalone: `shermo /path/to/opt.out`
2. Check that the opt file is a valid Gaussian/ORCA output with frequencies
3. Ensure the energy value extracted from the sp file is valid (not `NaN`, `****`, etc.)
4. Run with `--verbose` for detailed logging

### Missing output files

**Symptom:** No files appear in the output directory.

**Solution:**
1. Check the output directory was created: `ls -la output/`
2. Run with `--verbose` to see detailed logs
3. Verify file permissions: the user running EasyShermo must have write access
4. Check disk space

### V2 migration from settings.ini

**Symptom:**
```
⚠️ 检测到旧的 settings.ini，EasyShermo v2 现在使用 config.yaml 作为配置文件。
```

**Solution:** EasyShermo v2 replaces the old `settings.ini` with `config.yaml` (YAML format). Create a new `config.yaml` based on the template above. Key differences:
- YAML uses `key: value` instead of `KEY=VALUE`
- Section headers (`[settings]`) are no longer used
- String values should be quoted if they contain special characters

## About Shermo

[Shermo](http://sobereva.com/soft/shermo/) is a standalone program for calculating molecular thermochemistry data, developed by **Tian Lu (Sobereva)** at the **Beijing Kein Research Center for Natural Sciences**. It is widely used in the computational chemistry community for computing thermodynamic corrections from quantum chemistry output files.

**Key Shermo Resources:**
- [Official Website](http://sobereva.com/soft/shermo/) — Download the latest version
- [Chinese Tutorial: Using Shermo with Quantum Chemistry Programs](http://sobereva.com/552) — Comprehensive guide (in Chinese)
- [Original Paper](https://www.sciencedirect.com/science/article/abs/pii/S2210271X21001080) — Tian Lu, Qinxue Chen, *Computational and Theoretical Chemistry*, 1200, 113249 (2021)

**How to cite Shermo in your work:**

> Tian Lu, Qinxue Chen, Shermo: A general code for calculating molecular thermodynamic properties, *Comput. Theor. Chem.*, 1200, 113249 (2021). DOI: [10.1016/j.comptc.2021.113249](https://doi.org/10.1016/j.comptc.2021.113249)

## License

EasyShermo is open-source software released under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2023 Kimariyb. All rights reserved.


