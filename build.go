package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

const PLUGIN_NAME = "Card Fighters' Clash"
const PLUGIN_DIR = "o8g"
const PLUGIN_ID = "e3d56d9e-900d-49c6-b6ae-22cbb51be153"

func main() {
	if len(os.Args) > 1 {
		var param string = os.Args[1]
		switch param {
		case "build":
			build()
		case "buildnumber":
			increaseBuildNumber()
		case "deploy":
			deploy()
		case "help":
			printHelp()
		}
	} else {
		printHelp()
	}
}

// Builds a .o8g and a .nupkg file from the game definition files
func build() error {
	// Execute a program and redirect output to terminal
	cmd := exec.Command("o8build.exe", "-d="+PLUGIN_DIR)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err := cmd.Run()
	if err != nil {
		fmt.Println("Error executing command:", err)
		return err
	}
	return nil
}

// Increases the build number by 1
func increaseBuildNumber() error {
	filename := filepath.Join(PLUGIN_DIR, "definition.xml")
	fileContents, err := getFileContents(filename)
	if err != nil {
		fmt.Println("Cannot increase build number of file " + filename)
		return err
	}
	// Find plugin version number
	re := regexp.MustCompile(`version="(?:\d+\.){3,}\d+`)
	version := re.Find([]byte(fileContents))
	if version == nil {
		fmt.Println("Plugin version not found")
		return err
	}
	versionArr := strings.Split(string(version), ".")
	// Get build number
	buildNumber, err := strconv.Atoi(versionArr[len(versionArr)-1])
	if err != nil {
		fmt.Println("Failed to convert string build number to integer")
		return err
	}
	// Bump build number
	fmt.Printf("Bumping build number to %d\n", buildNumber+1)
	versionArr[len(versionArr)-1] = strconv.Itoa(buildNumber + 1)
	fileContentsReplaced := re.ReplaceAll([]byte(fileContents), []byte(strings.Join(versionArr, ".")))
	// Write file
	err = writeFileContents(filename, string(fileContentsReplaced))
	if err != nil {
		fmt.Println("Error updating plugin definition file")
		return err
	}
	return nil
}

// Builds and moves the NUPKG file to the OCTGN LocalFeed dir
func deploy() {
	startTime := time.Now()
	octgnDataDir, err := getOCTGNDataDir()
	if err != nil {
		fmt.Println("Error getting OCTGN paths")
		return
	}
	err = clobber(filepath.Join(octgnDataDir, "LocalFeed"), PLUGIN_NAME+"*.nupkg")
	if err != nil {
		return
	}
	err = increaseBuildNumber()
	if err != nil {
		return
	}
	err = build()
	if err != nil {
		return
	}
	pluginPkg, err := getFilesGlob(filepath.Join(PLUGIN_DIR, "*.nupkg"))
	if err != nil {
		return
	}
	err = moveFiles(pluginPkg, filepath.Join(octgnDataDir, "LocalFeed"))
	if err != nil {
		return
	}
	fmt.Printf("Task completed at %s\n", time.Now().Format(time.DateTime))
	fmt.Printf("Execution time: %s\n", time.Since(startTime))
}

func printHelp() {
	fmt.Println("=== Method 1: Using os.Args ===")
}

func getOCTGNDataDir() (string, error) {
	dir := filepath.Join(os.Getenv("USERPROFILE"), "AppData", "Local", "Programs", "OCTGN")
	// Open the file
	dataPath := "data.path"
	OCTGN_data_dir, err := getFileContents(filepath.Join(dir, dataPath))
	if err != nil {
		fmt.Println("Cannot access file " + dataPath)
		return "", err
	}
	return OCTGN_data_dir, nil
}

func getFile(path string) (*os.File, error) {
	// Open the file
	file, err := os.Open(path)
	if err != nil {
		fmt.Println("Cannot access file " + path)
		return nil, err
	}
	return file, nil
}

func getFileContents(path string) (string, error) {
	// Open the file
	file, err := getFile(path)
	defer file.Close()
	if err != nil {
		return "", err
	}
	// Read the file contents
	contents, err := io.ReadAll(file)
	if err != nil {
		fmt.Println("Cannot read file " + path)
		return "", err
	}
	// Get the file contents
	return string(contents), nil
}

func writeFileContents(path string, content string) error {
	// 0644: Owner can read/write, group/others can read only
	err := os.WriteFile(path, []byte(content), 0644)
	if err != nil {
		fmt.Println("Error writing file ", path)
		return err
	}
	return nil
}

func getFilesGlob(pattern string) ([]string, error) {
	// Find files matching the glob pattern
	files, err := filepath.Glob(pattern)
	if err != nil {
		fmt.Println("Error globbing files", err)
		return nil, err
	}
	return files, nil
}

func moveFiles(files []string, targetDir string) error {
	// Ensure the target directory exists
	_, err := os.Stat(targetDir)
	if os.IsNotExist(err) {
		fmt.Println("Target directory does not exist:", targetDir)
		return err
	}
	// Move each file to the target directory
	for _, file := range files {
		baseName := filepath.Base(file)
		targetPath := filepath.Join(targetDir, baseName)
		err := os.Rename(file, targetPath)
		if err != nil {
			fmt.Printf("Error moving file %s\n", file)
			continue
		}
		fmt.Printf("Moved file %s to %s\n", file, targetPath)
	}
	return nil
}

func clobber(dir string, filenamePattern string) error {
	files, err := getFilesGlob(filepath.Join(dir, filenamePattern))
	if err != nil {
		return err
	}
	for _, file := range files {
		fmt.Println("Deleting file", file)
		err := os.Remove(file)
		if err != nil {
			fmt.Println("Error deleting file", file)
			return err
		}
	}
	return nil
}
