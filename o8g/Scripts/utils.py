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

import re, time

#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------

def num(s):
# This function reads the value of a card and returns an integer. For some reason integer values of cards are not processed correctly
# see bug 373 https://octgn.16bugs.com/projects/3602/bugs/188805
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0


def delayedWhisper(text): # Because whispers for some reason execute before notifys
   rnd(1,10)
   whisper(text)


def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerSide, playerAxis
   if playerSide is not None:  # Has the player selected a side yet? If not, then...
      return;
   if Table.isTwoSided():
      playerAxis = Yaxis
      if me.hasInvertedTable():
         playerSide = -1
      else:
         playerSide = 1
   else:
      playerAxis = Yaxis
      if confirm("Will you play on the bottom side?"): # Ask which side they want
         playerSide = 1 # This is used to swap between the two halves of the X axis of the play field. Positive is on the right.
      else:
         playerSide = -1 # Negative is on the left.


def resetAll(): # Clears all the global variables in order to start a new game.
   # Import all our global variables and reset them.
   global playerSide, handSize, debugVerbosity
   debug(">>> resetAll()") #Debug
   playerSide = None
   handSize = HandSize
   me.HP = 30  # Wipe the counters
   me.SP = 0
   backups = getGlobalVar('Backups')
   backups.clear()
   setGlobalVar('Backups', backups)
   if len(players) > 1:
      debugVerbosity = DebugLevel.Off # Reset means normal game.
   elif debugVerbosity == DebugLevel.Off:
      debugVerbosity = DebugLevel.All
   debug("<<< resetAll()") #Debug


def clearAll(allPlayers = False):
   notify("{} clears all targets and highlights.".format(me))
   for card in table:
      if allPlayers or card.controller == me:
         clear(card, silent = True)


def switchAutomation(name, command = None):
   debug(">>> switchAutomation({})".format(name)) #Debug

   global automations
   if not name in automations:
      return
   if command == None:
      automations[name] = not automations[name]
   else:
      automations[name] = command
   notify("--> {}'s {} automations are {}.".format(me, name, automations[name]))

   debug("<<< switchAutomation({})".format(name)) #Debug


def rollDie(num):
   n = rnd(1, num)
   notify("{} rolls {} on a {}-sided die.".format(me, n, num))


def getGlobalVar(name, player = None):
   if player:
      return eval(player.getGlobalVariable(name))
   else:
      return eval(getGlobalVariable(name))


def setGlobalVar(name, value, player = None):
   if player:
      player.setGlobalVariable(name, str(value))
   else:
      setGlobalVariable(name, str(value))


def fromWhereStr(src):
   return " from the ring" if src == table else " from its " + src.name


#---------------------------------------------------------------------------
# Card Placement functions
#---------------------------------------------------------------------------

def fixCardY(y):
   # Variable to move the cards played by player 2 on a 2-sided table, more towards their own side. 
   # Player's 2 axis will fall one extra card length towards their side.
   # This is because of bug #146 (https://github.com/kellyelton/OCTGN/issues/146)
   offsetY = 0
   if me.hasInvertedTable():
      offsetY = CardHeight
   return (y + offsetY) * playerSide

   
def placeCard(card, type = None, action = None, target = None):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   debug(">>> placeCard()") #Debug

   if automations['Play']:
      if type == 'Character' and action != None:
         coords = (0, fixCardY(0))
         if action == PlayAction:
            coords = CardsCoords['Slot'+`target`]
            coords = (coords[0], fixCardY(coords[1]))
         elif action == BackupAction:
            cx,cy = target.position
            backups = getGlobalVar('Backups')
            numBkps = len([id for id in backups if backups[id] == target._id])
            coords = (cx+CardsCoords['BackupOffset'][0]*numBkps, cy+CardsCoords['BackupOffset'][1]*numBkps)
         card.moveToTable(coords[0], coords[1])
      else:
         card.moveToTable(-CardWidth/2, fixCardY(0))
   else:
      card.moveToTable(0, fixCardY(0))

   debug("<<< placeCard()")


def freeSlot(card):
# Frees a slot of the ring. It normally happens when a character leaves the ring
   debug(">>> freeSlot({})".format(card)) #Debug
   
   myRing = getGlobalVar('Ring', me)
   if card._id in myRing:
      myRing[myRing.index(card._id)] = None
   
   debug("{}'s ring: {}".format(me, myRing))
   setGlobalVar('Ring', myRing, me)
   
   debug("<<< freeSlot()")

   
def getSlotIdx(card, player = me):
   debug(">>> getSlotIdx({})".format(card)) #Debug
   
   ring = getGlobalVar('Ring', player)
   for i, id in enumerate(ring):
      if id == card._id:
         debug("Slot idx: {}".format(i))
         return i
   debug("Card isn't in a slot")
   return -1


def alignCard(card, x=0, y=0):
   debug(">>> alignCard({},{},{})".format(card, x, y)) #Debug
   card.moveToTable(x, fixCardY(y))


def alignBackups(card, x=0, y=0):
   debug(">>> alignBackups({})".format(card)) #Debug
   attachs = getAttachmets(card)
   if len(attachs) > 0:
      ox, oy = CardsCoords['BackupOffset']
      z = card.getIndex
      for i, c in enumerate(attachs):
         c.moveToTable(x+ox*(i+1), fixCardY(y+oy*(i+1)))
         c.setIndex(max(z-1, 0))


#---------------------------------------------------------------------------
# Card automation functions
#---------------------------------------------------------------------------

def getParsedCard(card):
   debug(">>> getParsedCard()") #Debug
   if not card.model in cards:
      cards[card.model] = ParsedCard(card)
   debug("Retrieved parsed card for model {} ({})".format(card.model, card.Name))
   return cards.get(card.model)
      
class ParsedCard():
   """ A class which stores the card ability name and its parsed rule autoscripts """   
   def __init__(self, card):
      debug(">>> ParsedCard()") #Debug
   
      ability = Regexps['Ability'].match(card.Rules)
      if ability:
         debug("Parsing {}".format(ability.group(0)))  # Causes weird IronPython error
         self.ability = ability.group(0)
         self.ability_type = ability.group(1)
         self.ability_name = ability.group(2)
      else:
         debug("No ability to parse")
         self.ability = None


#---------------------------------------------------------------------------
# Markers functions
#---------------------------------------------------------------------------

def changeMarker(cards, marker, question):  # Changes the number of markers in one or more cards
   n = 0
   for c in cards:
      if c.markers[marker] > n:
	     n = c.markers[marker]
   count = askInteger(question, n)
   if count == None: return
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = count
      dif = count-n
      if dif >= 0: dif = "+" + str(dif)   
      notify("{} sets {}'s {} to {}({}).".format(me, c, marker[0], count, dif))


def removeMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      card.markers[MarkersDict[mkname]] = 0
      

#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def modSP(count = 1, silent = False): # A function to modify the players SP counter. Can also notify.
   if me.SP + count < 0:
      count = -me.SP  # SP can't be less than 0
   me.SP += count # Now increase the SP by the amount passed to us.
   if not silent and count != 0:
      action = "gains" if count >= 0 else "loses"
      notify("{} {} {} SP. New total is {}.".format(me, action, count, me.SP))


def payCostSP(count = 1, silent = False, msg = 'play this card'): # Pay an SP cost. However we also check if the cost can actually be paid.
   count = num(count)
   if count >= 0:
      modSP(count, silent)
   else:
      if me.SP + count < 0: # If we don't have enough SP, we assume card effects or mistake and notify the player that they need to do things manually.
         if not silent:
            if not confirm("You do not seem to have enough SP to {}. Are you sure you want to proceed? \
            \n(If you do, your SP will go to the negative. You will need to increase it manually as required.)".format(msg)):
               return ERR_CANT_PAY_SP
            notify("{} was supposed to pay {} SP but only has {}.".format(me, count, me.SP))
      me.SP += count
      if not silent: notify("{} has spent {} SP. New total is {}.".format(me, count, me.SP))


#------------------------------------------------------------------------------
# Card Attachments
#------------------------------------------------------------------------------

def attach(card, target):
   debug(">>> attachCard()") #Debug
   target.target(False)
   backups = getGlobalVar('Backups')
   backups[card._id] = target._id
   setGlobalVar('Backups', backups)
   debugBackups()
   debug("<<< attachCard()")
   

def dettach(card):
   debug(">>> dettach()") #Debug
   mute()
   card.target(False)
   backups = getGlobalVar('Backups')
   # Next line causes an error
   # attachements = [att_id for att_id in backups if backups[att_id] == card._id]
   attach_len = len([id for id in backups if backups[id] == card._id])
   # Delete links of cards that were attached to the card
   if attach_len > 0:
      for id in backups:
         if backups[id] == card._id:
            del backups[id]
            notify("{} unattaches {} from {}.".format(me, Card(id), card))
   # Or, if the card was an attachment, delete the link
   elif card._id in backups:
      del backups[card._id]
      notify("Unattaching {} from {}".format(card, Card(backups[card._id])))
   else:
      return
   setGlobalVar('Backups', backups)
   debugBackups()
   debug("<<< dettach()")


def clearAttachLinks(card):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the attach dictionary, if it was itself attached to another card
   debug(">>> clearAttachLinks({})".format(card)) #Debug
   
   backups = getGlobalVar('Backups')
   # Next line causes an error
   # attachements = [k for k, v in backups.iteritems() if v == card._id]
   attach_len = len([id for id in backups if backups[id] == card._id])
   # Dettach cards that were attached to the card
   if attach_len > 0:
      for id in backups:
         if backups[id] == card._id:
            attcard = Card(id)
            debug("Unattaching {} from {}.".format(attcard, card))
            if attcard in table:
               discard(attcard)
            del backups[id]
   # If the card was an attachment, delete the link
   if backups.has_key(card._id):
      debug("{} is attached to {}. Unattaching.".format(card, Card(backups[card._id])))
      del backups[card._id] # If the card was an attachment, delete the link
   setGlobalVar('Backups', backups)
   
   debugBackups()   
   debug("<<< clearAttachLinks()") #Debug
   

def getAttachmets(card):
   # Returns a list with all the cards attached to this card
   backups = getGlobalVar('Backups')
   attachs = []
   for id in backups:
      if backups[id] == card._id:
         attachs.append(Card(id))
   return attachs


#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def debug(msg = 'Debug Ping!', level = 1):
   global debugVerbosity
   if debugVerbosity < DebugLevel.Info:
      return
   if isinstance(msg, (int, long, float)):
      msg = str(msg)
   if not re.search(r'(<<<|>>>)',msg):
      lvlPrefix = DebugLevelPrefixes[level]
      msg = lvlPrefix + ' ' + msg
   else:
      level = DebugLevel.Debug
   if debugVerbosity >= level:
      whisper(msg)


def testSuite(group, x=0, y=0):
   global debugVerbosity
   mute()
   whisper("### Checking Debug Validity")
   if len(players) > 1 or not me.name == Author:
      whisper("This function is only for development purposes.")
      return
   whisper("### Checking Players")
   if debugVerbosity < DebugLevel.Info:
      debugVerbosity = DebugLevel.All
      whisper("Reset debug verbosity to: {}".format(debugVerbosity))
   whisper("### Setting Table Side")
   chooseSide()


def setDebugVerbosity(group, x=0, y=0):
   global debugVerbosity
   mute()
   if not me.name == Author:
      whisper("This function is only for development purposes.")
      return
   n = askInteger("Set debug verbosity to: ({} to {})".format(DebugLevel.Off, DebugLevel.All), debugVerbosity)
   if n == None: return
   if n < DebugLevel.Off: n = DebugLevel.off
   elif n > DebugLevel.All: n = DebugLevel.All
   debugVerbosity = n
   whisper("Debug verbosity is now: {}".format(debugVerbosity))


def debugBackups():
   backups = getGlobalVar('Backups')
   debug("BACKUPS ({})".format(len(backups)))
   for id in backups:
      debug("   {} backups {}".format(Card(id), Card(backups[id])))
   