# Card Fighters' Clash plugin for OCTGN
Card Fighters' Clash is a card game for two players based on SNK Playmore’s video game
[SNK vs. Capcom Card Fighters' Clash 2 Expand Edition](http://neogeo.freeplaytech.com/svc-2/).
Players try to defeat each other playing powerful characters from video games licensed by Capcom and SNK Playmore.

This repository contains a game definition plugin for the free card game engine [Online Card and Tabletop Gaming Network (OCTGN)](http://octgn.net/).
This plugin allows online playing and creation of CFC decks.

Official plugin site: https://cardfightersclash.wordpress.com/

## Development
The project uses [Go](https://go.dev/) to automate some tasks, available through the following commands:

| Command            | Description        |
| ------------------ | ------------------ |
| `go build`       | Builds a .o8g and a .nupkg file from the game definition files using o8build.exe. |
| `go deploy`      | Builds and moves the NUPKG file to the OCTGN LocalFeed directory. |
| `go copy`        | Copies Python files to the game's script folder under OCTGN's games database folder. Useful when debugging your game along with the built-in functionality to reload Python scripts. |
| `go test`        | Verifies the files as a valid game definition. |
| `go bump`        | Increases the build number by 1 in the definition.xml file. |
| `go docs`        | Converts Markdown documents in Documents/ folder into HTML files. |

### Card Templates
CFC card templates (and sets of cards) are created and managed using [Magic Set Editor 2](http://magicseteditor.sourceforge.net/) software and a [custom template](https://github.com/raohmaru/CFC-MSE2).  
The card template is exported as an [OCTGN proxy card](https://github.com/octgn/OCTGN/wiki/ProxyGenerator), hence the [image packs](https://cardfightersclash.wordpress.com/image-packs/) for the cards only contains the illustrations.

### Card Coding
The game play is totally automated using [OCTGN Python API](https://github.com/octgn/OCTGN/wiki/OCTGN-Python-3.1.0.2-API-Reference), which means that players don't need to do any manual action to move the game forward. You can play CFC the same way you play Magic: The Gathering Arena or Hearthstone in your computer.

The mechanics of each card (this is, the rules of the card that interact with the game) are coded in the RuleScript language. [You can find the documentation here](./docs/RuleScript.md).

## Developing for OCTGN
OCTGN Game Development wiki: https://github.com/octgn/OCTGN/wiki#create-games-on-octgn

### Command Line Arguments
Run `OCTGN.exe [OPTION]`, where...

| Option                   | Description |
| ------------------------ | ----------- |
| `/t`<br>`/table`         | Starts OCTGN in the table view |
| `/g="game GUID"`<br>`/game="game GUID"`    | Starts with selected game |
| `/d="path/to/deck"`<br>`/deck="path/to/deck"` | Loads a deck |
| `/x`<br>`/devmode`       | Enables dev mode with the scripting console enabled |

### Debug
OCTGN Game logs are stored as .o8l files under the folder Documents/OCTGN/History/.

## Tips and Donations
If you find this OCTGN plugin useful, you can consider making a tip to support this project. Every little bit helps.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E2WE8J4)

## License
Released under the GNU General Public License version 3.

------

This project neither the author(s) are not affiliated with SNK Playmore or Capcom. All trademarks, trade names, services marks and logos belong to their respective companies. 
