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
      if me.isInverted:
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
   global playerSide, handSize, debugVerbosity, parsedCards, charsPlayed, backupsPlayed
   playerSide = None
   handSize = HandSize
   parsedCards = {}
   charsPlayed = 0
   backupsPlayed = 0
   me.HP = 30
   me.SP = 0
   clearGlobalVar('Backups')
   clearGlobalVar('UnitedAttack')
   clearGlobalVar('Blockers')
   clearGlobalVar('Transformed')
   clearGlobalVar('GameEvents')
   clearGlobalVar('CardCost')
   clearGlobalVar('Rules')
   
   if me.name == Author:
      if debugVerbosity == DebugLevel.Off:
         debugVerbosity = DebugLevel.All
   else:
      debugVerbosity = DebugLevel.Off # Reset means normal game.
   
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
# Reads a game global variable or a player global variable
   if player:
      return eval(player.getGlobalVariable(name))
   else:
      return eval(getGlobalVariable(name))


def setGlobalVar(name, value, player = None):
# Writes a game global variable or a player global variable
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
   elif isinstance(gvar, (int, long)):
      gvar = 0
   setGlobalVar(name, gvar, player)
   

def replaceVars(str):
   debug("replaceVars({})".format(str))
   str = re.sub(Regexps['BP'], r'hasattr(getParsedCard(\1), "BP") and getParsedCard(\1).BP', str)
   str = re.sub(Regexps['Action'], 'isAction(card)', str)
   str = re.sub(Regexps['Char'], 'isCharacter(card)', str)
   str = re.sub(Regexps['HandSize'], r'len(\1.hand)', str)
   str = re.sub(Regexps['Ring'], r'getRingSize(\1)', str)
   str = re.sub(Regexps['Chars'], r'getRing(\1)', str)
   str = str.replace('.sp', '.SP')
   str = str.replace('.hp', '.HP')
   str = str.replace('opp', 'getOpp()')
   str = str.replace('alone', 'getRingSize() == 1')
   debug("-- {}".format(str))
   return str
   
   
def evalExpression(expr, retValue = False, locals = None):
   expr = replaceVars(expr)
   forexpr = "[{} for card in {}]"
   
   if ':' in expr:
      parts = expr.split(":")
      expr = forexpr.format(parts[1], parts[0])
   
   if ' in ' in expr:
      parts = expr.split("in")
      expr = forexpr.format(parts[0], parts[1])
   
   if ' all ' in expr:
      expr = expr.replace('all', '')
      # https://docs.python.org/2.7/library/functions.html
      expr = 'all(' + expr + ')'
   
   try:
      res = eval(expr, None, locals)
      if retValue:
         debug("Evaluated expr  %s  (%s)" % (expr, res))
         return res
      else:
         debug("Evaluated expr  %s  ?  (%s)" % (expr, res))
         return bool(res)
   except:
      debug("%s  is not a valid Python expression" % (expr))
      return False
   
   
def showCardDlg(list, title, max=1, text="Select a card:", min=1, bottomList=None, label=None, bottomLabel=None):
   debug("showCardDlg({}, {}, {}, {}, {}, {}, {}, {})".format(list, title, max, text, min, bottomList, label, bottomLabel))
   dlg = cardDlg(list, bottomList)
   dlg.title = title
   dlg.text = text
   dlg.min = min
   dlg.max = max
   dlg.label = label
   dlg.bottomLabel = bottomLabel
   return dlg.show()
            

def getOpp():
   return players[1] if len(players) > 1 else me
            

def getNextActivePlayer():
   return players[1] if len(players) > 1 and me.isActive else me


def getRule(rule):
   rules = getGlobalVar('Rules')
   if rule in rules and rules[rule]:  # Not an empty list []
      for b in rules[rule]:
         if not b:
            return False
      return True
   else:
      return GameRulesDefaults[rule]


def addActionTempVars(name, value):
   vars = getGlobalVar('ActionTempVars')
   vars[name] = value
   setGlobalVar('ActionTempVars', vars)

#---------------------------------------------------------------------------
# Pile functions
#---------------------------------------------------------------------------

def swapPiles(pile1, pile2):
# This function swaps the cards of two piles.
   mute()
   savedPile1 = [card for card in pile1]
   for card in pile2:
      card.moveTo(pile1)
   rnd(100, 10000)  # Delay the next action until all animation is done
   for card in savedPile1:
      card.moveTo(pile2)   
   if len(players) > 1: rnd(10, 1000) # Wait a bit more, as in multiplayer games, things are slower.
   notify("{} swaps its {} with its {}.".format(me, pile1.name, pile2.name))


def reveal(group):
   debug(">>> reveal()") #Debug
   cards = [card for card in group]
   notify("{} shows his {}".format(group.controller, group.name))
   showCardDlg(cards, "Cards in {}'s {}".format(group.controller, group.name), 0, "", 0)
   
   
def getRing(player = None):
   if player:
      ring = getGlobalVar('Ring', player)
   else: 
      ring = getGlobalVar('Ring', me)
      if len(players) > 1:
         ring += getGlobalVar('Ring', players[1])
   return [c for c in table
      if c._id in ring]


def getRingSize(player = me):
   return NumSlots - getGlobalVar('Ring', player).count(None)


def moveToGroup(group, card, sourceGroup = None, pos = None, reveal = False, sourcePlayer = me):
   if not sourceGroup:
      sourceGroup = card.group
   fromText = fromWhereStr(sourceGroup, sourcePlayer)
   posText = "to the top of"
   if pos is not None:
      if pos < 0:
         posText = "to the bottom of"
      elif pos > 0:
         posText = str(pos) + "to position {} from the top of"
   if sourceGroup.name == 'Hand':
      card.isFaceUp = False
   if group.name == 'Hand':
      posText = "into"
   name = 'a card'
   if card.isFaceUp:
      name = card
   elif reveal:
      name = card.Name
   card.moveTo(group, pos)
   targetCtrl = 'its' if me == sourcePlayer else "{}'s".format(me)
   notify("{} moved {} {} {} {} {}.".format(sourcePlayer, name, fromText, posText, targetCtrl, group.name))
   

def selectRing():
   if len(players) == 1:
      return me
   t = askChoice("Select a ring", ['My ring', 'Enemy ring'])
   if t == 0:
      return False
   return players[t-1]


#---------------------------------------------------------------------------
# String functions
#---------------------------------------------------------------------------

def fromWhereStr(src, srcPlayer = me):
   if src == table:
      return "from the ring"
   else:
      ctrl = 'its'
      if srcPlayer != me:
         ctrl = "{}'s".format(me)
      elif src.controller != me:
         ctrl = "opponent's"
         
      return "from {} {}".format(ctrl, src.name)

   
def sanitizeStr(str):
# Strips the string, replaces spaces with dashes and removes characters not in
# a-z, 0-9
   valid_chars = '-abcdefghijklmnopqrstuvwxyz0123456789'
   str = str.strip().lower().replace(" ", "-")
   str = ''.join(c for c in str if c in valid_chars)
   return str
   

def getPlural(num):
   if num == 1:
      return ''
   return 's'
   

#---------------------------------------------------------------------------
# Card functions
#---------------------------------------------------------------------------

def fixCardY(y):
# Variable to move the cards played by player 2 on a 2-sided table, more towards their own side. 
# Player's 2 axis will fall one extra card length towards their side.
# This is because of bug #146 (https://github.com/kellyelton/OCTGN/issues/146)
   offsetY = 0
   if me.isInverted:
      offsetY = CardHeight
   if not playerSide:
      chooseSide()
   return (y + offsetY) * playerSide
   
   
def fixSlotIdx(slotIdx, player = me):
# Fixes the slot index for players playing with the inverted table
   if player.isInverted:
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
   
   
def getCardAtSlot(idx, player = me):
   debug(">>> getCardAtSlot({}, {})".format(idx, player)) #Debug
   
   ring = getGlobalVar('Ring', player)
   if player != me:
      ring.reverse()
   card = Card(ring[idx]) if ring[idx] else None
   debug("Card at slot {} is: {}".format(idx, card))
   return card
   

def charIsInRing(card, player = me):
   ring = getGlobalVar('Ring', player)
   return card._id in ring

   
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
      elif MarkersDict['United Attack'] in card.markers:
         uattack = getGlobalVar('UnitedAttack')
         if len(uattack) <= 1 or card._id not in uattack:
            return
         idx = uattack.index(card._id)
         ox, oy = CardsCoords['UAttackOffset']
         lead = Card(uattack[0])
         x, y = lead.position
         x += ox * idx * playerSide
         y += oy * idx
         z = lead.index - 1 * idx
      # Align blockers
      elif MarkersDict['Counter-attack'] in card.markers:
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
      card.index = max(z, 0)


def alignBackups(card, x=0, y=0):
   debug(">>> alignBackups({}, {}, {})".format(card, x, y)) #Debug
   attachs = getAttachmets(card)
   if len(attachs) > 0:
      ox, oy = CardsCoords['BackupOffset']
      z = card.index
      debug("{}'s index: {}".format(card, z))
      for i, c in enumerate(attachs):
         nx = x+ox*(i+1)
         ny = y+oy*(i+1)
         cx, cy = c.position
         if nx != cx or ny != cy:
            c.moveToTable(nx, ny)
         c.index = max(z-i-1, 0)


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
      clearAttachLinks(card)
      slotIdx = getSlotIdx(card)
      if slotIdx != -1:
         setMarker(newCard, 'BP', num(newCard.BP) / 100)
         putAtSlot(newCard, slotIdx)
      for m in card.markers:
         if m[0] != 'BP':
            setMarker(newCard, m[0], card.markers[m])
   else:
      newCard = group.create(cardModel, quantity = 1)
   if group == table and card.isFaceUp:
      notify("{} transform {} into {}.".format(me, card, newCard))
   else:
      notify("{} transformed a card {}.".format(me, fromWhereStr(group)))
   model = card.model
   transfCards = getGlobalVar('Transformed')
   if card._id in transfCards:
      model = transfCards[card._id]
      del transfCards[card._id]
   transfCards[newCard._id] = model
   setGlobalVar('Transformed', transfCards)
   card.delete()
   
   
def copyAlternateRules(card, target):
   debug(">>> copyAlternateRules({}, {})".format(card, target)) #Debug
   
   if not automations['ExtAPI']:
      return None
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
   ability = Ability(ability, rules)
   if not altname:
      altname = sanitizeStr(ability.name)
   cardData = _extapi.getCardDataById(card._id)
   cardData.Properties[altname] = cardData.Properties[''].Clone()
   _extapi.setCardProperty(cardData, "Rules", rules, altname)
   _extapi.setCardProperty(cardData, "Ability Type", ability.type, altname)
   _extapi.setCardProperty(cardData, "Ability Name", ability.name, altname)
   _extapi.setCardProperty(cardData, "Ability", (ability.type+' '+ability.name).strip(), altname)
   debug("Adding new alternate '{}' and generating proxy".format(altname))
   _extapi.generateProxy(cardData, altname)
   # Need to be here, otherwise if active player switches the card and network tasks are not
   # completed, the card won't switch at all
   card.alternate = altname
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
   # Don't ask of only 1 slot is empty
   if len(slots) == 1:
      return int(slots[0]) - 1
   slotIdx = askChoice("Select a{}slot:".format("n empty " if showEmptySlots else " "), slots)
   debug("Selected option {} ({})".format(slotIdx, slotIdx-1))
   if slotIdx == 0:
      return -1
   return int(slots[slotIdx-1]) - 1

   
def passControlTo(player, cards, cb = None):
   for card in cards:
      if card.group != table:
         card.moveToTable(0, 0, True)
      card.controller = player
   if cb is not None:
      update()
      remoteCall(player, cb[0], cb[1])
   


#---------------------------------------------------------------------------
# Markers functions
#---------------------------------------------------------------------------

def getMarker(card, mkname):
   return card.markers[MarkersDict[mkname]]

      
def changeMarker(cards, marker, question = None, count = None):
# Changes the number of markers in one or more cards
   n = 0
   if not count:
      for c in cards:
         if c.markers[marker] > n:
           n = c.markers[marker]
      count = askInteger(question, n)
   if count == None:
      return
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = count
      diff = count-n
      if diff >= 0: diff = "+" + str(diff)   
      notify("{} sets {}'s {} to {}({}).".format(me, c, marker[0], count, diff))


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
      oldBP = getMarker(target, 'BP')
      dmg = min(dmg, getMarker(target, 'BP'))
      addMarker(target, 'BP', -dmg)
      notify("{} deals {} damage to {}. New BP is {} (before was {}).".format(source, dmg, target, getMarker(target, 'BP'), oldBP))
   else:
      oldHP = target.HP
      target.HP -= dmg
      piercing = "piercing " if isPiercing else ""
      notify("{} deals {} {}damage to {}. New HP is {} (before was {}).".format(source, dmg, piercing, target, target.HP, oldHP))
      
      
def modBP(card, qty, mode = None):
   if mode == '=':
      changeMarker([card], MarkersDict['BP'], count = qty)
   elif qty >= 0:
      plusBP([card], count = qty)
   else:
      minusBP([card], count = -qty)


#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def modSP(count = 1, mode = None, silent = False, player = me):
# A function to modify the players SP counter. Can also notify.
   initialSP = player.SP
   if mode == '=':
      player.SP = count
      count = player.SP - initialSP
   else:
      if player.SP + count < 0:
         count = -initialSP  # SP can't be less than 0
      player.SP += count # Now increase the SP by the amount passed to us.
   if not silent and count != 0:
      action = "gains" if count >= 0 else "loses"
      notify("{} {} {} SP. New total is {} (before was {}).".format(player, action, count, player.SP, initialSP))


def payCostSP(count = 1, silent = False, msg = 'play this card', cardType = None):
# Pay an SP cost. However we also check if the cost can actually be paid.
   count = num(count)
   
   # Cost modifiers
   if cardType:
     cardType = cardType.lower()
     CardCost = getGlobalVar('CardCost')
     if cardType in CardCost and CardCost[cardType] != 0:
        cost = count + CardCost[cardType]
        # If initial cost was less than 0, then it cannot be less than -1 (Kyosuke rule)
        if cost >= 0:
           cost = max(count, -1)
        if count != cost:
           count = cost
           notify("The SP cost of the card has been modified by an ability.")
   
   if count >= 0:
      modSP(count, silent=silent)
   else:
      initialSP = me.SP
      if me.SP + count < 0: # If we don't have enough SP, we assume card effects or mistake and notify the player that they need to do things manually.
         if not silent:
            if not confirm("You do not seem to have enough SP to {}.\nAre you sure you want to proceed?\nCost is {} SP. \
            \n\n(If you do, your SP will go to the negative. You will need to increase it manually as required.)".format(msg, count)):
               return False
            notify("{} was supposed to pay {} SP but only has {}.".format(me, count, me.SP))
      me.SP += count
      if not silent:
         notify("{} has spent {} SP. New total is {}  (before was {}).".format(me, count, me.SP, initialSP))
   return True


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
      notify("{} clears all backups of {}.".format(me, card))
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
   

def getAcceptedBackups(card):
   return (card.properties['Backup 1'], card.properties['Backup 2'], card.properties['Backup 3'])


#---------------------------------------------------------------------------
# Helpers
#---------------------------------------------------------------------------

def isNumber(s):
   if not s:
      return False
   try:
      float(s)
      return True
   except ValueError:
      return False
        

def isPlayer(obj):
   return isinstance(obj, Player)


def isCard(obj):
   return isinstance(obj, Card)


def isCharacter(card):
   return card.Type == CharType


def isAction(card):
   return card.Type == ActionType


def isReaction(card):
   return card.Type == ReactionType


def isAttached(card):
   backups = getGlobalVar('Backups')
   return bool(backups.get(card._id))
   
   
def isFrozen(card):
   return card.orientation & Rot90 == Rot90


def compareValuesByOp(v1, v2, op):
   if op == RS_OP_EQUAL:
      return v1 == v2
   elif op == RS_OP_LTE:
      return v1 <= v2
   elif op == RS_OP_GTE:
      return v1 >= v2
      
   return False


def hasMarker(card, marker, include=True):
   if not isCard(card):
      return False
      
   res = MarkersDict[marker] in card.markers
   if include:
      return res
   else:
      return not res


def inUAttack(card):
   uattack = getGlobalVar('UnitedAttack')
   if len(uattack) > 0 and card._id in uattack:
      return True
   return False