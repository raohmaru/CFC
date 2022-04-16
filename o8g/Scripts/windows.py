#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Welcome screen
#---------------------------------------------------------------------------

def showWelcomeScreen(group=None, x=0, y=0):
   debug(">>> showWelcomeScreen()")
   # On program started
   if group is None:
      if not settings["WelcomeScreen"]:
         if settings["GameVersion"] != getGameVersion():
            debug("Showing changelog because of a version update")
            showChangelog()
         return
   debug("Showing welcome screen")
      
   choiceList = ["Tutorial", u"   Rulebook  🡕", u"   Download card images  🡕", u"   Help us improve the game  🡕", "What's new?"]
   colorsList = ["#004d99"] * len(choiceList)
   buttons = ["Close", "Do not show again"]
   msg = """        Welcome to Card Fighters" Clash!\n
Here you will find useful information to get started with the game.
Have a good battle and thanks for playing!"""
   choice = askChoice(msg, choiceList, colorsList, buttons)
   
   if choice == 1:
      global tutorial
      tutorial = True
      resetGame()
      
   elif choice == 2:
      openUrl(Website + "/rulebook/")
      showWelcomeScreen()
      
   elif choice == 3:
      downloadImagePacks()
      showWelcomeScreen()
      
   elif choice == 4:
      openUrl(Website + "/feedback/")
      showWelcomeScreen()
      
   elif choice == 5:
      showChangelog()
      showWelcomeScreen()
      
   elif choice == -2:
      switchSetting("WelcomeScreen", False)
      
      
def downloadImagePacks(group=table, x=0, y=0):
   openUrl(Website + "/image-packs#sets")
   

def getGameVersion():
   """
   Returns game version in the format x.y.z.
   """
   return ".".join(gameVersion.split(".")[:3])


#---------------------------------------------------------------------------
# Changelog screen
#---------------------------------------------------------------------------

def showChangelog():
   switchSetting("GameVersion", getGameVersion())
   msg = u"""What's new in version 0.9.9

- Ask for confirmation when a player discards cards from the game area.
- Improved card design.
- Performance improvements.
- Fixed bug in the `prophecy` command affecting Mischief.
- Bugfix: multiple combat damage to a player is not correctly subtracted.
- Bugfix: The Ump cannot join an United Attack although auto abilities are disabled in United Attacks.
""".format(TriggerUniChar)
   askChoice(msg, [], [], ["Close"])
   

#---------------------------------------------------------------------------
# Card info screen
#---------------------------------------------------------------------------

def cardInfo(card, x = 0, y = 0):
   offset = (60 - len(card.Name)) / 2
   msg = "{}{}\n\n{} card".format(" " * offset, card.Name, card.Type)
   
   if isCharacter(card):
      msg += " ({0})".format(card.Subtype)
      msg += "\nBP: {0}   SP: {0}".format(card.BP, card.SP)
   else:
      msg += "\nSP: {0}".format(card.SP)
   
   if isCharacter(card):
      pcard = getGameCard(card)
      abl = card.properties["Ability Type"]
      if abl:
         msg += "\n\n{} ability\n{}".format(pcard.ability.unicodeChar, MSG_HELP_AB[abl])
      
   rules = card.properties["Rules"]
   if rules:
      if re.search("becomes?[\w ]+card", rules, re.IGNORECASE):
         msg += """

BECOME ANOTHER CARD / TRANSFORM
When a card becomes another card (it is transformed), all of the card's properties are replaced by the other card's properties. If the card is a character, the BP is replaced by the other card BP (even if that character has received damage). Any back-up on the card is discarded.
The state of the transformed card does not change (fresh, freeze, etc.), but all effects applied on the card are terminated.
If the card goes to a pile (deck, Discard pile or Removed pile), it is transformed back to its original card."""

      if re.search("KO", rules):
         msg += """

KO
To move a character from the arena to its controller's Discard pile."""

      if re.search("copy[\w ]+abilit(y|ies)", rules, re.IGNORECASE):
         msg += """

COPY ABILITY
To copy an ability from a character and give it to another character. Any existing abilities of the target character are replaced with the copied ability."""

      if re.search("(give|steal)[\w ]+abilit(y|ies)", rules, re.IGNORECASE):
         msg += """

GIVE / STEAL ABILITY
To remove an ability from a character and give it to another character. Any existing abilities of the target character are replaced with the new one."""

      if re.search("freeze|frozen", rules, re.IGNORECASE):
         msg += u"""

FREEZE
A character in a "freeze" state (or "frozen") can't attack, counter-attack or activate {} abilities.""".format(TriggerUniChar)

      if re.search("fresh", rules, re.IGNORECASE):
         msg += """

FRESH
A character that has just entered the ring in your turn."""

      if re.search("lose[\w ]+abilit(y|ies)", rules, re.IGNORECASE):
         msg += """

LOSE ABILITY
To remove an ability from a character."""

      if re.search("mimic", rules, re.IGNORECASE):
         msg += """

MIMIC
To copy an ability or effect from a card and then resolve it. Once resolved, it ceases to exist."""

      if re.search("nullif(y|ies)", rules, re.IGNORECASE):
         msg += """

NULLIFY
Players cannot activate nullified abilities."""

      if re.search("piercing damage", rules, re.IGNORECASE):
         msg += """

PIERCING DAMAGE
If the total BP of the attacking character(s) is higher than the BP of the character that counters, this BP difference is dealt as damage to the enemy."""

      if re.search("steal[\w\d ]+sp", rules, re.IGNORECASE):
         msg += """

STEAL SP
An enemy loses an amount of SP and you gain that same amount."""

      if re.search("swap the abilities", rules, re.IGNORECASE):
         msg += """

SWAP ABILITIES
The abilities between two character are interchanged. Both abilities are copied from one character and given to the other character at the same time."""

      if re.search("trash", rules, re.IGNORECASE):
         msg += """

TRASH
To put cards from the top of a player's deck into their Discard pile."""            
         
   if isCharacter(card):
      msg += "\n\nBackups: {}.".format(", ".join(filter(None, getAcceptedBackups(card))))
      
   askChoice(msg, [], [], ["Close"])
