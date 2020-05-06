# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Based in the Python Scripts for the Doomtown CCG definition for OCTGN, by Konstantine Thoukydides
# Copyright (C) 2013  Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Welcome screen
#---------------------------------------------------------------------------

def showWelcomeScreen():
   if not settings['WelcomeScreen']:
      if settings['GameVersion'] != gameVersion:
         showChangelog()
      return
      
   choiceList = ['How to play', 'Rulebook', 'Download card images', 'What\'s new'] #, 'Tutorial']
   colorsList = ['#004d99'] * len(choiceList)
   buttons = ['Close', 'Do not show again']
   msg = """         Welcome to Card Fighters' Clash!\n
Here you will find useful information to get started with the game.
Good battle!"""
   choice = askChoice(msg, choiceList, colorsList, buttons)
   
   if choice == 1:
      openUrl('https://cardfightersclash.wordpress.com/how-to-play/')
      showWelcomeScreen()
      
   elif choice == 2:
      openUrl('https://cardfightersclash.wordpress.com/rulebook/')
      showWelcomeScreen()
      
   elif choice == 3:
      openUrl('https://cardfightersclash.wordpress.com/image-packs/')
      showWelcomeScreen()
      
   elif choice == 4:
      showChangelog()
      showWelcomeScreen()
      
   elif choice == -2:
      switchSetting('WelcomeScreen', False)


#---------------------------------------------------------------------------
# Changelog screen
#---------------------------------------------------------------------------

def showChangelog():
   switchSetting('GameVersion', gameVersion)
   msg = """What's new in version 0.8.2

- This window :)
- Character's BP and player's HP to thousands.
- Simplified in-game contextual menu.
- Improved gameplay.
- Prevent accidental moving of markers."""
   askChoice(msg, [], [], ['Close'])