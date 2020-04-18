# Card Fighters' Clash plugin for OCTGN
Card Fighters' Clash is a card game for two players based on SNK Playmore’s video game
[SNK vs. Capcom Card Fighters' Clash 2 Expand Edition](http://neogeo.freeplaytech.com/svc-2/).
Players try to defeat each other playing powerful characters from video games licensed by Capcom and
SNK Playmore.

This is a game definition plugin for the free card game engine [Online Card and Tabletop Gaming Network (OCTGN)](http://octgn.net/).
This plugin allows online playing and creation of CFC decks.

Official plugin site: https://cardfightersclash.wordpress.com/

## Development
The project uses [Rake](https://github.com/ruby/rake) to automate some tasks, available through the 
the following commands:
- `rake build` Builds a .o8g and a .nupkg file from the game definition files using o8build.exe.
- `rake deploy` Builds and moves the NUPKG file to the OCTGN LocalFeed directory.
- `rake copy` Copies python files to the game's script folder under OCTGN's games database folder.
Useful when debugging your game along with the built-in functionality to reload python scripts.
- `rake test` Verifies the files as a valid game definition.
- `rake versionbump` Increases the build number by 1 in the definition.xml file.
- `rake octgn` Runs OCTGN in dev mode, in the table view with the CFC plugin loaded.
- `rake docs` Converts Markdown documents in Documents/ folder into HTML files.

Use [bundler](http://bundler.io/) to install the dependencies.

## License
Released under the GNU General Public License version 3.

------

This project neither the author(s) are not affiliated with SNK Playmore or Capcom. All trademarks, trade names, services marks and logos belong to their respective companies. 