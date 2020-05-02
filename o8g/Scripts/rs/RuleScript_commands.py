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
         debug(">>> applyNext({}, {})".format(cmd, self.cmdsArgs))
         self.applyCmd(cmd, *self.cmdsArgs)
      elif len(self.cmdsArgs) > 1:
         self.prevTargets = self.cmdsArgs[0]
         self.cmdsArgs = []
      else:
         self.prevTargets = None


   def applyCmd(self, cmd, targets, restr, source, revert=False):
      debug(">>> applyCmd({}, {}, {}, {}, {})".format(cmd, targets, restr, source, revert))
      funcStr = cmd[0]
      params = cmd[1]
      
      if funcStr[-1] == RS_OP_OPT:
         funcStr = funcStr[:-1]
         question = funcStr
         if funcStr in CMD_LABELS:
            question = CMD_LABELS[funcStr]
         if not confirm("{}?".format(question)):
            debug("-- optional cmd: not apply")
            self.applyNext()
            return
      
      # Executing command functions
      if funcStr in RulesCommands.items and not revert:
         debug("-- applying cmd '%s' to targets %s (%s)" % (funcStr, targets, restr))
         func = RulesCommands.items[funcStr]
         func(self, targets, source, restr, *params)
            
      # Abilities/bonus manipulation
      elif funcStr in RS_PREFIX_BONUS:
         for target in targets:
            if funcStr == RS_PREFIX_PLUS:
               if revert:
                  RulesAbilities.remove(params, target._id)
               else:
                  RulesAbilities.add(params, target._id, source._id, restr)
         self.applyNext()
      else:
         debug("-- cmd not found: {}".format(cmd[0]))
         self.applyNext()


   def setTarget(self, target):
      self.cmdsArgs[0] = target


   def destroy(self):
      self.cmds = None
      self.prevTargets = None
      
      
#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def toggleRule(ruleName, value, id, restr = None):
   debug(">>> toggleRule({}, {}, {})".format(ruleName, value, id))
   Rules = getGlobalVar('Rules')
   if not ruleName in Rules:
      Rules[ruleName] = {}
   rule = Rules[ruleName]
   if id in rule:
      del rule[id]
   else:
      if isNumber(value):
         value = int(value)
      rule[id] = value
   setGlobalVar('Rules', Rules)
   debug("Rule {} has been {} ({})".format(ruleName, ('disabled','enabled')[bool(value)], Rules[ruleName]))
   ruleValue = getRule(ruleName)
   if (bool(value) and ruleValue) or (value == False and not ruleValue):
      if ruleName in MSG_RULES:
         restr = getTextualRestr(restr)
         notify(MSG_RULES[ruleName][bool(value)].format(value, restr))


def getLocals(**kwargs): 
# Adds action local variables defined in other places
   locals = {}
   # Convert card IDs into Card objects
   for key, value in getGlobalVar('ActionTempVars').iteritems():
      key = key.lower()
      if isinstance(value, list):
         locals[key] = [stringToObject(id) for id in value]
      else:
         locals[key] = stringToObject(value)
        
   rc = commander
   if kwargs:
      if 'source' in kwargs:
         locals['this'] = kwargs['source']
      if 'targets' in kwargs and len(kwargs['targets']) > 0:
         locals['tgt'] = kwargs['targets'][0]
      if 'rc' in kwargs:
         rc = kwargs['rc']
      
   if rc and rc.prevTargets != None and len(rc.prevTargets) > 0:
      locals['prevtgt'] = rc.prevTargets[0]
      
   # Add some default variables
   if not 'discarded' in locals:
      locals['discarded'] = []
   
   return locals


def getEnvVars(): 
# Adds action global variables
   global envVars
   if not envVars:
      envVars = {
         'me': me,
         # aliases
         'ischar': isCharacter
      }
      # To use in eval()
      globalFuncs = [getParsedCard, isAction, isReaction, isCharacter, getRingSize, getRing, getState, getOpp, getAttackingCards]
      for f in globalFuncs:
         envVars[f.__name__] = f
      # Used in cardRules
      globalFuncs = [flipCoin, isCharacter]
      for f in globalFuncs:
         envVars[f.__name__.lower()] = f
   return envVars


#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmd_damage(rc, targets, source, restr, dmg):
   debug(">>> cmd_damage({}, {})".format(targets, dmg))
   if isNumber(dmg):
      dmg = int(dmg)
   else:
      dmg = evalExpression(dmg, True, getLocals(rc=rc, targets=targets, source=source))
   for target in targets:
      dealDamage(dmg, target, source)
   rc.applyNext()


def cmd_swapPiles(rc, targets, source, restr, pile1, pile2):
   debug(">>> cmd_swapPiles({}, {}, {})".format(source, pile1, pile2))
   pile1 = RulesUtils.getZoneByName(pile1)
   pile2 = RulesUtils.getZoneByName(pile2)
   swapPiles(pile1, pile2)
   rc.applyNext()


def cmd_shuffle(rc, targets, source, restr, pileName=None):
   debug(">>> cmd_shuffle({})".format(pileName))
   if not pileName:
      pileName = RS_KW_ZONE_DECK
   prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, pileName)
   if name in RS_KW_ZONES_PILES:
      target = targets[0] if targets else None
      pile = RulesUtils.getZoneByName(pileName, target)
      if pile.controller == me:
         shuffle(pile)
      else:
         remoteCall(pile.controller, "shuffle", [pile])
   rnd(10, 1000) # Wait until all animation is done
   rc.applyNext()


def cmd_destroy(rc, targets, source, restr, *args):
   debug(">>> cmd_destroy({})".format(targets))
   if not targets:
      targets = [source]
   for target in targets:
      if target.controller == me:
         destroy(target)
      else:
         remoteCall(target.controller, "destroy", [target, 0, 0, me])
      # Add destroyet card to action local variables
   addActionTempVars('destroyed', targets)
   rc.applyNext()


def cmd_reveal(rc, targets, source, restr, pileName=None):
   debug(">>> cmd_reveal({})".format(pileName))
   if not pileName:
      if targets:
         if targets[0].controller == me:
            reveal(targets)
         else:
            remoteCall(getOpp(), "reveal", [targets])
   elif pileName in RS_KW_ZONES_PILES:
      if not targets or isCard(targets[0]):
         targets = [me]
      for player in targets:
         pile = RulesUtils.getZoneByName(pileName, player)
         if pile.controller == me:
            remoteCall(getOpp(), "reveal", [pile])
         else:
            reveal(pile)
   rc.applyNext()


def cmd_discard(rc, targets, source, restr, whichCards=''):
   debug(">>> cmd_discard({}, {})".format(targets, whichCards))
   if isNumber(whichCards):
      whichCards = '<{}>*'.format(whichCards)
   cardsTokens = RulesLexer.parseTarget(whichCards)
   if not targets or isCard(targets[0]):
      targets = [me]
   # Is a random discard?
   if cardsTokens['qty'] and cardsTokens['qty'][0] == RS_KW_RANDOM:
      cmd_randomDiscard(rc, targets, source, restr, RulesUtils.getTargetQty(cardsTokens['qty']).samples)
      return
   # Normal discard
   for player in targets:
      cardsTokens['zone'] = ['', RS_KW_ZONE_HAND]
      if player != me:
         cardsTokens['zone'][0] = RS_KW_TARGET_OPP
      reveal = 'all' if len(targets) == 1 and player != me else False
      cards = RulesUtils.getTargets(cardsTokens, reveal=reveal)
      if cards:
         addActionTempVars('discarded', cards)
         for card in cards:
            if player == me:
               discard(card)
            else:
               remoteCall(player, "discard", [card])
      else:
         notify(MSG_ERR_NO_CARDS_DISCARD.format(player))
   rc.applyNext()


def cmd_randomDiscard(rc, targets, source, restr, numCards=1):
   debug(">>> cmd_randomDiscard({}, {})".format(targets, numCards))
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


def cmd_moveTo(rc, targets, source, restr, zone, pos = None, reveal = None):
   debug(">>> cmd_moveTo({}, {}, {}, {})".format(targets, zone, pos, reveal))
   zonePrefix, zoneName = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone, RS_PREFIX_CTRL)
   if targets:
      if zoneName in RS_KW_ZONES_PILES:
         if isNumber(pos):
            pos = num(pos)
         elif pos == '?':
            choice = askChoice("Where to put the card{}?".format(plural(len(targets))), ['Top of pile', 'Bottom of pile'])
            pos = (max(choice, 1) - 1) * -1
         elif pos is not None:
            reveal = pos
            pos = None
         if reveal is not None:
            reveal = True if reveal == 'true' else False
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
            # Add trashed card to action local variables
         addActionTempVars('moved', targets)
   rc.applyNext()


def cmd_movePile(rc, targets, source, restr, zone1, zone2):
   debug(">>> cmd_movePile({}, {})".format(zone1, zone2))
   z1Prefix, z1Name = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone1, RS_PREFIX_CTRL)
   z2Prefix, z2Name = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone2, RS_PREFIX_CTRL)
   if z1Name in RS_KW_ZONES_PILES and z2Name in RS_KW_ZONES_PILES:
      pile1 = RulesUtils.getZoneByName(zone1)
      pile2 = RulesUtils.getZoneByName(zone2)
      mute()
      for card in pile1:
         card.moveTo(pile2)
      if len(players) > 1: rnd(1, 100) # Wait a bit more, as in multiplayer games, things are slower.
      notify("{} moves all cards from their {} to its {}.".format(me, pile1.name, pile2.name))      
   rc.applyNext()


def cmd_bp(rc, targets, source, restr, qty):
   mode = None
   amount = None
   if isNumber(qty):
      amount = num(qty)
   elif qty[0] in RS_MODES:
      mode = qty[0]
      if isNumber(qty[1:]):
         amount = num(qty[1:])
      else:
         qty = qty[1:]
   if amount == None:
      amount = num(evalExpression(qty, True, getLocals(rc=rc, targets=targets, source=source)))
   if not targets:
      targets = [source]
   debug(">>> cmd_bp({}, {}, {}, {})".format(targets, qty, mode, amount))
   for target in targets:
      if isCharacter(target):
         newQty = amount
         if mode == 'x':
            newQty = getMarker(target, 'BP') * (amount - 1)
         modBP(target, newQty, mode)
   rc.applyNext()


def cmd_sp(rc, targets, source, restr, qty):
   mode = None
   if isNumber(qty):
      amount = num(qty)
   elif qty[0] in RS_MODES:
      mode = qty[0]
      amount = num(qty[1:])
   else:
      amount = num(evalExpression(qty, True, getLocals(rc=rc, targets=targets, source=source)))
   if not targets or isCard(targets[0]):
      targets = [me]
   debug(">>> cmd_sp({}, {}, {})".format(targets, amount, mode))
   for player in targets:
      modSP(amount, mode, player=player)
   rc.applyNext()


def cmd_hp(rc, targets, source, restr, qtyExpr):
   if isNumber(qtyExpr):
      qty = int(qtyExpr)
   else:
      qty = evalExpression(qtyExpr, True, getLocals(rc=rc, targets=targets, source=source))
   if not targets or isCard(targets[0]):
      targets = [me]
   debug(">>> cmd_hp({}, {}) => {}".format(targets, qtyExpr, qty))
   for player in targets:
      player.HP += qty
      sign = '+' if qty >= 0 else ''
      notify("{} sets {}'s HP to {} ({}{})".format(me, player, player.HP, sign, qty))
   rc.applyNext()


def cmd_playExtraChar(rc, targets, source, restr, *args):
   cpt = getState(me, 'charsPerTurn')
   debug(">>> cmd_playExtraChar() {} -> {}".format(cpt, cpt+1))
   setState(me, 'charsPerTurn', cpt+1)
   notify("{} can play an additional character this turn.".format(me))
   rc.applyNext()


def cmd_draw(rc, targets, source, restr, qty = None):
   if qty == '' or not qty:
      qty = 1
   if isNumber(qty):
      amount = num(qty)
   else:
      amount = num(evalExpression(qty, True, getLocals(rc=rc, targets=targets, source=source)))
   if not targets or isCard(targets[0]):
      targets = [me]
   debug(">>> cmd_draw({}, {}, {})".format(targets, qty, amount))
   for target in targets:
      if target == me:
         drawMany(me.Deck, amount)
      else:
         remoteCall(target, "drawMany", [target.Deck, amount])
   rc.applyNext()


def cmd_steal(rc, targets, source, restr, extraSource = None):
   if extraSource:
      cardsTokens = RulesLexer.parseTarget(extraSource)
      cards = RulesUtils.getTargets(cardsTokens)
      if cards:
         source = cards[0]
   debug(">>> cmd_steal({}, {}, {})".format(targets, source, extraSource))
   stealAbility(source, target = targets[0])
   rc.applyNext()


def cmd_loseAbility(rc, targets, source, restr, *args):
   debug(">>> cmd_loseAbility({})".format(targets))
   for target in targets:
      toggleAbility(target, remove=True)
      rnd(1, 100) # Wait until all animation is done
   rc.applyNext()
   

def cmd_copyAbility(rc, targets, source, restr, expr):
   debug(">>> cmd_copyAbility({}, {}, {})".format(targets, source, expr))
   card = evalExpression(expr, True, getLocals(rc=rc, targets=targets, source=source))
   if not targets:
      targets = [source]
   if card:
      for target in targets:
         copyAbility(target, target = card)
   rc.applyNext()


def cmd_swapAbilities(rc, targets, source, restr, *args):
   debug(">>> cmd_swapAbilities({}, {})".format(targets, source))
   swapAbilities(targets[0], target = targets[1])
   rc.applyNext()
   

def cmd_each(rc, targets, source, restr, args):
   cond, func = args.split(RS_KW_ARROW)
   func = RulesLexer.parseAction(func)
   func = func['effects'][0][1]
   debug(">>> cmd_each({}, {}, {})".format(targets, cond, func))
   
   if not ' in ' in cond:
      tokens = RulesLexer.parseTarget(cond)
      res = RulesUtils.getTargets(tokens, source=source, reveal=False)
   else:
      res = evalExpression(cond, True, getLocals(rc=rc, targets=targets, source=source))
   
   if res and len(res) > 0:
      subrc = RulesCommands()
      for v in res:
         if v:
            subrc.applyAll(func, targets, None, source)
            rnd(1, 100) # Wait between effects until all animation is done
      subrc.destroy()
   update()
   rc.applyNext()

   
def cmd_transform(rc, targets, source, restr, expr):
   model = None
   models = queryCard({"Name":expr}, True)
   if len(models):
      model = models[0]
   else:
      card = evalExpression(expr, True, getLocals(rc=rc, targets=targets, source=source))
      if card:
         model = card.model
   debug(">>> cmd_transfrom({}, {}) => {}".format(targets, expr, model))
   if model:
      for target in targets:
         if target.controller == me:
            transformCard(target, model)
         else:
            remoteCall(target.controller, "transformCard", [target, model])
         rnd(1,100) # Small wait (bug workaround) to make sure all animations are done.
   rc.applyNext()

   
def cmd_moveRestTo(rc, targets, source, restr, zone, pos = None):
   pile = me.deck
   index = len(pile)
   if len(targets) > 0:
      pile = targets[0].group
      index = targets[0].index
   newPile = [pile[i] for i in range(0, index)]
   targetZone = RulesUtils.getZoneByName(zone, pile[0])
   myPile = targetZone.controller == me
   debug(">>> cmd_moveRestTo({}, {}, {})".format(zone, index, pos))
   notify("{} looks through the top of {} {} ({} card{} revealed)".format(me, 'his' if myPile else players[1], pile.name, index+1, plural(index+1)))
   for card in newPile:
      if myPile:
         moveToGroup(targetZone, card, pile, num(pos), True)
      else:
         remoteCall(targetZone.controller, "moveToGroup", [targetZone, card, pile, num(pos), True])
      rnd(1, 100) # Wait between effects until all animation is done
   rc.applyNext()
   
  
def cmd_disableRule(rc, targets, source, restr, rule):
   debug(">>> cmd_disableRule({})".format(rule))
   toggleRule(rule, False, source._id, restr)
   args = ['toggleRule', source._id, None, restr, [rule, True, source._id, restr]]
   if isCharacter(Card(source._id)):
      addGameEventListener(GameEvents.Removed,   *args)
      addGameEventListener(GameEvents.Powerless, *args)
   if restr:
      addGameEventListener(GameEvents.EndPhase, *args)
   rc.applyNext()
   
   
def cmd_enableRule(rc, targets, source, restr, rule, value = True):
   debug(">>> cmd_enableRule({})".format(rule))
   toggleRule(rule, value, source._id, restr)
   args = ['toggleRule', source._id, None, restr, [rule, False, source._id, restr]]
   if isCharacter(Card(source._id)):
      addGameEventListener(GameEvents.Removed,   *args)
      addGameEventListener(GameEvents.Powerless, *args)
   if restr:
      addGameEventListener(GameEvents.EndPhase, *args)
   rc.applyNext()


def cmd_freeze(rc, targets, source, restr, unfreeze=False):
   debug(">>> cmd_freeze({}, {})".format(targets, unfreeze))
   if bool(unfreeze):
      unfreeze = None
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = unfreeze)
      else:
         remoteCall(target.controller, "freeze", [target, 0, 0, unfreeze])
   rc.applyNext()


def cmd_unfreeze(rc, targets, source, restr, *args):
   debug(">>> cmd_unfreeze({})".format(targets))
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = True)
      else:
         remoteCall(target.controller, "freeze", [target, 0, 0, True])
   rc.applyNext()


def cmd_alterCost(rc, targets, source, restr, type, mod):
   debug(">>> cmd_alterCost({}, {})".format(type, mod))
   mode = None
   msg = MSG_RULES['card_cost']
   if 'cost_' + type in MSG_RULES:
      msg = MSG_RULES['cost_' + type]
   if isNumber(mod):
      mod = num(mod)
      notify(msg.format(type.title(), abs(mod), 'less ' if mod >= 0 else 'more ', getTextualRestr(restr)))
   else:
      mode = mod[0]
      mod = num(mod[1:])
      notify(msg.format(type.title(), mod, '', getTextualRestr(restr)))
      
   addGameMod('cost', source._id, type, mod, mode)
   
   if restr:
      addGameEventListener(Hooks.CallOnRemove, 'removeGameMod', source._id, restr=restr, args=[source._id])
   else:
      msg = msg.format(type.title(), abs(mod), 'more ' if mod >= 0 else 'less ', '')
      addGameEventListener(GameEvents.Removed,   'removeGameMod', source._id, args=[source._id, msg])
      addGameEventListener(GameEvents.Powerless, 'removeGameMod', source._id, args=[source._id, msg])
   rc.applyNext()


def cmd_swapChars(rc, targets, source, restr, *args):
   debug(">>> cmd_swapChars({})".format(targets))
   if len(targets) >= 2:
      if targets[0].controller == me:
         changeSlot(targets[0], targets = [targets[1]])
      else:
         remoteCall(targets[0].controller, "changeSlot", [targets[0], 0, 0, [targets[1]]])
   rc.applyNext()


def cmd_moveToSlot(rc, targets, source, restr, *args):
   debug(">>> cmd_moveToSlot({})".format(targets))
   if targets[0].controller == me:
      changeSlot(targets[0])
   else:
      remoteCall(targets[0].controller, "changeSlot", [targets[0]])
   rc.applyNext()


def cmd_trash(rc, targets, source, restr, numCards=1):
   debug(">>> cmd_trash({}, {})".format(targets, numCards))
   numCards = int(numCards)
   if not targets or isCard(targets[0]):
      targets = [me]
   for player in targets:
      if player == me:
         trash(me.Deck, count=numCards)
      else:
         remoteCall(player, "trash", [None, 0, 0, False, numCards])
   rc.applyNext()


def cmd_prophecy(rc, targets, source, restr, numCards=1, deckPos=0):
   pile = me.Deck
   if targets:
      pile = targets[0].group
   if deckPos != 0:
      if deckPos == 'top':
         deckPos = 1
      else:
         deckPos = 2
   debug(">>> cmd_prophecy({}, {}, {})".format(numCards, pile, deckPos))
   prophecy(group = pile, count = int(numCards), deckPos = deckPos)
   rc.applyNext()


def cmd_activate(rc, targets, source, restr, expr):
   debug(">>> cmd_activate({})".format(expr))
   card = evalExpression(expr, True, getLocals(rc=rc, targets=targets, source=source))
   if card:
      pcard = parseCard(source, card.model, dryRun = True)
      pcard.activateEffect()
   rc.applyNext()
   

def cmd_turns(rc, targets, source, restr, qty):
   global turns
   qty = int(qty)
   debug(">>> cmd_turns({}, {})".format(targets, qty))
   turns += qty
   if qty > 0:
      notify("{} will play another turn after this one".format(me))
   elif qty < 0:
      notify("{} will skip his next turn".format(me))
      
   rc.applyNext()
   

def cmd_skip(rc, targets, source, restr, phase):
   phases = map(str.lower, Phases)
   idx = phases.index(phase)
   debug(">>> cmd_skip({}, {} ({}))".format(targets, phase, idx))
   for player in targets:
      skipPhases = getState(player, 'skip')
      if not idx in skipPhases:
         skipPhases.append(idx)
         setState(player, 'skip', skipPhases)
      notify("{} will skip his next {} phase.".format(player, phase.title()))
   rc.applyNext()
   
   
def cmd_unite(rc, targets, source, restr, *args):
   debug(">>> cmd_unite({})".format(targets))
   if targets:
      uattack = getGlobalVar('UnitedAttack')
      if len(uattack) > 0:
         target = Card(uattack[0])
      else:
         target = targets[0]
      for card in targets:
         if card != target:
            remoteCall(getOpp(), "unitedAttackAuto", [card, [target], False])
            rnd(1, 100) # Wait until all animation is done
      notify("{} has forced {} to do an United Attack".format(me, cardsNamesStr(targets)))
   rc.applyNext()
   rc.applyNext()
   
   
def cmd_removeFromAttack(rc, targets, source, restr, *args):
   debug(">>> cmd_removeFromAttack({})".format(targets))
   for card in targets:
      remoteCall(getOpp(), "attackAuto", [card, True])
      rnd(1, 100) # Wait until all animation is done
      notify("{} removes {} from attack.".format(me, card))
   rc.applyNext()
   

RulesCommands.register('damage',           cmd_damage)
RulesCommands.register('swappiles',        cmd_swapPiles)
RulesCommands.register('shuffle',          cmd_shuffle)
RulesCommands.register('destroy',          cmd_destroy)
RulesCommands.register('reveal',           cmd_reveal)
RulesCommands.register('discard',          cmd_discard)
RulesCommands.register('rnddiscard',       cmd_randomDiscard)
RulesCommands.register('moveto',           cmd_moveTo)
RulesCommands.register('movepile',         cmd_movePile)
RulesCommands.register('bp',               cmd_bp)
RulesCommands.register('sp',               cmd_sp)
RulesCommands.register('hp',               cmd_hp)
RulesCommands.register('playextrachar',    cmd_playExtraChar)
RulesCommands.register('draw',             cmd_draw)
RulesCommands.register('steal',            cmd_steal)
RulesCommands.register('loseability',      cmd_loseAbility)
RulesCommands.register('copyability',      cmd_copyAbility)
RulesCommands.register('swapabilities',    cmd_swapAbilities)
RulesCommands.register('each',             cmd_each)
RulesCommands.register('transform',        cmd_transform)
RulesCommands.register('moverestto',       cmd_moveRestTo)
RulesCommands.register('disablerule',      cmd_disableRule)
RulesCommands.register('enablerule',       cmd_enableRule)
RulesCommands.register('modrule',          cmd_enableRule)  # alias
RulesCommands.register('freeze',           cmd_freeze)
RulesCommands.register('unfreeze',         cmd_unfreeze)
RulesCommands.register('altercost',        cmd_alterCost)
RulesCommands.register('swapchars',        cmd_swapChars)
RulesCommands.register('movetoslot',       cmd_moveToSlot)
RulesCommands.register('trash',            cmd_trash)
RulesCommands.register('prophecy',         cmd_prophecy)
RulesCommands.register('activate',         cmd_activate)
RulesCommands.register('turns',            cmd_turns)
RulesCommands.register('skip',             cmd_skip)
RulesCommands.register('unite',            cmd_unite)
RulesCommands.register('removefromattack', cmd_removeFromAttack)
