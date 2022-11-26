#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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
# Utility functions
#---------------------------------------------------------------------------

def chooseSide():
   """
   Checks if the player has chosen a side for this game.
   """
   if me.side is not None:
      return
   if Table.isTwoSided():
      me.side = (1, -1)[me.isInverted]
   else:
      side = 0
      while side == 0:
         side = askChoice("In which side of the board will you play?", ["△ Top side", "▽ Bottom side"])
      me.side = (-1, 1)[side - 1]


def resetAll():
   """
   Clears all the global and player variables in order to start a new game.
   """
   debug(">>> resetAll()")
   # Import all our global variables and reset them
   global gameCards, transformed, Globals, tutorial
   gameCards = {}
   transformed = {}
   me.HP = StartingHP
   me.SP = 0
   Globals = {}
   me.reset()
   resetState()
   # The user is playing the tutorial
   # FIXME If player does not start the tutorial and resets the game, the tutorial is still active
   if isinstance(tutorial, Tutorial) and tutorial.step > 0:
      tutorial = None
   debug("<<< resetAll()")


def switchSetting(name, value = None):
   """
   Updates the game settings of the player.
   """
   debug(">>> switchSetting({})", name)
   global settings
   if value == None:
      settings[name] = not settings[name]
   else:
      settings[name] = value
   setSetting("settings", str(settings))  # API method
   if isinstance(settings[name], bool):
      status = ("OFF", "ON")[settings[name]]
   else:
      status = settings[name]
   debug(" -> {}'s {} setting is {}.", me, name, status)
   debug("<<< switchSetting({})", name)


def rollDie(sides):
   n = rnd(1, sides)
   notify("{} rolls {} on a {}-sided die.", me, n, sides)
   return n


def showCardDlg(list, title, max = 1, text = "Card Selection", min = 1, bottomList = None, label = None, bottomLabel = None):
   """
   Shortcut function for the cardDlg dialog.
   """
   debug("showCardDlg({}, {}, {}, {}, {}, {}, {}, {})", list, title, max, text, min, bottomList, label, bottomLabel)
   groups = {}
   newList = []
   
   for c in list:
      # Removes KOed chars in the ring
      if c.group == table and getMarker(c, "BP") == 0:
         continue
      # Organizes chars by group
      if not c.group.name in groups:
         groups[c.group.name] = []
      groups[c.group.name].append(c)
   
   # Sort cards in table according to its slot index
   if "Table" in groups:
      charsRing = getRing()
      for c in charsRing:
         if c in groups["Table"]:
            newList.append(c)
      del groups["Table"]
   
   # Sort cards according to its index in the group
   for k, v in groups.iteritems():
      # Hand has indexes reversed
      sign = -1 if k == "Hand" else 1
      newList += sorted(v, key = lambda r: sign * r.index)
   
   dlg = cardDlg(newList, bottomList)
   dlg.title = text
   dlg.text = title
   dlg.min = min
   dlg.max = max
   dlg.label = label
   dlg.bottomLabel = bottomLabel
   playSnd("win-ask-1", True)
   return dlg.show()
            

def getOpp(player = None):
   if len(players) > 1:
      if player:
         return players[1] if player == me else me
      return players[1]
   return me
   

def getCurrentPhase():
   return currentPhase()[1]


def selectRing():
   """
   Gets the owner (player) of the ring selected by the user.
   """
   if len(players) == 1:
      return me
   t = askChoice("Select a ring", ['My ring', 'Enemy\'s ring'])
   if t == 0:
      return False
   return players[t-1]
   

def getSourceController():
   """
   Gets the controller of the source effect.
   """
   if commander and commander.cmdsArgs:
      return commander.cmdsArgs[2].controller
   return me
   

#---------------------------------------------------------------------------
# Rules
#---------------------------------------------------------------------------

def getRule(rule, Rules = None):
   """
   Gets a game rule that could be modified.
   """
   if not Rules:
      Rules = getGlobalVar("Rules", me)
      # It could be an empty list []
      if not rule in Rules or not Rules[rule]:
         Rules = getGlobalVar("Rules")
   # Not an empty list []
   if rule in Rules and Rules[rule]:
      for id, v in Rules[rule].iteritems():
         if not isinstance(v, bool):
            # We return all the values of the rule
            return Rules[rule].values()
         # If any value is false then the rule is false
         if not v:
            return False
      return True
   else:
      return GameRulesDefaults[rule]


def toggleRule(ruleName, value, id, restr = None, playerId = None):
   """
   Modifies a game rule.
   """
   debug(">>> toggleRule({}, {}, {}, {}, {})", ruleName, value, id, restr, playerId)
   player = None
   if playerId:
      player = Player(playerId)
   Rules = getGlobalVar("Rules", player)
   if not ruleName in Rules:
      Rules[ruleName] = {}
   rule = Rules[ruleName]
   # If modified rule already exists, reset it
   if id in rule:
      del rule[id]
   else:
      if isNumber(value):
         value = int(value)
      # Assign the rule value to the source ID that toggled the rule
      rule[id] = value
   setGlobalVar("Rules", Rules, player)
   debug("Rule {} has been {} ({})", ruleName, ("disabled", "enabled")[bool(value)], Rules[ruleName])
   ruleValue = getRule(ruleName, Rules)
   # Show a message if the rule did changed
   if (bool(value) and ruleValue) or (value == False and not ruleValue) or ruleValue == None:
      if ruleName in MSG_RULES:
         msg = MSG_RULES[ruleName]
         # Select message when the effect targets a player
         if playerId and ruleName +  "_player" in MSG_RULES:
            msg = MSG_RULES[ruleName +  "_player"]
         msg = msg[int(bool(value))]
         restr = getTextualRestr(restr)
         ctrl = player if playerId else ""
         notify(msg, value, restr, ctrl)


#---------------------------------------------------------------------------
# Temp variables
#---------------------------------------------------------------------------

def addTempVar(name, value, merge = False):
   """
   Adds a global temporal variable which is usually used during the execution of card rules.
   """
   debug(">>> addTempVar({}, {})", name, value)
   name = name.lower()
   vars = getGlobalVar("TempVars")
   if isinstance(value, list):
      value = [stringify(c) for c in value]
   else:
      value = stringify(value)
   if merge and name in vars:
      vars[name] += value
   else:
      vars[name] = value
   setGlobalVar("TempVars", vars)
   
   
def getTempVar(name, default = None):
   vars = getGlobalVar("TempVars")
   name = name.lower()
   if not name in vars:
      return default
   return objectify(vars[name])


#---------------------------------------------------------------------------
# Game state
#---------------------------------------------------------------------------

def getState(player = None, name = None):
   """
   Gets the actual state of the game for a player or a property of the current state.
   """
   debug(">>> getState({}, {})", player, name)
   GameState = getGlobalVar("GameState")
   name = name.lower()
   if not player:
      return GameState[name] if name in GameState else None
   if not name:
      return GameState[player._id]
   debug("GameState: {}", GameState)
   if name in GameState[player._id]:
      debug(" -- {}: {}", name, GameState[player._id][name])
      return GameState[player._id][name]
   return None


def setState(player, name, value):
   debug(">>> setState({}, {}, {})", player, name, value)
   GameState = getGlobalVar("GameState")
   name = name.lower()
   if player:
      GameState[player._id][name] = value
   else:
      GameState[name] = value
   setGlobalVar("GameState", GameState)
   debug("GameState: {}", GameState)
   

def resetState():
   """
   Resets the game state for both players.
   """
   GameState = getGlobalVar("GameState")
   if not "activeplayer" in GameState:
      GameState["activeplayer"] = getActivePlayer()._id if getActivePlayer() else None
   # Player with the priority
   GameState["priority"] = GameState["activeplayer"] if GameState["activeplayer"] is not None else 0
   for p in players:
      gs = GameState[p._id] if p._id in GameState else {}
      GameState[p._id] = {
         # Note that all keys must be lowercase
         "charsplayed"  : 0,            # Num of chars played this turn
         "charsperturn" : CharsPerTurn, # Allowed number of chars to play per turn
         "backupsplayed": 0,            # Num of chars backed-up this turn
         "ncdamaged"    : False,        # Player damaged by non-character card
         "lostsp"       : 0,            # SP lost this turn
         # Skip phases, don't reset
         "skip"         : gs["skip"] if "skip" in gs else [],
          # It seems that OCTGN counters are not updated among players fast enough, so we relay on these
         "hp"           : p.HP,
         "sp"           : p.SP
      }
   setGlobalVar("GameState", GameState)
   debug(">>> resetState()\n{}", GameState)
   

#---------------------------------------------------------------------------
# Game modifications
#---------------------------------------------------------------------------

def addGameMod(type, id, *args):
   """
   Applies a modification to the game rules.
   """
   debug(">>> addGameMod({}, {}, {})", type, id, args)
   Modifiers = getGlobalVar("Modifiers")
   if not type in Modifiers:
      Modifiers[type] = []
   Modifiers[type].append([id] + list(args))
   debug("{}", Modifiers)
   setGlobalVar("Modifiers", Modifiers)
   
  
def removeGameMod(id, msg = False):
   debug(">>> removeGameMod({}, {})", id, msg)
   Modifiers = getGlobalVar("Modifiers")
   debug("{}", Modifiers)
   for key, modList in Modifiers.iteritems():
      for i, mod in enumerate(list(reversed(modList))):
         if mod[0] == id:
            del modList[len(modList) - 1 - i]
   debug("{}", Modifiers)
   setGlobalVar("Modifiers", Modifiers)
   if msg:
      notify(msg)


#---------------------------------------------------------------------------
# Attack & Block
#---------------------------------------------------------------------------

def rearrangeUAttack(card):
   """
   Rearrange or cancels a UA if the card was part of it.
   """
   debug(">>> rearrangeUAttack({})", card)
   uattack = getGlobalVar("UnitedAttack")
   if card._id in uattack:
      notify("{} was part of an United Attack. Now the attack it will be rearranged.", card)
      uatttackIdx = uattack.index(card._id)
      uattack.remove(card._id)
      uattack = filter(None, uattack)
      setGlobalVar("UnitedAttack", uattack)
      # If it was the lead card, or there is only 1 char left, cancel UA
      if uatttackIdx == 0 or len(uattack) == 1:
         notify("{} cancels the United Attack.", me)
         clearGlobalVar("UnitedAttack")
         for cid in uattack:
            c = Card(cid)
            removeMarker(c, "United Attack")
            if attackAuto(c, True):
               c.highlight = AttackColor
            else:
               cancelAttack(c, True)
      # Reorder remaining chars in the UA
      else:
         for cid in uattack[1:]:
            alignCard(Card(cid))
      debug("UnitedAttack: {}", uattack)
      

def cancelAttack(card, silent = False):
   debug(">>> cancelAttack({})", card)
   removeMarker(card, "Attack")
   removeMarker(card, "United Attack")
   removeMarker(card, "Unfreezable")
   clear(card)
   alignCard(card)
   rearrangeUAttack(card)
   if not silent:
      notify("{} cancels the attack with {}.", me, card)
      playSnd("cancel-1")
   

def cancelBlock(card, silent = False):
   removeMarker(card, "Counter-attack")
   clear(card)
   alignCard(card)
   blockers = getGlobalVar("Blockers")
   for i in blockers:
      if blockers[i] == card._id:
         del blockers[i]
         debug("Removed blocker {}", blockers)
         setGlobalVar("Blockers", blockers)
         break
   if not silent:
      notify("{} cancels the counter-attack with {}.", me, card)
      playSnd("cancel-1")
