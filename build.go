package main

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	cp "github.com/otiai10/copy"
	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/renderer/html"
	"github.com/yuin/goldmark/text"
	"go.abhg.dev/goldmark/toc"
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
		case "bump":
			increaseBuildNumber()
		case "deploy":
			deploy()
		case "test":
			test()
		case "copy":
			copyPythonScripts()
		case "docs":
			docs()
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

// Increases build number, converts docs, builds game plugin and moves the NUPKG file to the OCTGN LocalFeed dir
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
	docs()
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

func test() {
	// Execute a program and redirect output to terminal
	cmd := exec.Command("o8build.exe", "-v", "-d="+PLUGIN_DIR)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Run()
}

func copyPythonScripts() {
	octgnDataDir, err := getOCTGNDataDir()
	if err != nil {
		fmt.Println("Error getting OCTGN paths")
		return
	}
	targetDir := filepath.Join(octgnDataDir, "GameDatabase", PLUGIN_ID, "Scripts")
	err = cp.Copy(filepath.Join(PLUGIN_DIR, "Scripts"), targetDir)
	if err != nil {
		fmt.Println("Error copying Python scripts:", err)
	}
	fmt.Println("Python scripts copied to", targetDir)
}

func docs() {
	files, err := getFilesGlob(filepath.Join(PLUGIN_DIR, "Documents", "*.md"))
	if err != nil {
		return
	}
	md := goldmark.New(
		goldmark.WithParserOptions(
			parser.WithAutoHeadingID(), // Enables auto heading ids
		),
		goldmark.WithRendererOptions(
			html.WithHardWraps(), // Render newlines as <br>
			html.WithUnsafe(),
		),
		goldmark.WithExtensions(
			extension.GFM, // Table, Strikethrough, Linkify and TaskList
		),
	)
	for _, path := range files {
		doc, err := getFileContents(path)
		if err != nil {
			fmt.Println("Cannot open MD file")
			return
		}
		// Render MD to HTML
		var buf bytes.Buffer
		if err := md.Convert([]byte(doc), &buf); err != nil {
			panic(err)
		}
		ext := filepath.Ext(path)
		baseNameWithoutExt := strings.TrimSuffix(filepath.Base(path), ext)
		absPath, _ := filepath.Abs(path)
		html := fmt.Sprintf(`<!doctype html>
			<html lang="en">
			<head>
				<meta charset="utf-8">
				<title>%s</title>
				<link href="doc.css" rel="stylesheet">
			</head>
			<body>
				%s
			</body>
			</html>`, baseNameWithoutExt, buf.String())
		// Build TOC
		if strings.Contains(doc, "<!-- toc -->") {
			// Parse MD document
			ast := md.Parser().Parse(text.NewReader([]byte(doc)))
			// Build table of contents
			tree, err := toc.Inspect(ast, []byte(doc))
			if err == nil {
				// Build a list representation of the table of contents to be rendered as Markdown or HTML
				list := toc.RenderList(tree)
				// Writes the TOC list as HTML into output
				var output bytes.Buffer
				md.Renderer().Render(&output, []byte(doc), list)
				html = strings.Replace(html, "<!-- toc -->", output.String(), -1)
			}
		}
		targetHTMLFile := strings.TrimSuffix(absPath, ext) + ".html"
		err = writeFileContents(targetHTMLFile, html)
		if err != nil {
			fmt.Printf("Error writing HTML file %s to disk\n", targetHTMLFile)
		}
	}
	fmt.Println("Markdown documents converted to HTML")
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
