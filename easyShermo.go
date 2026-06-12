package main

import (
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

// ---------------------------------------------------------------------------
// 版本信息
// ---------------------------------------------------------------------------

const (
	version   = "v2.0.0"
	developer = "Kimariyb, Ryan Hsiun"
	address   = "XiaMen University, School of Electronic Science and Engineering"
	website   = "https://github.com/kimariyb/easy-shermo"
)

// ---------------------------------------------------------------------------
// 配置文件结构
// ---------------------------------------------------------------------------

// ShermoConfig 映射 config.yaml 的所有字段
type ShermoConfig struct {
	ShermoPath string `yaml:"shermoPath"`
	SpFile     int    `yaml:"spFile"`
	SpDir      string `yaml:"spDir"`
	OptDir     string `yaml:"optDir"`
	OutputDir  string `yaml:"outputDir"`
	Prtvib     int    `yaml:"prtvib"`
	T          string `yaml:"T"`
	P          string `yaml:"P"`
	SclZPE     string `yaml:"sclZPE"`
	SclHeat    string `yaml:"sclheat"`
	SclS       string `yaml:"sclS"`
	SclCV      string `yaml:"sclCV"`
	Ilowfreq   int    `yaml:"ilowfreq"`
	Ravib      string `yaml:"ravib"`
	Intpvib    string `yaml:"intpvib"`
	Imagreal   string `yaml:"imagreal"`
	Imode      int    `yaml:"imode"`
	Conc       string `yaml:"conc"`
	Outshm     int    `yaml:"outshm"`
	Defmass    int    `yaml:"defmass"`
}

func (s *ShermoConfig) String() string {
	return fmt.Sprintf(
		"ShermoConfig(shermoPath=%s, spFile=%d, spDir=%s, optDir=%s, outputDir=%s, "+
			"prtvib=%d, T=%s, P=%s, sclZPE=%s, sclheat=%s, sclS=%s, sclCV=%s, "+
			"ilowfreq=%d, ravib=%s, intpvib=%s, imagreal=%s, imode=%d, conc=%s, "+
			"outshm=%d, defmass=%d)",
		s.ShermoPath, s.SpFile, s.SpDir, s.OptDir, s.OutputDir,
		s.Prtvib, s.T, s.P, s.SclZPE, s.SclHeat, s.SclS, s.SclCV,
		s.Ilowfreq, s.Ravib, s.Intpvib, s.Imagreal, s.Imode, s.Conc,
		s.Outshm, s.Defmass,
	)
}

func defaultConfig() ShermoConfig {
	return ShermoConfig{
		SpDir:     "sp",
		OptDir:    "opt",
		OutputDir: "output",
		SpFile:    1,
		Prtvib:    0,
		T:         "298.15",
		P:         "1.0",
		SclZPE:    "1.0",
		SclHeat:   "1.0",
		SclS:      "1.0",
		SclCV:     "1.0",
		Ilowfreq:  2,
		Ravib:     "100",
		Intpvib:   "100",
		Imagreal:  "20",
		Imode:     0,
		Conc:      "0",
		Outshm:    0,
		Defmass:   3,
	}
}

// ---------------------------------------------------------------------------
// YAML 配置加载
// ---------------------------------------------------------------------------

func loadConfig(path string) (*ShermoConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("读取配置文件失败: %w", err)
	}

	cfg := defaultConfig()
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("解析 YAML 失败: %w", err)
	}

	if cfg.ShermoPath == "" {
		return nil, fmt.Errorf("config.yaml 中 shermoPath 不能为空")
	}
	if cfg.SpFile != 1 && cfg.SpFile != 2 {
		return nil, fmt.Errorf("spFile 只能为 1 (Gaussian) 或 2 (ORCA)，收到 %d", cfg.SpFile)
	}

	return &cfg, nil
}

// ---------------------------------------------------------------------------
// 能量提取
// ---------------------------------------------------------------------------

// energyResult 保存单点能提取结果
type energyResult struct {
	FileName string
	Energy   string
}

// energyPattern 定义一种能量模式及其正则
type energyPattern struct {
	Name  string
	Regex *regexp.Regexp
}

var gaussianPatterns = []energyPattern{
	{"CCSD(T)", regexp.MustCompile(`CCSD\(T\)\s*=\s*(-?\d+\.\d+)`)},
	{"MP2", regexp.MustCompile(`MP2\s*=\s*(-?\d+\.\d+)`)},
	{"HF", regexp.MustCompile(`HF\s*=\s*(-?\d+\.\d+)`)},
}

var orcaPattern = regexp.MustCompile(`FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)`)

// lastMatch 返回正则的最后一个匹配的指定捕获组
func lastMatch(contents string, re *regexp.Regexp, group int) (string, bool) {
	matches := re.FindAllStringSubmatch(contents, -1)
	if len(matches) == 0 {
		return "", false
	}
	last := matches[len(matches)-1]
	if len(last) <= group {
		return "", false
	}
	return last[group], true
}

// extractGaussianEnergy 从 Gaussian 输出中按优先级提取能量
func extractGaussianEnergy(contents string) (string, error) {
	// 压缩空白符，适应 Gaussian 多变的输出格式
	ws := regexp.MustCompile(`\s+`)
	compact := ws.ReplaceAllString(contents, "")

	for _, p := range gaussianPatterns {
		if energy, ok := lastMatch(compact, p.Regex, 1); ok {
			slog.Info("Gaussian 能量", "type", p.Name, "value", energy)
			return energy, nil
		}
	}
	return "", fmt.Errorf("未找到 Gaussian 单点能（尝试了 CCSD(T)、MP2、HF）")
}

// extractOrcaEnergy 从 ORCA 输出中提取能量
func extractOrcaEnergy(contents string) (string, error) {
	if energy, ok := lastMatch(contents, orcaPattern, 1); ok {
		slog.Info("ORCA 能量", "value", energy)
		return energy, nil
	}
	return "", fmt.Errorf("未找到 ORCA 单点能（FINAL SINGLE POINT ENERGY）")
}

// scanEnergies 扫描 spDir 目录下所有文件，提取单点能
func scanEnergies(spDir string, spFile int) ([]energyResult, error) {
	entries, err := os.ReadDir(spDir)
	if err != nil {
		return nil, fmt.Errorf("读取目录 %s 失败: %w", spDir, err)
	}

	var results []energyResult

	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}
		name := entry.Name()
		path := filepath.Join(spDir, name)

		data, err := os.ReadFile(path)
		if err != nil {
			slog.Warn("读取文件失败", "file", name, "error", err)
			continue
		}

		var energy string
		switch spFile {
		case 1:
			energy, err = extractGaussianEnergy(string(data))
		case 2:
			energy, err = extractOrcaEnergy(string(data))
		}
		if err != nil {
			slog.Warn("提取能量失败", "file", name, "error", err)
			continue
		}

		results = append(results, energyResult{FileName: name, Energy: energy})
		slog.Info("单点能", "file", name, "energy", energy)
	}

	return results, nil
}

// ---------------------------------------------------------------------------
// 文件配对（前缀匹配）
// ---------------------------------------------------------------------------

var (
	reSpSuffix  = regexp.MustCompile(`^(.*?)_sp\.[^.]+$`)
	reOptSuffix = regexp.MustCompile(`^(.*?)_opt\.[^.]+$`)
)

// fileStem 提取文件名公共前缀: "CH4_sp.out" → "CH4"
func fileStem(name string) (string, bool) {
	for _, re := range []*regexp.Regexp{reSpSuffix, reOptSuffix} {
		if m := re.FindStringSubmatch(name); m != nil {
			return m[1], true
		}
	}
	return "", false
}

// stemPair 记录一个配对的 (opt文件名, sp文件名)
type stemPair struct {
	Opt, Sp string
}

// matchByPrefix 基于文件名前缀将 sp 和 opt 文件配对
func matchByPrefix(spFiles, optFiles []string) ([]stemPair, error) {
	spIdx := make(map[string]string)
	for _, f := range spFiles {
		if stem, ok := fileStem(f); ok {
			spIdx[stem] = f
		}
	}

	optIdx := make(map[string]string)
	for _, f := range optFiles {
		if stem, ok := fileStem(f); ok {
			optIdx[stem] = f
		}
	}

	// 按 opt 前缀字母序配对
	keys := make([]string, 0, len(optIdx))
	for k := range optIdx {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	var pairs []stemPair
	for _, key := range keys {
		spF, ok := spIdx[key]
		if !ok {
			return nil, fmt.Errorf("opt 文件 '%s' (前缀 '%s') 没有对应的 sp 文件", optIdx[key], key)
		}
		pairs = append(pairs, stemPair{Opt: optIdx[key], Sp: spF})
	}

	// 警告未配对的 sp 文件
	for key, f := range spIdx {
		if _, ok := optIdx[key]; !ok {
			slog.Warn("sp 文件没有对应的 opt 文件，将被忽略", "file", f)
		}
	}

	return pairs, nil
}

// ---------------------------------------------------------------------------
// Shermo 执行引擎
// ---------------------------------------------------------------------------

func buildShermoArgs(cfg *ShermoConfig, optPath, energy string) []string {
	return []string{
		cfg.ShermoPath,
		optPath,
		"-E", energy,
		"-prtvib", fmt.Sprintf("%d", cfg.Prtvib),
		"-T", cfg.T,
		"-P", cfg.P,
		"-sclZPE", cfg.SclZPE,
		"-sclheat", cfg.SclHeat,
		"-sclS", cfg.SclS,
		"-sclCV", cfg.SclCV,
		"-ilowfreq", fmt.Sprintf("%d", cfg.Ilowfreq),
		"-ravib", cfg.Ravib,
		"-intpvib", cfg.Intpvib,
		"-imagreal", cfg.Imagreal,
		"-imode", fmt.Sprintf("%d", cfg.Imode),
		"-conc", cfg.Conc,
		"-outshm", fmt.Sprintf("%d", cfg.Outshm),
		"-defmass", fmt.Sprintf("%d", cfg.Defmass),
	}
}

func runShermo(cfg *ShermoConfig, optPath, energy string) error {
	basename := filepath.Base(optPath)
	stem := strings.TrimSuffix(basename, filepath.Ext(basename))

	// 使用绝对路径，避免 Shermo 内部切换工作目录导致文件查找失败
	absPath, err := filepath.Abs(optPath)
	if err != nil {
		return fmt.Errorf("获取绝对路径失败 [%s]: %w", optPath, err)
	}

	args := buildShermoArgs(cfg, absPath, energy)
	slog.Info("运行 Shermo", "cmd", strings.Join(args, " "))

	cmd := exec.Command(args[0], args[1:]...)
	var stderrBuf strings.Builder
	cmd.Stderr = &stderrBuf
	output, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("Shermo 执行失败 [%s]: %w\n%s", basename, err, stderrBuf.String())
	}

	slog.Info("Shermo 成功完成", "file", basename)

	if err := os.MkdirAll(cfg.OutputDir, 0755); err != nil {
		return fmt.Errorf("创建输出目录失败: %w", err)
	}

	outPath := filepath.Join(cfg.OutputDir, stem+".txt")
	if err := os.WriteFile(outPath, output, 0644); err != nil {
		return fmt.Errorf("写入输出文件失败: %w", err)
	}
	slog.Debug("输出写入", "path", outPath)

	return nil
}

// ---------------------------------------------------------------------------
// 主流程
// ---------------------------------------------------------------------------

func runAll(cfg *ShermoConfig) error {
	// 1. 扫描单点能
	slog.Info("正在扫描单点能文件", "dir", cfg.SpDir)
	energies, err := scanEnergies(cfg.SpDir, cfg.SpFile)
	if err != nil {
		return fmt.Errorf("扫描单点能失败: %w", err)
	}
	if len(energies) == 0 {
		return fmt.Errorf("未从 %s 中读取到任何单点能", cfg.SpDir)
	}

	// 构建能量查找表
	energyMap := make(map[string]string)
	for _, e := range energies {
		energyMap[e.FileName] = e.Energy
	}

	// 2. 扫描 opt 文件
	optEntries, err := os.ReadDir(cfg.OptDir)
	if err != nil {
		return fmt.Errorf("读取目录 %s 失败: %w", cfg.OptDir, err)
	}
	var optFiles []string
	for _, entry := range optEntries {
		if !entry.IsDir() {
			optFiles = append(optFiles, entry.Name())
		}
	}
	if len(optFiles) == 0 {
		return fmt.Errorf("opt 目录为空: %s", cfg.OptDir)
	}

	// 3. 前缀配对
	spNames := make([]string, 0, len(energyMap))
	for k := range energyMap {
		spNames = append(spNames, k)
	}
	pairs, err := matchByPrefix(spNames, optFiles)
	if err != nil {
		return fmt.Errorf("文件配对失败: %w", err)
	}

	// 4. 逐对调用 Shermo
	for _, p := range pairs {
		energy, ok := energyMap[p.Sp]
		if !ok {
			slog.Warn("能量未找到，跳过", "file", p.Sp)
			continue
		}
		optPath := filepath.Join(cfg.OptDir, p.Opt)
		if err := runShermo(cfg, optPath, energy); err != nil {
			slog.Error("执行 Shermo 失败", "file", p.Opt, "error", err)
		}
	}

	slog.Info("全部任务完成")
	return nil
}

// ---------------------------------------------------------------------------
// 入口
// ---------------------------------------------------------------------------

func main() {
	configPath := flag.String("config", "config.yaml", "配置文件路径")
	spDir := flag.String("sp-dir", "", "单点能文件目录（覆盖 config.yaml 中的 spDir）")
	optDir := flag.String("opt-dir", "", "振动分析文件目录（覆盖 config.yaml 中的 optDir）")
	outDir := flag.String("output-dir", "", "输出目录（覆盖 config.yaml 中的 outputDir）")
	showVersion := flag.Bool("version", false, "显示版本信息")
	verbose := flag.Bool("verbose", false, "输出调试日志")
	flag.Parse()

	if *showVersion {
		fmt.Printf("EasyShermo %s\n", version)
		return
	}

	if *verbose {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	cfg, err := loadConfig(*configPath)
	if err != nil {
		slog.Error("配置加载失败", "error", err)
		os.Exit(1)
	}

	// CLI 参数覆盖配置文件
	if *spDir != "" {
		cfg.SpDir = *spDir
	}
	if *optDir != "" {
		cfg.OptDir = *optDir
	}
	if *outDir != "" {
		cfg.OutputDir = *outDir
	}

	// settings.ini 迁移检测
	if _, err := os.Stat("settings.ini"); err == nil {
		fmt.Println("⚠️  检测到旧的 settings.ini，EasyShermo v2 现在使用 config.yaml 作为配置文件。")
		fmt.Println("   请参考 config.yaml 示例创建新配置文件。")
		fmt.Println()
	}

	// 横幅
	fmt.Printf("EasyShermo %s\n", version)
	fmt.Printf("配置文件: %s\n", *configPath)
	fmt.Println(cfg)
	fmt.Println()

	if err := runAll(cfg); err != nil {
		slog.Error("执行失败", "error", err)
		os.Exit(1)
	}

	fmt.Println()
	fmt.Println("Copyright (C) 2023 Kimariyb. All rights reserved.")
	fmt.Printf("Currently timeline: %s\n", time.Now().Format("Jan-02-2006, 15:04:05"))
}
