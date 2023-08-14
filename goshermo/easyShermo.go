package main

import (
	"fmt"
	"gopkg.in/ini.v1"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
)

/*
******************
对应 config.py
******************
*/

// shermoConfig 用来记录 Shermo 的配置信息
type ShermoConfig struct {
	ShermoPath string
	SpFile     string
	Prtvib     string
	T          string
	P          string
	SclZPE     string
	SclHeat    string
	SclS       string
	SclCV      string
	Ilowfreq   string
	Ravib      string
	Imode      string
	Conc       string
	Outshm     string
	Defmass    string
}

func NewShermoConfig() (*ShermoConfig, error) {
	s := &ShermoConfig{}

	// 获取当前工作目录
	currentDir, _ := os.Getwd()

	// 获取 settings.ini 文件的路径
	settingsPath := filepath.Join(currentDir, "settings.ini")

	// 创建 ini config 对象
	cfg, err := ini.Load(settingsPath)
	if err != nil {
		return nil, err
	}

	// 读取配置项
	section := cfg.Section("Shermo")
	s.ShermoPath = section.Key("shermoPath").String()
	s.SpFile = section.Key("spFile").String()
	s.Prtvib = cfg.Section("Shermo").Key("prtvib").String()
	s.T = cfg.Section("Shermo").Key("T").String()
	s.P = cfg.Section("Shermo").Key("P").String()
	s.SclZPE = cfg.Section("Shermo").Key("sclZPE").String()
	s.SclHeat = cfg.Section("Shermo").Key("sclheat").String()
	s.SclS = cfg.Section("Shermo").Key("sclS").String()
	s.SclCV = cfg.Section("Shermo").Key("sclCV").String()
	s.Ilowfreq = cfg.Section("Shermo").Key("ilowfreq").String()
	s.Ravib = cfg.Section("Shermo").Key("ravib").String()
	s.Imode = cfg.Section("Shermo").Key("imode").String()
	s.Conc = cfg.Section("Shermo").Key("conc").String()
	s.Outshm = cfg.Section("Shermo").Key("outshm").String()
	s.Defmass = cfg.Section("Shermo").Key("defmass").String()

	return s, nil
}

func (s *ShermoConfig) String() string {
	return fmt.Sprintf("The ShermoConfig is: shermoPath=%s, spFile=%s, prtvib=%s, T=%s, P=%s, sclZPE=%s, sclheat=%s, "+
		"sclS=%s, sclCV=%s, ilowfreq=%s, ravib=%s, imode=%s, conc=%s, outshm=%s, defmass=%s",
		s.ShermoPath, s.SpFile, s.Prtvib, s.T, s.P, s.SclZPE, s.SclHeat, s.SclS, s.SclCV, s.Ilowfreq, s.Ravib,
		s.Imode, s.Conc, s.Outshm, s.Defmass)
}

/*
******************
对应 easyShermo.py
******************
*/

type results struct {
	FileName string
	Energy   string
}

func GetOrcaEnergy() []results {
	// 创建一个切片用来存放每一个文件对应的 results
	var resultsCollection []results

	// 得到当前文件下的 sp 文件夹下的所有 out 文件名
	filePattern := filepath.Join("sp", "*.out")
	filesName, err := filepath.Glob(filePattern)
	if err != nil {
		fmt.Println("获取文件列表时发生错误:", err)
		return resultsCollection
	}

	// 遍历 filesName 切片，将每一个 results 存放在 resultsCollection 切片中
	for _, fileName := range filesName {
		// 通过 fileName 打开文件
		file, err := os.Open(fileName)
		if err != nil {
			fmt.Println("无法打开文件:", err)
			continue
		}
		defer file.Close()

		// 读取文件内容为 Bytes
		contentsBytes, err := io.ReadAll(file)
		// Bytes 转化为字符串
		contentsString := string(contentsBytes)
		if err != nil {
			fmt.Println("读取文件时发生错误:", err)
			continue
		}

		// 使用正则表达式搜索 orca 单点能
		energyRegex := regexp.MustCompile(`FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)`)

		// 查找匹配的能量值
		matches := energyRegex.FindAllStringSubmatch(string(contentsString), -1)
		if len(matches) > 0 {
			// 查找文件中最后一个匹配项的能量值
			energy := matches[len(matches)-1][1]
			fmt.Println("Energy:", energy)

			// 创建 results 结构体对象
			fileResults := results{
				FileName: fileName,
				Energy:   energy,
			}

			resultsCollection = append(resultsCollection, fileResults)
		} else {
			fmt.Println("未找到能量值:", fileName)
		}
	}

	return resultsCollection
}

/*
******************
对应 main.py
******************
*/
func main() {
	// 版权信息
	versionInfo := map[string]string{
		"version":      "v1.2.1",
		"release_date": "Aug-3-2023",
		"developer":    "Kimariyb, Ryan Hsiun",
		"address":      "XiaMen University, School of Electronic Science and Engineering",
		"website":      "https://github.com/kimariyb/kimariPlot",
	}

	fmt.Println("EasyShermo -- A Go program to automate the use of Shermo")
	fmt.Printf("Version: %s, release date: %s\n", versionInfo["version"], versionInfo["release_date"])
	fmt.Printf("Developer: %s\n", versionInfo["developer"])
	fmt.Printf("Address: %s\n", versionInfo["address"])
	fmt.Printf("EasyShermo home website: %s\n", versionInfo["website"])
	fmt.Println()

	// 读取 ShermoConfig
	shermoConfig, _ := NewShermoConfig()
	fmt.Println(shermoConfig)
	fmt.Println()

	// 将 spFile 转化为 int 类型
	spFileValue, _ := strconv.Atoi(shermoConfig.SpFile)

	// 如果 settings.ini 中设置为 1，则读取 orca

	// 如果 settings.ini 中设置为 2，则读取 orca
	if spFileValue == 2 {
		// 调用 GetOrcaEnergy 函数获取结果
		result := GetOrcaEnergy()
		fmt.Println(result)
	}

}
