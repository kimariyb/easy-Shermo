package main

import (
	"fmt"
	"gopkg.in/ini.v1"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

/*
EasyShermo 是厦门大学 Kimariyb 开发的一款全自动批处理使用 Shermo 计算热力学量的 Go 语言程序

@Name: EasyShermo
@Author: Kimariyb
@Institution: XiaMen University
@Data: 2023-09-12
*/

/*
******************
对应 config.py
******************
*/

// ShermoConfig 用来记录 Shermo 的配置信息
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
	section := cfg.Section("")
	s.ShermoPath = section.Key("shermoPath").String()
	s.SpFile = section.Key("spFile").String()
	s.Prtvib = section.Key("prtvib").String()
	s.T = section.Key("T").String()
	s.P = section.Key("P").String()
	s.SclZPE = section.Key("sclZPE").String()
	s.SclHeat = section.Key("sclheat").String()
	s.SclS = section.Key("sclS").String()
	s.SclCV = section.Key("sclCV").String()
	s.Ilowfreq = section.Key("ilowfreq").String()
	s.Ravib = section.Key("ravib").String()
	s.Imode = section.Key("imode").String()
	s.Conc = section.Key("conc").String()
	s.Outshm = section.Key("outshm").String()
	s.Defmass = section.Key("defmass").String()

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

func FindLastMatch(contents string, regex *regexp.Regexp, groupIndex int) (string, error) {
	// 使用正则表达式在字符串中查找所有匹配项
	matches := regex.FindAllStringSubmatch(contents, -1)
	// 获取第二个匹配项
	if len(matches) >= 2 {
		secondMatch := matches[1]
		if len(secondMatch) > groupIndex {
			return secondMatch[groupIndex], nil
		}
	}
	return "", fmt.Errorf("No energy found")
}

func GetGaussianEnergy() []results {
	// 创建一个切片用来存放每一个文件对应的 results
	var resultsCollection []results

	// 得到当前文件下的 sp 文件夹下的所有 out 文件名
	filePattern := filepath.Join("sp", "*.out")
	filesName, err := filepath.Glob(filePattern)
	if err != nil {
		fmt.Println("Error: failed to get files from directory", err)
		return resultsCollection
	}
	// 遍历 filesName 切片，将每一个 results 存放在 resultsCollection 切片中
	for _, fileName := range filesName {
		// 通过 fileName 打开文件
		file, err := os.Open(fileName)
		if err != nil {
			fmt.Println("Error: Unable to open the file", err)
			continue
		}
		defer file.Close()

		// 读取文件内容为 Bytes
		contentsBytes, err := io.ReadAll(file)
		// Bytes 转化为字符串
		contentsString := string(contentsBytes)
		// 替换空格
		re := regexp.MustCompile(`\s+`)
		contentsString = re.ReplaceAllString(contentsString, "")

		if err != nil {
			fmt.Println("Error: Failed to read", err)
			continue
		}

		// 使用正则表达式搜索 gaussian 单点能
		ccsdTRegex := regexp.MustCompile(`CCSD\(T\)=\s*(-?\d+\.\d+)`)
		mp2Regex := regexp.MustCompile(`MP2=\s*(-?\d+\.\d+)`)
		hfRegex := regexp.MustCompile(`HF=\s*(-?\d+\.\d+)`)

		// 首先匹配是否存在 CCSD(T) 的能量，如果存在则直接读取，并将结果保存在 results 中
		ccsdTEnergy, err := FindLastMatch(contentsString, ccsdTRegex, 1)
		if err == nil {
			fileResults := results{
				FileName: fileName,
				Energy:   ccsdTEnergy,
			}
			fmt.Println("The Single Point Energy [CCSD(T)] of " + fileName + " is : " + ccsdTEnergy)

			resultsCollection = append(resultsCollection, fileResults)
			continue
		}
		// 如果不存在 CCSD(T) 的能量，但是存在 MP2 能量，则将 MP2 结果保存在 results 中
		mp2Energy, err := FindLastMatch(contentsString, mp2Regex, 1)
		if err == nil {
			fileResults := results{
				FileName: fileName,
				Energy:   mp2Energy,
			}
			fmt.Println("The Single Point Energy [MP2] of " + fileName + " is : " + mp2Energy)

			resultsCollection = append(resultsCollection, fileResults)
			continue
		}
		// 如果不存在 CCSD(T) 和 MP2 的能量，但是存在 HF 能量，则将 HF 结果保存在 results 中
		hfEnergy, err := FindLastMatch(contentsString, hfRegex, 1)
		if err == nil {
			fileResults := results{
				FileName: fileName,
				Energy:   hfEnergy,
			}
			fmt.Println("The Single Point Energy [HF] of " + fileName + " is : " + mp2Energy)
			resultsCollection = append(resultsCollection, fileResults)
			continue
		}

		fmt.Println("No energy found", fileName)
	}

	return resultsCollection
}

func GetOrcaEnergy() []results {
	// 创建一个切片用来存放每一个文件对应的 results
	var resultsCollection []results

	// 得到当前文件下的 sp 文件夹下的所有 out 文件名
	filePattern := filepath.Join("sp", "*.out")
	filesName, err := filepath.Glob(filePattern)
	if err != nil {
		fmt.Println("Error: failed to get files from directory", err)
		return resultsCollection
	}

	// 遍历 filesName 切片，将每一个 results 存放在 resultsCollection 切片中
	for _, fileName := range filesName {
		// 通过 fileName 打开文件
		file, err := os.Open(fileName)
		if err != nil {
			fmt.Println("Error: Unable to open the file", err)
			continue
		}
		defer file.Close()

		// 读取文件内容为 Bytes
		contentsBytes, err := io.ReadAll(file)
		// Bytes 转化为字符串
		contentsString := string(contentsBytes)
		if err != nil {
			fmt.Println("Error: Failed to read", err)
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
			fmt.Println("No energy found", fileName)
		}
	}

	return resultsCollection
}

func RunShermo(config *ShermoConfig, filePath string, energy string) {
	// 获取文件名和输出文件夹路径
	file := filepath.Base(filePath)
	fileName := strings.TrimSuffix(file, filepath.Ext(file))
	outputDir := filepath.Join(".", "output")
	// 得到 file 文件的绝对路径
	absPath, err := filepath.Abs(filePath)

	// 运行 Shermo 程序所需要的参数
	args := []string{
		config.ShermoPath,
		absPath,
		"-E", energy,
		"-prtvib", config.Prtvib,
		"-T", config.T,
		"-P", config.P,
		"-sclZPE", config.SclZPE,
		"-sclheat", config.SclHeat,
		"-sclS", config.SclS,
		"-sclCV", config.SclCV,
		"-ilowfreq", config.Ilowfreq,
		"-ravib", config.Ravib,
		"-imode", config.Imode,
		"-conc", config.Conc,
		"-outshm", config.Outshm,
		"-defmass", config.Defmass,
	}

	// 同时输出命令
	fmt.Println(strings.Join(args, " "))

	// 通过命令行运行 Shermo
	cmd := exec.Command(args[0], args[1:]...)
	result, err := cmd.CombinedOutput()

	if err == nil {
		fmt.Println()
		fmt.Printf("Hint: Shermo completed successfully on file %s.\n\n", file)
		contents := string(result)
		// 写入输出数据到文件
		outputFile := filepath.Join(outputDir, fileName+".txt")
		err = ioutil.WriteFile(outputFile, []byte(contents), 0644)
		if err != nil {
			fmt.Printf("Error writing output file: %v\n", err)
		}
	} else {
		fmt.Println()
		fmt.Printf("Hint: Shermo execution failed on file %s.\n", file)
	}
}

func RunAllShermo(config *ShermoConfig, energies []results) {
	// 注册输入文件夹
	optDir := filepath.Join(".", "opt")
	// 注册输入文件夹里所有的 out 文件
	files, err := filepath.Glob(filepath.Join(optDir, "*.out"))
	if err != nil {
		fmt.Printf("Error: failed to get files from directory %s\n", optDir)
		return
	}

	// 遍历所有的 files 文件和 result 集合，并全部调用 RunShermo 方法
	for i, file := range files {
		// 检查文件是否存在
		if _, err := os.Stat(file); os.IsNotExist(err) {
			fmt.Printf("Error: file %s not found.\n", file)
			continue
		}

		// 获取能量值
		energy := energies[i].Energy

		// 调用 RunShermo 函数
		RunShermo(config, file, energy)
	}
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

	// 读取 ShermoConfig 配置，并输出到屏幕
	shermoConfig, _ := NewShermoConfig()
	fmt.Println(shermoConfig)
	fmt.Println()

	// 将 spFile 转化为 int 类型
	spFileValue, _ := strconv.Atoi(shermoConfig.SpFile)
	// 如果 settings.ini 中设置为 1，则读取 gaussian
	if spFileValue == 1 {
		// 调用 GetGaussianEnergy 函数获取结果
		result := GetGaussianEnergy()
		RunAllShermo(shermoConfig, result)
	}
	// 如果 settings.ini 中设置为 2，则读取 orca
	if spFileValue == 2 {
		// 调用 GetOrcaEnergy 函数获取结果
		result := GetOrcaEnergy()
		RunAllShermo(shermoConfig, result)
	}

	// 获取当前日期和时间
	now := time.Now().Format("Jan-02-2006, 15:04:05") // 程序结束后提示版权信息和问候语
	// 程序结束后提示版权信息和问候语
	fmt.Println("Thank you for using our plotting tool! Have a great day!")
	fmt.Println("Copyright (C) 2023 Kimariyb. All rights reserved.")
	fmt.Printf("Currently timeline: %s\n", now)
}
