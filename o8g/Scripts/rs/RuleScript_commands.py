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

   def __init__(self):
      self.cmds = []
      self.cmdsArgs = []
      self.prevTargets = None

   @staticmethod
   def register(name, cmd):
      RulesCommands.items[name] = cmd


   def applyAll(self, cmds, targets, restr, source, revert=False):
      self.cmds = list(cmds)  # Clone array
      self.cmdsArgs = [targets, restr, source, revert]
      self.applyNext()


   def applyNext(self):
   # Ensures that a command is applied only when the precedent command is done
      if len(self.cmds) > 0:
         cmd = self.cmds.pop(0)
         debug(">>> applyNext({}, {})".format(cmd, self.cmdsArgs)) #Debug
         self.applyCmd(cmd, *self.cmdsArgs)
      elif len(self.cmdsArgs) > 1:
         self.prevTargets = self.cmdsArgs[0]
         self.cmdsArgs = []
      else:
         self.prevTargets = None


   def applyCmd(self, cmd, targets, restr, source, revert=False):
      debug(">>> applyCmd({}, {}, {}, {}, {})".format(cmd, targets, restr, source, revert)) #Debug
      funcStr = cmd[0]
      params = cmd[1]
      
      # Executing command functions
      if funcStr in RulesCommands.items and not revert:
         debug("-- applying cmd '%s' to targets %s (%s)" % (funcStr, targets, restr))
         func = RulesCommands.items[funcStr]
         func(self, targets, source, *params)
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


   def destroy(self):
      debug(">>> RulesCommands.destroy()")
      self.cmds = None
      self.prevTargets = None
      
      
#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def nextCommand():
   commander.applyNext()
      

def disableRule(rule=None):
   debug(">>> disableRule({})".format(rule)) #Debug
   rules = getGlobalVar('Rules')
   rules[rule] = not GameRulesDefaults[rule]
   setGlobalVar('Rules', rules)
   debug("Rule {} has been disabled".format(rule))
   if rule in MSG_RULES:
      notify(MSG_RULES[rule][rules[rule]])


def enableRule(event_card_id=None, rule=None, source_id=None):
   debug(">>> enableRule({})".format(rule)) #Debug
   if event_card_id == source_id:
      rules = getGlobalVar('Rules')
      rules[rule] = GameRulesDefaults[rule]
      setGlobalVar('Rules', rules)
      debug("Rule {} has been enabled".format(rule))
      if rule in MSG_RULES:
         notify(MSG_RULES[rule][rules[rule]])


def alterCost(event_card_id, cardType, mod):
   debug(">>> alterCost({}, {})".format(cardType, mod)) #Debug
   CardCost = getGlobalVar('CardCost')
   if not cardType in CardCost:
       CardCost[cardType] = 0
   CardCost[cardType] += mod
   setGlobalVar('CardCost', CardCost)
   debug("{}'s cost has been modified by {} (now costs {})".format(cardType, mod, CardCost[cardType]))
   notify(MSG_RULES['card_cost'].format(cardType.title(), abs(CardCost[cardType]), 'less' if CardCost[cardType] >= 0 else 'more'))

            
#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmd_damage(rc, targets, source, dmg):
   debug(">>> cmd_damage({}, {})".format(targets, dmg)) #Debug
   if isNumber(dmg):
      dmg = int(dmg)
   else:
      if dmg == 'tgt.bp':
         dmg = getParsedCard(targets[0]).BP
      elif dmg == 'prevtgt.bp':
         dmg = getParsedCard(rc.prevTargets[0]).BP
   for target in targets:
      dealDamage(dmg, target, source)
   rc.applyNext()


def cmd_swapPiles(rc, targets, source, pile1, pile2):
   debug(">>> cmd_swapPiles({}, {}, {})".format(source, pile1, pile2)) #Debug
   pile1 = RulesUtils.getZoneByName(pile1)
   pile2 = RulesUtils.getZoneByName(pile2)
   swapPiles(pile1, pile2)
   rc.applyNext()


def cmd_shuffle(rc, targets, source, pileName=None):
   debug(">>> cmd_shuffle({})".format(pileName)) #Debug
   if not pileName:
      pileName = RS_KW_ZONE_DECK
   prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, pileName)
   if name == RS_KW_ZONE_DECK:
      pile = RulesUtils.getZoneByName(pileName)
      if pile.controller == me:
         shuffle(pile)
      else:
         remoteCall(pile.controller, "shuffle", [pile])
   rnd(1, 100) # Wait until all animation is done
   rc.applyNext()


def cmd_destroy(rc, targets, source, *args):
   debug(">>> cmd_destroy({})".format(targets)) #Debug
   for target in targets:
      if target.controller == me:
         destroy(target)
      else:
         remoteCall(target.controller, "destroy", [target, 0, 0, me])
   rc.applyNext()


def cmd_reveal(rc, targets, source, pileName=None):
   debug(">>> cmd_reveal({})".format(pileName)) #Debug
   if not pileName:
      for card in targets:
         isFaceUp = card.isFaceUp
         card.isFaceUp = True
         notify("{} reveals {} {}.".format(me, card, fromWhereStr(card.group)))
         if isFaceUp == False:
            card.isFaceUp = False
   elif pileName in RS_KW_ZONES_PILES:
      pile = RulesUtils.getZoneByName(pileName)
      if pile.controller == me:
         # Once the other player is done, apply next command
         remoteCall(getOpp(), "reveal", [pile, "nextCommand"])
         return
      else:
         reveal(pile)
   else:
      debug("{} is not a valid pile".format(pileName))
   rc.applyNext()


def cmd_discard(rc, targets, source, whichCards=''):
   debug(">>> cmd_discard({}, {})".format(targets, whichCards)) #Debug
   cardsTokens = RulesLexer.parseTarget(whichCards)
   if not targets:
      targets = [me]
   for player in targets:
      cardsTokens['zone'] = ['', RS_KW_ZONE_HAND]
      if player != me:
         cardsTokens['zone'][0] = RS_KW_TARGET_OPP
      cards = RulesUtils.getTargets(cardsTokens)
      if cards:
         for card in cards:
            if player == me:
               discard(card)
            else:
               remoteCall(player, "discard", [card])
   rc.applyNext()


def cmd_randomDiscard(rc, targets, source, numCards=1):
   debug(">>> cmd_randomDiscard({}, {})".format(targets, numCards)) #Debug
   if not isNumber(numCards):
      numCards = int(numCards)
   if not targets:
      targets = [me]
   if numCards > 0:
      for player in targets:
         for i in range(0, numCards):
            if player == me:
               randomDiscard()
            else:
               remoteCall(player, "randomDiscard", [])
   rc.applyNext()


def cmd_moveTo(rc, targets, source, zone, pos = None, reveal = False):
   debug(">>> cmd_moveTo({}, {})".format(targets, zone)) #Debug
   zonePrefix, zoneName = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone, RS_PREFIX_CTRL)
   if zoneName in RS_KW_ZONES_PILES:      
      if pos == 'true':
         reveal = True
         pos = None
      if pos is not None:
         if pos == '?':
            choice = askChoice("Where to put the card(s)?", ['Top of pile', 'Bottom of pile'])
            pos = (max(choice, 1) - 1) * -1
         pos = num(pos)
      reveal = bool(reveal)
      for target in targets:
         pile = RulesUtils.getZoneByName(zone, target)
         debug("{}'s {} -> {}'s {}".format(target.controller, target, pile.controller, pile.name))
         if target.controller == me and pile.controller == me:
            moveToGroup(pile, target, pos = pos, reveal = reveal)
         elif target.controller == me and pile.controller != me:
            group = target.group
            target.moveToTable(0, 0, True)
            target.controller = pile.controller
            remoteCall(target.controller, "moveToGroup", [pile, target, group, pos, reveal, me])
         elif target.controller != me and pile.controller == me:
            remoteCall(target.controller, "passControlTo", [me, [target], ["moveToGroup", [pile, target, target.group, pos, reveal, me]]])
         else:
            remoteCall(target.controller, "moveToGroup", [pile, target, None, pos, reveal, me])
         rnd(1, 100) # Wait until all animation is done
   rc.applyNext()


def cmd_bp(rc, targets, source, qty):
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
   rc.applyNext()


def cmd_sp(rc, targets, source, qty):
   qty = int(qty)
   if not targets:
      targets = [me]
   debug(">>> cmd_sp({}, {})".format(targets, qty)) #Debug
   if qty > 0:
      for player in targets:
         if player == me:
            modSP(qty)
         else:
            remoteCall(player, "modSP", [qty])
   rc.applyNext()


def cmd_playExtraChar(rc, targets, source, *args):
   global charsPlayed
   debug(">>> cmd_playExtraChar() {} -> {}".format(charsPlayed, charsPlayed-1))
   charsPlayed = 0
   notify("{} can play an additional character this turn.".format(me))
   rc.applyNext()


def cmd_draw(rc, targets, source, qty):
   if qty == '':
      qty = 1
   if isNumber(qty):
      amount = num(qty)
   else:
      amount = num(evalExpression(qty, True))
   if not targets:
      targets = [me]
   debug(">>> cmd_draw({}, {}, {})".format(targets, qty, amount)) #Debug
   for target in targets:
      if isCard(target):
         target = me
      if target == me:
         drawMany(me.Deck, amount)
      else:
         remoteCall(target, "drawMany", [target.Deck, amount])
   rc.applyNext()


def cmd_steal(rc, targets, source, *args):
   debug(">>> cmd_steal({}, {})".format(targets, source)) #Debug
   stealAbility(source, target = targets[0])
   rc.applyNext()


def cmd_loseAbility(rc, targets, source, *args):
   debug(">>> cmd_loseAbility({})".format(targets)) #Debug
   for target in targets:
      toggleAbility(target, remove=True)
      rnd(1, 100) # Wait until all animation is done
   rc.applyNext()


def cmd_each(rc, targets, source, args):
   cond, func = args.split('=>')
   func = RulesLexer.parseAction(func)
   func = func['effects'][0][1]
   debug(">>> cmd_each({}, {}, {})".format(targets, cond, func)) #Debug
   
   res = evalExpression(cond, True)
   if len(res) > 0:
      subrc = RulesCommands()
      for v in res:
         if v:
            subrc.applyAll(func, targets, None, source)
            rnd(1, 100) # Wait between effects until all animation is done
      subrc.destroy()
   
   rc.applyNext()

   
def cmd_transfrom(rc, targets, source, cardName):
   debug(">>> cmd_transfrom({}, {})".format(targets, cardName)) #Debug
   models = queryCard({"Name":cardName}, True)
   if len(models):
      for target in targets:
         transformCard(target, models[0])
         rnd(1,100) # Small wait (bug workaround) to make sure all animations are done.
   rc.applyNext()

   
def cmd_moveRestTo(rc, targets, source, zone):
   pile = me.deck
   index = len(pile)
   targetZone = RulesUtils.getZoneByName(zone)
   if len(targets) > 0:
      pile = targets[0].group
      index = targets[0].index
   debug(">>> cmd_moveRestTo({}, {})".format(zone, index)) #Debug
   notify("{} looks through the top of his {}".format(me, pile.name))
   for i in range(0, index):
      moveToGroup(targetZone, pile[0], pile, reveal = True)
      rnd(1, 100) # Wait between effects until all animation is done
   rc.applyNext()
   
  
def cmd_disableRule(rc, targets, source, rule):
   debug(">>> cmd_disableRule({})".format(rule)) #Debug
   disableRule(rule)
   addGameEventListener(GameEvents.CharRemoved, 'enableRule', source._id, args=[rule, source._id])
   rc.applyNext()


def cmd_freeze(rc, targets, source, *args):
   debug(">>> cmd_freeze({})".format(targets)) #Debug
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = False)
      else:
         remoteCall(target.controller, "unfreeze", [target, 0, 0, False])
   rc.applyNext()


def cmd_unfreeze(rc, targets, source, *args):
   debug(">>> cmd_unfreeze({})".format(targets)) #Debug
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = True)
      else:
         remoteCall(target.controller, "unfreeze", [target, 0, 0, True])
   rc.applyNext()


def cmd_alterCost(rc, targets, source, cardType, mod):
   debug(">>> cmd_alterCost({}, {})".format(cardType, mod)) #Debug
   alterCost(source._id, cardType, num(mod))
   addGameEventListener(GameEvents.CharRemoved, 'alterCost', source._id, args=[cardType, -num(mod)])
   rc.applyNext()


def cmd_swapChars(rc, targets, source, *args):
   debug(">>> cmd_swapChars({})".format(targets)) #Debug
   if targets[0].controller == me:
      changeSlot(targets[0], targets = [targets[1]])
   else:
      remoteCall(targets[0].controller, "changeSlot", [targets[0], 0, 0, [targets[1]]])
   rc.applyNext()


def cmd_moveToSlot(rc, targets, source, *args):
   debug(">>> cmd_moveToSlot({})".format(targets)) #Debug
   if targets[0].controller == me:
      changeSlot(targets[0])
   else:
      remoteCall(targets[0].controller, "changeSlot", [targets[0]])
   rc.applyNext()


def cmd_trash(rc, targets, source, numCards=1):
   debug(">>> cmd_trash({}, {})".format(targets, numCards)) #Debug
   numCards = int(numCards)
   if not targets:
      targets = [me]
   for player in targets:
      if player == me:
         trash(count=numCards)
      else:
         remoteCall(player, "trash", [None, 0, 0, False, numCards])
   rc.applyNext()


def cmd_prophecy(rc, targets, source, numCards=1):
   pile = me.Deck
   if targets:
      pile = targets[0].group
   debug(">>> cmd_prophecy({}, {})".format(numCards, pile)) #Debug
   prophecy(group = pile, count = int(numCards))
   rc.applyNext()
   

RulesCommands.register('damage',        cmd_damage)
RulesCommands.register('swappiles',     cmd_swapPiles)
RulesCommands.register('shuffle',       cmd_shuffle)
RulesCommands.register('destroy',       cmd_destroy)
RulesCommands.register('reveal',        cmd_reveal)
RulesCommands.register('discard',       cmd_discard)
RulesCommands.register('rnddiscard',    cmd_randomDiscard)
RulesCommands.register('moveto',        cmd_moveTo)
RulesCommands.register('bp',            cmd_bp)
RulesCommands.register('sp',            cmd_sp)
RulesCommands.register('playextrachar', cmd_playExtraChar)
RulesCommands.register('draw',          cmd_draw)
RulesCommands.register('steal',         cmd_steal)
RulesCommands.register('loseability',   cmd_loseAbility)
RulesCommands.register('each',          cmd_each)
RulesCommands.register('transform',     cmd_transfrom)
RulesCommands.register('moverestto',    cmd_moveRestTo)
RulesCommands.register('disablerule',   cmd_disableRule)
RulesCommands.register('freeze',        cmd_freeze)
RulesCommands.register('unfreeze',      cmd_unfreeze)
RulesCommands.register('altercost',     cmd_alterCost)
RulesCommands.register('swapchars',     cmd_swapChars)
RulesCommands.register('movetoslot',    cmd_moveToSlot)
RulesCommands.register('trash',         cmd_trash)
RulesCommands.register('prophecy',      cmd_prophecy)
