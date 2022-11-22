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
# Commands class
#---------------------------------------------------------------------------

class RulesCommands():
   """
   Class to handle the commands that are applied to a set of objects.
   """
   items = {}

   def __init__(self):
      self.cmds = []
      self.cmdsArgs = []
      self.prevTargets = None
      self.lastCmdSuccess = None

   @staticmethod
   def register(name, cmd):
      RulesCommands.items[name] = cmd


   def applyAll(self, cmds, targets, restr, source, revert = False):
      self.cmds = list(cmds)  # Clone array
      self.cmdsArgs = [targets, restr, source, revert]
      self.lastCmdSuccess = True
      self.applyNext()


   def applyNext(self, success = True):
      """
      Ensures that a command is applied only when the precedent command is done.
      """
      debug(">>> applyNext(success: {})", success)
      self.lastCmdSuccess = success
      if len(self.cmds) > 0:
         cmd = self.cmds.pop(0)
         debug("-- next cmd: {}({})", cmd, self.cmdsArgs)
         self.applyCmd(cmd, *self.cmdsArgs)
      # Save target for next action
      elif len(self.cmdsArgs) > 1:
         debug("-- empty queue, saving prevTargets to {}", self.cmdsArgs[0])
         self.prevTargets = self.cmdsArgs[0]
         self.cmdsArgs = []
      else:
         debug("-- empty queue, clearing prevTargets")
         self.prevTargets = None


   def applyCmd(self, cmd, targets, restr, source, revert = False):
      debug(">>> applyCmd({}, {}, {}, {}, {})", cmd, targets, restr, source, revert)
      funcStr = cmd[0]
      params = cmd[1]
      # Last character can mark cmd as optional
      if funcStr[-1] == RS_OP_OPT:
         debug("-- it's an optional cmd")
         funcStr = funcStr[:-1]
         question = funcStr
         if funcStr in CMD_LABELS:
            question = CMD_LABELS[funcStr]
         if not confirm("{}?".format(question)):
            debug("-- optional cmd: not apply, skip and go next")
            self.applyNext()
            return
      # Executing command functions
      if funcStr in RulesCommands.items and not revert:
         debug("-- applying cmd '{}' to targets {} ({})", funcStr, targets, restr)
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
            # if funcStr == RS_PREFIX_MINUS:
         self.applyNext()
      else:
         if funcStr in RulesCommands.items:
            debug("-- skipping cmd {} because condition does not match", cmd[0])
         else:
            debug("-- cmd not found: {}", cmd[0])
         self.applyNext()


   def setTarget(self, target):
      self.cmdsArgs[0] = target


   def dispose(self):
      self.cmds = None
      self.prevTargets = None


#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmd_damage(rc, targets, source, restr, dmg):
   debug(">>> cmd_damage({}, {})", targets, dmg)
   if isNumber(dmg):
      dmg = int(dmg)
   else:
      dmg = evalExpression(dmg, True, getLocals(rc = rc, targets = targets, source = source))
   for target in targets:
      dealDamage(dmg, target, source, combatDmg = False)
   rc.applyNext()


def cmd_loseLife(rc, targets, source, restr, qty):
   debug(">>> cmd_loseLife({}, {})", targets, qty)
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   for target in targets:
      loseLife(int(qty), target, source)
   rc.applyNext()


def cmd_swapPiles(rc, targets, source, restr, pile1, pile2):
   debug(">>> cmd_swapPiles({}, {}, {})", source, pile1, pile2)
   pile1 = RulesUtils.getPileByName(pile1)
   pile2 = RulesUtils.getPileByName(pile2)
   swapPiles(pile1, pile2)
   rc.applyNext()


def cmd_shuffle(rc, targets, source, restr, pileName = None):
   debug(">>> cmd_shuffle({})", pileName)
   if not pileName:
      pileName = RS_KW_ZONE_DECK
   prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, pileName)
   if name in RS_KW_ZONES_PILES:
      target = targets[0] if targets else None
      pile = RulesUtils.getPileByName(pileName, target)
      if pile.controller == me:
         shuffle(pile)
      else:
         remoteCall(pile.controller, "shuffle", [pile])
   waitForAnimation()
   rc.applyNext()


def cmd_destroy(rc, targets, source, restr, *args):
   debug(">>> cmd_destroy({})", targets)
   if not targets:
      targets = [source]
   for target in targets:
      if target.controller == me:
         destroy(target)
      else:
         remoteCall(target.controller, "destroy", [target, me])
      update()
   # Add destroyed cards to action local variables
   addTempVar("destroyed", targets)
   rc.applyNext()


def cmd_reveal(rc, targets, source, restr, pileName = None):
   debug(">>> cmd_reveal({})", pileName)
   if not pileName:
      if targets:
         if targets[0].controller == me:
            reveal(targets)
            remoteCall(getOpp(), "showCardDlg", [targets, "Cards revealed by {}".format(me)])
         else:
            remoteCall(getOpp(), "reveal", [targets])
            showCardDlg(targets, "Cards revealed by {}".format(getOpp()))
   elif pileName in RS_KW_ZONES_PILES:
      if not targets or isCard(targets[0]):
         targets = [source.controller]
      for player in targets:
         pile = RulesUtils.getPileByName(pileName, player)
         if pile.controller == me:
            remoteCall(getOpp(), "reveal", [pile])
         else:
            reveal(pile)
   rc.applyNext()


def cmd_discard(rc, targets, source, restr, whichCards = ""):
   debug(">>> cmd_discard({}, {})", targets, whichCards)
   success = True
   if isNumber(whichCards):
      whichCards = "<{}>*".format(whichCards)
   cardsTokens = RulesLexer.parseTarget(whichCards)
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   # It's a random discard?
   if cardsTokens["qty"] and cardsTokens["qty"][0] == RS_KW_RANDOM:
      cmd_randomDiscard(rc, targets, source, restr, RulesUtils.getTargetQty(cardsTokens["qty"]).samples)
      return
   # Normal discard
   for player in targets:
      cardsTokens["zone"] = ["", RS_KW_ZONE_HAND]
      if player != me:
         cardsTokens["zone"][0] = RS_KW_TARGET_OPP
      reveal = "all" if len(targets) == 1 and player != me else False
      cards = RulesUtils.getTargets(cardsTokens, reveal = reveal)
      if cards:
         addTempVar("discarded", cards)
         for card in cards:
            if player == me:
               discard(card)
            else:
               remoteCall(player, "discard", [card])
      else:
         if whichCards == "all":
            notify(MSG_ERR_NO_CARDS_DISCARD, player)
         else:
            notify(MSG_ERR_NO_CARDS_DISCARD_F, player)
         success = False
      # Peek cards
      if reveal or len(targets) > 1:
         if player == me:
            remoteCall(getOpp(), "cardPeek", [player.hand])
         else:
            cardPeek(player.hand)
   rc.applyNext(success)


def cmd_randomDiscard(rc, targets, source, restr, numCards = 1):
   debug(">>> cmd_randomDiscard({}, {})", targets, numCards)
   if not targets:
      targets = [source.controller]
   if numCards > 0:
      for player in targets:
         for i in range(0, numCards):
            if player == me:
               randomDiscard()
            else:
               remoteCall(player, "randomDiscard", [])
   rc.applyNext()


def cmd_moveTo(rc, targets, source, restr, zone, pos = None, reveal = None):
   debug(">>> cmd_moveTo({}, {}, {}, {})", targets, zone, pos, reveal)
   # This cmd cannot have default targets
   mute()
   zonePrefix, zoneName = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone, RS_PREFIX_CTRL)
   if targets:
      if zoneName in RS_KW_ZONES_PILES:
         if isNumber(pos):
            pos = int(pos)
         elif pos == "?":
            choice = askChoice("Where to put the card{}?".format(pluralize(len(targets))), ["Top of pile", "Bottom of pile"])
            pos = (max(choice, 1) - 1) * -1
         elif pos is not None:
            reveal = pos
            pos = None
         if reveal is not None:
            reveal = True if reveal == True else False
         msgs = []
         for target in targets:
            pile = RulesUtils.getPileByName(zone, target)
            debug("{}'s {} -> {}'s {} {} ({})", target.controller, target, pile.controller, pile.name, pos, reveal)
            if target.controller == me and pile.controller == me:
               msg = moveToGroup(pile, target, pos = pos, reveal = reveal, silent = True)
               msgs.append(msg)
            elif target.controller == me and pile.controller != me:
               group = target.group
               target.moveToTable(0, 0, True)
               target.controller = pile.controller
               remoteCall(target.controller, "moveToGroup", [pile, target, group, pos, reveal, source.controller])
            elif target.controller != me and pile.controller == me:
               remoteCall(target.controller, "passControlTo", [me, [target], "moveToGroup", [pile, target, target.group, pos, reveal, source.controller]])
            else:
               remoteCall(target.controller, "moveToGroup", [pile, target, None, pos, reveal, source.controller])
            waitForAnimation()
         if msgs:
            notify("\n".join(msgs))
      else:
         targets = []
   # Add moved card to action local variables
   addTempVar("moved", targets)
   rc.applyNext()


def cmd_movePile(rc, targets, source, restr, zone1, zone2):
   debug(">>> cmd_movePile({}, {})", zone1, zone2)
   z1Prefix, z1Name = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone1, RS_PREFIX_CTRL)
   z2Prefix, z2Name = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone2, RS_PREFIX_CTRL)
   if z1Name in RS_KW_ZONES_PILES and z2Name in RS_KW_ZONES_PILES:
      pile1 = RulesUtils.getPileByName(zone1)
      pile2 = RulesUtils.getPileByName(zone2)
      mute()
      for card in pile1:
         card.moveTo(pile2)
      if len(players) > 1:
         waitForAnimation()
      notify("{} moves all cards from their {} to their {}.", me, pile1.name, pile2.name)
   rc.applyNext()


def cmd_bp(rc, targets, source, restr, qty):
   mode = None
   amount = None
   if isNumber(qty):
      amount = int(qty)
   elif qty[0] in RS_MODES:
      mode = qty[0]
      if isNumber(qty[1:]):
         amount = int(qty[1:])
      else:
         qty = qty[1:]
   if amount == None:
      amount = num(evalExpression(qty, True, getLocals(rc = rc, targets = targets, source = source)))
   if not targets:
      targets = [source]
   debug(">>> cmd_bp({}, {}, {}, {})", targets, qty, mode, amount)
   for target in targets:
      if isCharacter(target):
         newQty = amount
         if mode == "x":
            newQty = getMarker(target, "BP") * (amount - 1) # New markers will be added on top of the existing
         modBP(target, newQty, mode)
   rc.applyNext()


def cmd_sp(rc, targets, source, restr, qty):
   mode = None
   if isNumber(qty):
      amount = int(qty)
   elif qty[0] in RS_MODES:
      mode = qty[0]
      amount = int(qty[1:])
   else:
      amount = num(evalExpression(qty, True, getLocals(rc = rc, targets = targets, source = source)))
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   debug(">>> cmd_sp({}, {}, {})", targets, amount, mode)
   for player in targets:
      modSP(amount, mode, player = player)
   rc.applyNext()


def cmd_hp(rc, targets, source, restr, qtyExpr):
   if isNumber(qtyExpr):
      qty = int(qtyExpr)
   else:
      qty = evalExpression(qtyExpr, True, getLocals(rc = rc, targets = targets, source = source))
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   debug(">>> cmd_hp({}, {}) => {}", targets, qtyExpr, qty)
   for player in targets:
      player.HP = getState(player, "HP") + qty
      sign = "+" if qty >= 0 else ""
      notify("{} sets {}'s HP to {} ({}{})", me, player, player.HP, sign, qty)
      if qty > 0:
         playSnd("gain-life")
   rc.applyNext()


def cmd_playExtraChar(rc, targets, source, restr, *args):
   cpt = getState(me, "charsPerTurn")
   debug(">>> cmd_playExtraChar() {} -> {}", cpt, cpt + 1)
   setState(me, "charsPerTurn", cpt + 1)
   notify("{} can play an additional character this turn.", me)
   rc.applyNext()


def cmd_draw(rc, targets, source, restr, qty = None):
   if qty == "" or not qty:
      qty = 1
   if isNumber(qty):
      amount = int(qty)
   else:
      amount = num(evalExpression(qty, True, getLocals(rc = rc, targets = targets, source = source)))
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   debug(">>> cmd_draw({}, {}, {})", targets, qty, amount)
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
   debug(">>> cmd_steal({}, {}, {})", targets, source, extraSource)
   stealAbility(source, target = targets[0])
   rc.applyNext()


def cmd_loseAbility(rc, targets, source, restr, *args):
   debug(">>> cmd_loseAbility({})", targets)
   for target in targets:
      toggleAbility(target, remove = True)
      update()
   rc.applyNext()
   

def cmd_copyAbility(rc, targets, source, restr, expr):
   debug(">>> cmd_copyAbility({}, {}, {})", targets, source, expr)
   card = evalExpression(expr, True, getLocals(rc = rc, targets = targets, source = source))
   if card:
      if not targets:
         targets = [source]
      for target in targets:
         # copyAbility(target, target = card)
         funcCall(target.controller, copyAbility, [target, 0, 0, card])
         update()
   rc.applyNext()


def cmd_swapAbilities(rc, targets, source, restr, *args):
   debug(">>> cmd_swapAbilities({}, {})", targets, source)
   swapAbilities(targets[0], target = targets[1])
   rc.applyNext()
   

def cmd_each(rc, targets, source, restr, args):
   cond, func = args.split(RS_KW_ARROW)
   func = RulesLexer.parseAction(func)
   func = func["effects"][0][1]
   debug(">>> cmd_each({}, {}, {})", targets, cond, func)
   
   if not " in " in cond:
      tokens = RulesLexer.parseTarget(cond)
      res = RulesUtils.getTargets(tokens, source = source, reveal = False)
   else:
      res = evalExpression(cond, True, getLocals(rc = rc, targets = targets, source = source))
   
   if res and len(res) > 0:
      subrc = RulesCommands()
      for v in res:
         if v:
            subrc.applyAll(func, targets, None, source)
            # waitForAnimation()
      subrc.dispose()
   update()
   rc.applyNext()

   
def cmd_transform(rc, targets, source, restr, expr):
   model = None
   expr = RulesLexer.stripQuotes(expr)
   # Is expr a literal with a UUID?
   if RS_RGX_UUID.match(expr):
      model = expr
   else:
      card = evalExpression(expr, True, getLocals(rc = rc, targets = targets, source = source))
      if card:
         model = card.model
   debug(">>> cmd_transfrom({}, {}) => {}", targets, expr, model)
   if model:
      for target in targets:
         if target.controller == me:
            transformCard(target, model)
         else:
            remoteCall(target.controller, "transformCard", [target, model])
         waitForAnimation()
   rc.applyNext()

   
def cmd_moveRevealedCardsTo(rc, targets, source, restr, zone, pos = None):
   debug(">>> cmd_moveRevealedCardsTo({}, {})", zone, pos)
   pile = me.deck
   index = len(pile)
   success = True
   # Maybe there is a selected card
   if len(targets) > 0:
      pile = targets[0].group
      index = targets[0].index
   # Do nothing if there ain't cards in the pile
   if len(pile) > 0:
      newPile = [pile[i] for i in range(0, index)]
      targetZone = RulesUtils.getPileByName(zone, pile[0])
      myPile = targetZone.controller == me
      debug("Moving up to {} cards to {} in pos {}", index, zone, pos)
      notify("{} looks through the top of {} {} ({} card{} revealed)", me, "his" if myPile else players[1], pile.name, index + 1, pluralize(index + 1))
      for card in newPile:
         if myPile:
            moveToGroup(targetZone, card, pile, num(pos), True)
         else:
            remoteCall(targetZone.controller, "moveToGroup", [targetZone, card, pile, num(pos), True])
         waitForAnimation()
   else:
      success = False
   rc.applyNext(success)
   
   
def cmd_enableRule(rc, targets, source, restr, rule, value = True):
   debug(">>> cmd_enableRule({}, {})", rule, value)
   player = None
   if targets and isPlayer(targets[0]):
      player = targets[0]._id
   toggleRule(rule, value, source._id, restr, player)
   args = ["toggleRule", source._id, None, restr, [rule, GameRulesDefaults[rule], source._id, restr, player]]
   if isCharacter(Card(source._id)) and not restr:
      addGameEventListener(GameEvents.Removed,   *args)
      addGameEventListener(GameEvents.Powerless, *args)
   if restr:
      addGameEventListener(Hooks.CallOnRemove, *args)
   rc.applyNext()
   
  
def cmd_disableRule(rc, targets, source, restr, rule):
   debug(">>> cmd_disableRule({})", rule)
   cmd_enableRule(rc, targets, source, restr, rule, False)


def cmd_freeze(rc, targets, source, restr, toggle = False):
   debug(">>> cmd_freeze({}, {})", targets, toggle)
   # Any value other than False will be None to toggle the freeze state
   if bool(toggle):
      toggle = None
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = toggle)
      else:
         remoteCall(target.controller, "freeze", [target, 0, 0, toggle])
   rc.applyNext()


def cmd_unfreeze(rc, targets, source, restr, *args):
   debug(">>> cmd_unfreeze({})", targets)
   for target in targets:
      if target.controller == me:
         freeze(target, unfreeze = True)
      else:
         remoteCall(target.controller, "freeze", [target, 0, 0, True])
   rc.applyNext()


def cmd_alterCost(rc, targets, source, restr, type, mod):
   debug(">>> cmd_alterCost({}, {}, {})", type, mod, restr)
   mode = None
   msg = MSG_RULES["card_cost"]
   if "cost_" + type in MSG_RULES:
      msg = MSG_RULES["cost_" + type]
   if isNumber(mod):
      mod = int(mod)
      notify(msg.format(type.title(), abs(mod), "less " if mod >= 0 else "more ", getTextualRestr(restr)))
   else:
      mode = mod[0]
      mod = int(mod[1:])
      notify(msg.format(type.title(), mod, "", getTextualRestr(restr)))
   addGameMod("cost", source._id, type, mod, mode)
   if restr:
      addGameEventListener(Hooks.CallOnRemove, "removeGameMod", source._id, restr = restr, args = [source._id])
   else:
      msg = msg.format(type.title(), abs(mod), "more " if mod >= 0 else "less ", "")
      addGameEventListener(GameEvents.Removed,   "removeGameMod", source._id, args = [source._id, msg])
      addGameEventListener(GameEvents.Powerless, "removeGameMod", source._id, args = [source._id, msg])
   rc.applyNext()


def cmd_modCost(rc, targets, source, restr, type, mod):
   debug(">>> cmd_modCost({}, {})", type, mod)
   mod = int(mod)
   addTempVar("costMod" + type, mod, True)
   notify(MSG_RULES["card_cost"].format(type.title(), abs(mod), "less " if mod >= 0 else "more ", getTextualRestr(restr)))
   rc.applyNext()


def cmd_swapChars(rc, targets, source, restr, *args):
   debug(">>> cmd_swapChars({})", targets)
   if len(targets) >= 2:
      if targets[0].controller == me:
         changeSlot(targets[0], targets = [targets[1]])
      else:
         remoteCall(targets[0].controller, "changeSlot", [targets[0], 0, 0, [targets[1]]])
   rc.applyNext()


def cmd_moveToSlot(rc, targets, source, restr, *args):
   debug(">>> cmd_moveToSlot({})", targets)
   if targets[0].controller == me:
      changeSlot(targets[0])
   else:
      remoteCall(targets[0].controller, "changeSlot", [targets[0]])
   rc.applyNext()


def cmd_trash(rc, targets, source, restr, numCards = 1):
   debug(">>> cmd_trash({}, {})", targets, numCards)
   numCards = int(numCards)
   if not targets or isCard(targets[0]):
      targets = [source.controller]
   for player in targets:
      if player == me:
         trash(me.Deck, count = numCards)
      else:
         remoteCall(player, "trash", [None, 0, 0, numCards])
   rc.applyNext()


def cmd_prophecy(rc, targets, source, restr, numCards = 1, deckPos = False):
   pile = source.controller.Deck
   if targets:
      pile = targets[0].group
   if deckPos == "top":
      deckPos = 0
   elif deckPos == "bottom":
      deckPos = -1
   debug(">>> cmd_prophecy({}, {}, {})", numCards, pile, deckPos)
   prophecy(group = pile, count = int(numCards), deckPos = deckPos)
   rc.applyNext()


def cmd_activate(rc, targets, source, restr, expr):
   debug(">>> cmd_activate({})", expr)
   card = evalExpression(expr, True, getLocals(rc = rc, targets = targets, source = source))
   if card:
      pcard = createGameCard(source, card.model, dryRun = True)
      pcard.activateEffect()
      pcard.destroy()
      del pcard
   rc.applyNext()
   

def cmd_turns(rc, targets, source, restr, qty):
   qty = int(qty)
   debug(">>> cmd_turns({}, {})", targets, qty)
   me.turnsRemaining += qty
   if qty > 0:
      notify("{} will play another turn after this one", me)
   elif qty < 0:
      notify("{} will skip his next turn", me)
   rc.applyNext()
   

def cmd_skip(rc, targets, source, restr, phase):
   phases = map(str.lower, PhaseNames)
   idx = phases.index(phase)
   debug(">>> cmd_skip({}, {} ({}))", targets, phase, idx)
   for player in targets:
      skipPhases = getState(player, "skip")
      if not idx in skipPhases:
         skipPhases.append(idx)
         setState(player, "skip", skipPhases)
      notify("{} will skip his next {} phase.", player, phase.title())
   rc.applyNext()
   
   
def cmd_unite(rc, targets, source, restr, *args):
   debug(">>> cmd_unite({})", targets)
   if targets:
      uattack = getGlobalVar("UnitedAttack")
      if len(uattack) > 0:
         target = Card(uattack[0])
      else:
         target = targets[0]
      for card in targets:
         if card != target:
            remoteCall(getOpp(), "unitedAttackAuto", [card, [target], True])
            waitForAnimation()
      notify("{} has forced {} to do an United Attack", me, cardsAsNamesListStr(targets))
   rc.applyNext()
   
   
def cmd_removeFromAttack(rc, targets, source, restr, *args):
   debug(">>> cmd_removeFromAttack({})", targets)
   for card in targets:
      remoteCall(getOpp(), "cancelAttack", [card])
      waitForAnimation()
      notify("{} removes {} from attack.", me, card)
   rc.applyNext()


def cmd_modDamage(rc, targets, source, restr, qty):
   debug(">>> cmd_modDamage({})", qty)
   addTempVar("damageMod", int(qty), True)
   rc.applyNext()
   

def cmd_peek(rc, targets, source, restr):
   debug(">>> cmd_peek()")
   cardPeek(getOpp().hand)
   rc.applyNext()   


def cmd_pileView(rc, targets, source, restr, pileName, viewState):
   debug(">>> cmd_pileView({}, {})", pileName, viewState)
   prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, pileName)
   if name in RS_KW_ZONES_PILES:
      pile = RulesUtils.getPileByName(pileName)
      if pile.controller == me:
         pile.viewState = viewState
      else:
         # This is diabolic
         remoteCall(getOpp(), "exec", ["me.piles['{}'].viewState = '{}'".format(pile.name, viewState)])
   rc.applyNext()


def cmd_clear(rc, targets, source, restr):
   debug(">>> cmd_clear()")
   pcard = getGameCard(source)
   pcard.setState("willHighlight", False)
   rc.applyNext()


def cmd_or(rc, targets, source, restr):
   debug(">>> cmd_or({})", rc.lastCmdSuccess)
   if rc.lastCmdSuccess:
      cmd = rc.cmds.pop(0)
      debug("Skip next cmd: {}", cmd)
   rc.applyNext()


def cmd_and(rc, targets, source, restr):
   debug(">>> cmd_and({})", rc.lastCmdSuccess)
   if not rc.lastCmdSuccess:
      # Clear commands queue
      rc.cmds = []
      debug("Stop execution")
   rc.applyNext()
   

RulesCommands.register("damage",           cmd_damage)
RulesCommands.register("loselife",         cmd_loseLife)
RulesCommands.register("swappiles",        cmd_swapPiles)
RulesCommands.register("shuffle",          cmd_shuffle)
RulesCommands.register("destroy",          cmd_destroy)
RulesCommands.register("reveal",           cmd_reveal)
RulesCommands.register("discard",          cmd_discard)
RulesCommands.register("rnddiscard",       cmd_randomDiscard)
RulesCommands.register("moveto",           cmd_moveTo)
RulesCommands.register("movepile",         cmd_movePile)
RulesCommands.register("bp",               cmd_bp)
RulesCommands.register("sp",               cmd_sp)
RulesCommands.register("hp",               cmd_hp)
RulesCommands.register("playextrachar",    cmd_playExtraChar)
RulesCommands.register("draw",             cmd_draw)
RulesCommands.register("steal",            cmd_steal)
RulesCommands.register("loseability",      cmd_loseAbility)
RulesCommands.register("copyability",      cmd_copyAbility)
RulesCommands.register("swapabilities",    cmd_swapAbilities)
RulesCommands.register("each",             cmd_each)
RulesCommands.register("transform",        cmd_transform)
RulesCommands.register("moverevealedto",   cmd_moveRevealedCardsTo)
RulesCommands.register("enablerule",       cmd_enableRule)
RulesCommands.register("disablerule",      cmd_disableRule)
RulesCommands.register("modrule",          cmd_enableRule)  # alias
RulesCommands.register("freeze",           cmd_freeze)
RulesCommands.register("unfreeze",         cmd_unfreeze)
RulesCommands.register("altercost",        cmd_alterCost)
RulesCommands.register("modcost",          cmd_modCost)
RulesCommands.register("swapchars",        cmd_swapChars)
RulesCommands.register("movetoslot",       cmd_moveToSlot)
RulesCommands.register("trash",            cmd_trash)
RulesCommands.register("prophecy",         cmd_prophecy)
RulesCommands.register("activate",         cmd_activate)
RulesCommands.register("turns",            cmd_turns)
RulesCommands.register("skip",             cmd_skip)
RulesCommands.register("unite",            cmd_unite)
RulesCommands.register("removefromattack", cmd_removeFromAttack)
RulesCommands.register("moddamage",        cmd_modDamage)
RulesCommands.register("peek",             cmd_peek)
RulesCommands.register("pileview",         cmd_pileView)
RulesCommands.register("clear",            cmd_clear)
RulesCommands.register("or",               cmd_or)
RulesCommands.register("and",              cmd_and)
