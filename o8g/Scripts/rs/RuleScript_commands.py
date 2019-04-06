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
# Commands class
#---------------------------------------------------------------------------

class RulesCommands():
   """ Class to handle the filters that are applied to a set of objects """
   items = {}
   cmds = []
   cmdsArgs = []

   @staticmethod
   def register(name, cmd):
      RulesCommands.items[name] = cmd


   @staticmethod
   def applyAll(cmds, targets, restr, source, revert=False):
      RulesCommands.cmds = list(cmds)  # Clone array
      RulesCommands.cmdsArgs = [targets, restr, source, revert]
      RulesCommands.applyNext()
      # for cmd in cmds:
         # RulesCommands.applyCmd(cmd, targets, restr, source, revert)


   @staticmethod
   def applyNext():
   # Ensures that a command is applied only when the precedent command is done
      if len(RulesCommands.cmds) > 0:
         cmd = RulesCommands.cmds.pop(0)
         debug(">>> applyNext({})".format(cmd)) #Debug    
         RulesCommands.applyCmd(cmd, *RulesCommands.cmdsArgs)
      else:
         RulesCommands.cmdsArgs = []


   @staticmethod
   def applyCmd(cmd, targets, restr, source, revert=False):
      debug(">>> applyCmd({}, {}, {}, {}, {})".format(cmd, targets, restr, source, revert)) #Debug
      funcStr = cmd[0]
      params = cmd[1]
      # Executing command functions
      if funcStr in RulesCommands.items and not revert:
         debug("-- applying cmd '%s' to targets %s (%s)" % (funcStr, targets, restr))
         func = RulesCommands.items[funcStr]
         # func = eval(RulesCommands.items[funcStr])  # eval is a necessary evil...
         func(targets, restr, source, *params)
      # Abilities/bonus manipulation
      elif funcStr in RS_PREFIX_BONUS:
         for target in targets:
            if funcStr == RS_PREFIX_PLUS:
               if revert:
                  RulesAbilities.remove(params, target._id)
               else:
                  RulesAbilities.add(params, target._id, source._id, restr)
      else:
         debug("-- cmd not found: {}".format(cmd[0]))


#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmd_damage(targets, restr, source, dmg):
   debug(">>> cmd_damage({}, {}, {})".format(targets, restr, dmg)) #Debug
   dmg = int(dmg)
   for target in targets:
      dealDamage(dmg, target, source)
   RulesCommands.applyNext()


def cmd_swapPiles(targets, restr, source, pile1, pile2):
   debug(">>> cmd_swapPiles({}, {}, {})".format(source, pile1, pile2)) #Debug
   pile1 = RulesUtils.getZoneByName(pile1)
   pile2 = RulesUtils.getZoneByName(pile2)
   swapPiles(pile1, pile2)
   RulesCommands.applyNext()


def cmd_shuffle(targets, restr, source, pileName=None):
   debug(">>> cmd_shuffle({})".format(pileName)) #Debug
   if not pileName:
      pileName = RS_KW_ZONE_HAND
   prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, pileName)
   if name == RS_KW_ZONE_DECK:
      pile = RulesUtils.getZoneByName(pileName)
      if pile.controller == me:
         shuffle(pile)
      else:
         remoteCall(pile.controller, "shuffle", [pile])
   rnd(1, 100) # Wait until all animation is done
   RulesCommands.applyNext()


def cmd_destroy(targets, restr, source, *args):
   debug(">>> cmd_destroy({})".format(targets)) #Debug
   for target in targets:
      if target.controller == me:
         destroy(target)
      else:
         remoteCall(target.controller, "destroy", [target, 0, 0, me])
   RulesCommands.applyNext()


def cmd_reveal(targets, restr, source, pileName=None):
   debug(">>> cmd_reveal({})".format(pileName)) #Debug
   if not pileName:
      pileName = RS_KW_ZONE_HAND
   if pileName in RS_KW_ZONES_PILES:
      pile = RulesUtils.getZoneByName(pileName)
      if pile.controller == me:
         # Once the other player is done, apply next command
         remoteCall(getOpp(), "reveal", [pile, "RulesCommands.applyNext"])
         return
      else:
         reveal(pile)
   else:
      debug("{} is not a valid pile".format(pileName))
   RulesCommands.applyNext()


def cmd_discard(targets, restr, source, whichCards):
   debug(">>> cmd_discard({})".format(whichCards)) #Debug
   cardsTokens = RulesLexer.parseTarget(whichCards)
   if not targets == 0:
      targets = [me]
   for player in targets:
      cardsTokens['zone'] = ['', RS_KW_ZONE_HAND]
      if player != me:
         cardsTokens['zone'][0] = RS_KW_TARGET_OPP
      cards = RulesUtils.getTargets(cardsTokens)
      for card in cards:
         if player == me:
            discard(card)
         else:
            remoteCall(player, "discard", [card])
   RulesCommands.applyNext()


def cmd_randomDiscard(targets, restr, source, numCards=1):
   debug(">>> cmd_randomDiscard({})".format(whichCards)) #Debug
   if isNumber(numCards):
      numCards = int(numCards)
   if not targets == 0:
      targets = [me]
   for player in targets:
      if numCards > 0:
         for i in range(0, numCards):
            if player == me:
               randomDiscard()
            else:
               remoteCall(player, "randomDiscard", [])
   RulesCommands.applyNext()


def cmd_moveTo(targets, restr, source, zone):
   debug(">>> cmd_moveTo({}, {})".format(targets, zone)) #Debug
   zonePrefix, zoneName = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone, RS_PREFIX_CTRL)
   if zoneName in RS_KW_ZONES_PILES:
      pile = RulesUtils.getZoneByName(zone)
      for target in targets:
         if zonePrefix == RS_PREFIX_MY or (zonePrefix == RS_PREFIX_CTRL and target.controller == me):
            moveToGroup(pile, target)
         else:
            remoteCall(target.controller, "moveToGroup", [pile, target])
         rnd(1, 100) # Wait until all animation is done
   RulesCommands.applyNext()


def cmd_bp(targets, restr, source, qty):
   mod = False
   if qty[0] == 'x':
      mod = qty[0]
      amount = num(qty[1:])
   else:
      amount = num(qty)
   debug(">>> cmd_bp({}, {}, {}, {})".format(targets, qty, mod, amount)) #Debug
   for target in targets:
      if isCharacter(target):
         newQty = amount
         if mod == 'x':
            newQty = getMarker(target, 'BP') * (amount - 1)
         if target.controller == me:
            modBP(target, newQty)
         else:
            remoteCall(target.controller, "modBP", [target, newQty])
   RulesCommands.applyNext()


RulesCommands.register('damage',     cmd_damage)
RulesCommands.register('swappiles',  cmd_swapPiles)
RulesCommands.register('shuffle',    cmd_shuffle)
RulesCommands.register('destroy',    cmd_destroy)
RulesCommands.register('reveal',     cmd_reveal)
RulesCommands.register('discard',    cmd_discard)
RulesCommands.register('rnddiscard', cmd_randomDiscard)
RulesCommands.register('moveto',     cmd_moveTo)
RulesCommands.register('bp',         cmd_bp)
