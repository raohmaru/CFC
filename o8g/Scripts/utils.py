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


def delayedWhisper(text):
# Because whispers for some reason execute before notifys
   rnd(1,10)
   whisper(text)


def checkTwoSidedTable():
   debug(">>> checkTwoSidedTable()") #Debug
   mute()
   if not table.isTwoSided():
      warning("This game is designed to be played on a two-sided table.\nPlease start a new game and make sure the appropriate option is checked.")

      
def chooseSide():
# Called from many functions to check if the player has chosen a side for this game.
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


def resetAll():
# Clears all the global variables in order to start a new game.
   debug(">>> resetAll()") #Debug
   # Import all our global variables and reset them.
   global playerSide, handSize, debugVerbosity, parsedCards, transfCards, charsPlayed, backupsPlayed
   playerSide = None
   handSize = HandSize
   parsedCards = {}
   transfCards = {}
   charsPlayed = 0
   backupsPlayed = 0
   me.HP = 30
   me.SP = 0
   clearGlobalVar('Backups')
   clearGlobalVar('UnitedAttack')
   clearGlobalVar('Blockers')
   
   if len(players) > 1:
      debugVerbosity = DebugLevel.Off # Reset means normal game.
   elif debugVerbosity == DebugLevel.Off:
      debugVerbosity = DebugLevel.All
   debug("<<< resetAll()") #Debug


def switchAutomation(name, command = None):
   debug(">>> switchAutomation({})".format(name)) #Debug

   global automations
   if not name in automations:
      return
   if command == None:
      automations[name] = not automations[name]
   else:
      automations[name] = command
   status = "ON" if automations[name] else "OFF"
   notify("--> {}'s {} automations are {}.".format(me, name, status))

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


def clearGlobalVar(name, player = None):
   gvar = getGlobalVar(name, player)
   if isinstance(gvar, list):
      del gvar[:]  # Clear list
   elif isinstance(gvar, dict):
      gvar.clear()
   elif isinstance(gvar, basestring):
      gvar = ''
   elif isinstance(gvar, int):
      gvar = 0
   setGlobalVar(name, gvar, player)
   

def fromWhereStr(src):
   return "from the ring" if src == table else "from its " + src.name

   
def sanitizeStr(str):
# Strips the string, replaces spaces with dashes and removes characters not in
# a-z, 0-9
   valid_chars = '-abcdefghijklmnopqrstuvwxyz0123456789'
   str = str.strip().lower().replace(" ", "-")
   str = ''.join(c for c in str if c in valid_chars)
   return str


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
   
   
def fixSlotIdx(slotIdx, player = me):
# Fixes the slot index for players playing with the inverted table
   if player.hasInvertedTable():
      slotIdx = abs(slotIdx - (NumSlots-1))
   return slotIdx

   
def placeCard(card, type = None, action = None, target = None, faceDown = False):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   debug(">>> placeCard()") #Debug

   if automations['Play']:
      if type == CharType and action != None:
         coords = (0, fixCardY(0))
         if action == PlayAction:
            coords = CardsCoords['Slot'+`fixSlotIdx(target)`]
            coords = (coords[0], fixCardY(coords[1]))
         elif action == BackupAction:
            cx,cy = target.position
            backups = getGlobalVar('Backups')
            numBkps = len([id for id in backups if backups[id] == target._id])
            coords = (cx+CardsCoords['BackupOffset'][0]*numBkps, cy+CardsCoords['BackupOffset'][1]*numBkps)
         card.moveToTable(coords[0], coords[1], faceDown)
      else:
         card.moveToTable(-CardWidth/2, fixCardY(0), faceDown)
   else:
      card.moveToTable(0, fixCardY(0), faceDown)

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
         if card.controller != me:
            i = fixSlotIdx(i, player)
         debug("Slot idx: {}".format(i))
         return i
   debug("Card isn't in a slot")
   return -1

   
def putAtSlot(card, idx, player = me, move = False):
   debug(">>> putAtSlot({}, {}, move={})".format(card, idx, move)) #Debug
   if idx < NumSlots:
      ring = getGlobalVar('Ring', player)
      if move:
         oldIdx = getSlotIdx(card, player)
         if oldIdx != -1:
            ring[oldIdx] = None         
      ring[idx] = card._id
      setGlobalVar('Ring', ring, player)
      debug("{}'s ring: {}".format(me, ring))


def alignCard(card, x=None, y=None, slotIdx=None):
   debug(">>> alignCard({}, {}, {}, {})".format(card, x, y, slotIdx)) #Debug
   z = None
   if x == None or y == None:
      if slotIdx == None:
         slotIdx = getSlotIdx(card)
      if slotIdx == -1:
         return
      slotIdx = fixSlotIdx(slotIdx)
      # Align attacking chars
      if MarkersDict['Attack'] in card.markers:
         x, y = CardsCoords['Attack'+`slotIdx`]
         y = fixCardY(y)
      # Align chars in a uattack
      elif MarkersDict['UnitedAttack'] in card.markers:
         uattack = getGlobalVar('UnitedAttack')
         if len(uattack) <= 1 or card._id not in uattack:
            return
         idx = uattack.index(card._id)
         ox, oy = CardsCoords['UAttackOffset']
         lead = Card(uattack[0])
         x, y = lead.position
         x += ox * idx * playerSide
         y += oy * idx
         z = lead.getIndex - 1 * idx
      # Align blockers
      elif MarkersDict['CounterAttack'] in card.markers:
         blockers = getGlobalVar('Blockers')         
         for i in blockers:
            if blockers[i] == card._id:
               atkIdx = getSlotIdx(Card(i), players[1])
               x, y = CardsCoords['Attack'+`atkIdx`]
               y = fixCardY(y)
               break
      # Align char in his assigned slot
      else:
         x, y = CardsCoords['Slot'+`slotIdx`]
         y = fixCardY(y)
   if x != None and y != None:
      card.moveToTable(x, y)
   if z != None:
      card.setIndex(max(z, 0))


def alignBackups(card, x=0, y=0):
   debug(">>> alignBackups({})".format(card)) #Debug
   attachs = getAttachmets(card)
   if len(attachs) > 0:
      ox, oy = CardsCoords['BackupOffset']
      z = card.getIndex
      debug("{}'s index: {}".format(card, z))
      for i, c in enumerate(attachs):
         nx = x+ox*(i+1)
         ny = y+oy*(i+1)
         cx, cy = c.position
         if nx != cx or ny != cy:
            c.moveToTable(nx, ny)
         c.setIndex(max(z-i-1, 0))


def getTargetedCards(card=None, targetedByMe=True, controlledByMe=True, type=CharType):
   targetedBy   = me if targetedByMe   or len(players) == 1 else players[1]
   controlledBy = me if controlledByMe or len(players) == 1 else players[1]
   targets = [c for c in table
      if  c != card
      and c.targetedBy == targetedBy
      and c.controller == controlledBy
      and c.Type == type]
   return targets

   
def revealDrawnCard(card, type = None, faceUp = True):
   cardname = card.Name
   if not card.isFaceUp:
      if confirm("Reveal card to all players?"):
         if faceUp:
            card.isFaceUp = True
         rnd(1,100) # Small wait (bug workaround) to make sure all animations are done.
         cardname = card.Name
      else:
         type = type + " " if type != None else ""
         cardname = "a {}card".format(type)
         
   return cardname
   
   
def transformCard(card, cardModel):
   debug(">>> transformCard({}, {})".format(card, cardModel)) #Debug
   
   group = card.group
   cx, cy = card.position
   if group == table:
      newCard = group.create(cardModel, cx, cy, quantity = 1, persist = True)
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         setMarker(newCard, 'BP', num(newCard.BP) / 100)
         putAtSlot(newCard, slotIdx)
         clearAttachLinks(card)
   else:
      newCard = group.create(cardModel, quantity = 1)
   if group == table and card.isFaceUp:
      notify("{} transform {} into {}.".format(me, card, newCard))
   else:
      notify("{} transformed a card {}.".format(me, fromWhereStr(group)))
   model = card.model
   if card._id in transfCards:
      model = transfCards[card._id]
      del transfCards[card._id]
   transfCards[newCard._id] = model
   card.delete()
   
   
def copyAlternateRules(card, target):
   debug(">>> copyAlternateRules({}, {})".format(card, target)) #Debug
   
   if not automations['ExtAPI']:
      return None
   rules = None
   ability = None
   if isinstance(target, basestring):
      targetData = _extapi.getCardDataByModel(target)
      if targetData:
         rules = _extapi.getCardProperty(targetData, "Rules")
         ability = _extapi.getCardProperty(targetData, "Ability")
   else:
      rules = target.Rules
      ability = target.Ability
   if rules:
      debug("Found rule '{} {}'".format(ability, rules))
      return addAlternateRules(card, ability, rules)
   return None
   
   
def addAlternateRules(card, ability, rules, altname=None):
   debug(">>> addAlternateRules({}, {}, {})".format(card, ability, altname)) #Debug
   
   if not automations['ExtAPI']:
      return None
   ability = Ability(ability)
   if not altname:
      altname = sanitizeStr(ability.name)
   cardData = _extapi.getCardDataById(card._id)
   cardData.Properties[altname] = cardData.Properties[''].Clone()
   _extapi.setCardProperty(cardData, "Rules", rules, altname)
   _extapi.setCardProperty(cardData, "Ability Type", ability.type, altname)
   _extapi.setCardProperty(cardData, "Ability Name", ability.name, altname)
   debug("Adding new alternate '{}' and generating proxy".format(altname))
   _extapi.generateProxy(cardData, altname)
   card.switchTo(altname)
   return altname
   

def askForSlot(player = me, showEmptySlots = True):
   ring = getGlobalVar('Ring', player)
   if showEmptySlots and ring.count(None) == 0:
      warning("There is no emply slot in your ring where to put a character card.")
      return -1
   # Prompt the player to select an empty slot
   slots = []
   for i, id in enumerate(ring):
      if not showEmptySlots or id == None:
         slots.append(str(i+1))
   slotIdx = askChoice("Select an {}slot:".format("empty " if showEmptySlots else ""), slots)
   debug("Selected option {} ({})".format(slotIdx, slotIdx-1))
   if slotIdx == 0:
      return -1
   return int(slots[slotIdx-1]) - 1


#---------------------------------------------------------------------------
# Markers functions
#---------------------------------------------------------------------------

def getMarker(card, mkname):
   return card.markers[MarkersDict[mkname]]

      
def changeMarker(cards, marker, question):
# Changes the number of markers in one or more cards
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


def setMarker(card, mkname, qty=1):
   card.markers[MarkersDict[mkname]] = qty


def addMarker(card, mkname, qty=1):
   card.markers[MarkersDict[mkname]] += qty


def removeMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      setMarker(card, mkname, 0)


def toggleMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      removeMarker(card, mkname)
   else:
      setMarker(card, mkname, 1)
      

def dealDamage(dmg, target, source, isPiercing = False):
   if isinstance(target, Card):
      dmg = min(dmg, getMarker(target, 'BP'))
      addMarker(target, 'BP', -dmg)
      notify("{} deals {} damage to {} (new BP is {})".format(source, dmg, target, getMarker(target, 'BP')))
   else:
      target.HP -= dmg
      piercing = "piercing " if isPiercing else ""
      notify("{} deals {} {}damage to {} (new HP is {})".format(source, dmg, piercing, target, target.HP))
      

#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def modSP(count = 1, silent = False):
# A function to modify the players SP counter. Can also notify.
   if me.SP + count < 0:
      count = -me.SP  # SP can't be less than 0
   me.SP += count # Now increase the SP by the amount passed to us.
   if not silent and count != 0:
      action = "gains" if count >= 0 else "loses"
      notify("{} {} {} SP. New total is {}.".format(me, action, count, me.SP))


def payCostSP(count = 1, silent = False, msg = 'play this card'):
# Pay an SP cost. However we also check if the cost can actually be paid.
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
   debug(">>> getAttachmets({})".format(card)) #Debug
   
   # Returns a list with all the cards attached to this card
   backups = getGlobalVar('Backups')
   attachs = []
   for id in backups:
      if backups[id] == card._id:
         attachs.append(Card(id))
         
   debug("{} has {} cards attached".format(card, len(attachs)))
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
      

def setupDebug(group, x=0, y=0):
   # setup(group)
   debug(">>> setupDebug()") #Debug   
   mute()
   
   if len(players) > 1 or not me.name == Author:
      whisper("This function is only for development purposes.")
      return      
   if turnNumber() == 0:
      warning("Start the game prior to setup the debug environment")
      return      
   if len(me.Deck) == 0:
      warning("Please load a deck first.")
      return
   
   global charsPlayed, debugVerbosity
   debugVerbosity = DebugLevel.All
   me.SP = 50
   chooseSide()
   goToMain()
   cards = [
      'aa867ea1-89f8-4154-8e20-2263edd00002',
      'aa867ea1-89f8-4154-8e20-2263edd00014',
      'aa867ea1-89f8-4154-8e20-2263edd00135',
      'aa867ea1-89f8-4154-8e20-2263edd00240'
   ]
   for i, id in enumerate(cards):
      debug("Creating card {} at slot {}".format(id, i))
      card = table.create(id, 0, 0, quantity=1, persist=True)
      playAuto(card, i)
      ability = Ability(card)
      if ability.type and ability.type != InstantAbility:
         card.markers[MarkersDict['JustEntered']] = 0
      charsPlayed = 0
   drawMany(me.Deck, HandSize, True)
   
   debug("<<< setupDebug()") #Debug


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
   