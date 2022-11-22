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
# RuleScript
#---------------------------------------------------------------------------

class Rules():
   """
   A class to parse, hold and execute the rules of a card.
   """

   def __init__(self, rule, card_id):
      self.rule_id = rule.lower()  # case insensitive
      self.card_id = card_id
      self.rules_tokens = None
      self.parsed = False
      self.has_events = False


   def parse(self):
      """
      Parses the rules if they exists in RulesDict.
      """
      # Get the rules
      if self.rule_id in RulesDict:
         rules = RulesDict[self.rule_id]
      else:
         return
      debug("Parsing rule id {}", self.rule_id)
      self.rules_tokens = RulesLexer.tokenize(rules)
      self.parsed = True

         
   def init(self, forceActivateAuto = False):
      if not self.parsed:
         self.parse()
   
      if not self.rules_tokens:
         return
      
      # Add abilities, they will trigger when needed
      if RS_KEY_ABILITIES in self.rules_tokens:
         RulesAbilities.addAll(self.rules_tokens[RS_KEY_ABILITIES], self.card_id)
      
      # Add events from the "auto" key
      if RS_KEY_AUTO in self.rules_tokens:
         auto = self.rules_tokens[RS_KEY_AUTO]
         if auto["event"]:
            for event in auto["event"]:
               self.addEvent(event)
         else:
            self.addEventsFromIfCond()
         # If it does not have events, or if it is allowed to execute on init,
         # then it means that it has commands that must be executed
         if not self.has_events or forceActivateAuto and self.canActivateAuto(auto["event"]):
            debug("Can execute auto on init")
            self.execAction(auto, [Card(self.card_id)], True)
         
         
   def addEvent(self, event):
      eventName = event[0] + event[1]
      appliesto = event[2] if len(event) > 2 else None
      addGameEventListener(eventName, self.card_id, self.card_id, appliesto = appliesto)
      self.has_events = True
         
         
   def addEventsFromIfCond(self):
      """
      If an if conditions is found, adds events according to the variables that are used.
      """
      auto = self.rules_tokens[RS_KEY_AUTO]
      for effect in auto["effects"]:         
         # Conditions
         if effect[0]:
            cond = effect[0]
            if cond[0] == RS_KW_COND_IF:
               leftCond = Regexps["leftcond"].match(cond[1])
               if leftCond:
                  event = RulesLexer.getPrefix(RS_PREFIX_EVENTS, leftCond.group())
                  if event[1] in GameEventsFromVars:
                     self.addEvent((event[0], GameEventsFromVars[event[1]]))
            
            
   def canActivateAuto(self, events):
      for event in events:
         if event[1] in GameEventsActivateOnCopy:
            return True
      return False
                     
                     
   def getTargets(self, targetList):
      targets = []
      for item in targetList:
         target = RulesUtils.getTargets(item, source = Card(self.card_id))
         if target == False and not item["opt"]:
            debug("Targeting cancelled")
            return False
         if target:
            targets += target
      return targets
      
      
   def activate(self):
      thisCard = Card(self.card_id)
      # Just in case
      if not self.parsed:
         self.init()
         
      if not self.rules_tokens:
         whisper("{}'s ability has not been scripted yet. You need to apply manually its effects.".format(thisCard))
         return True
   
      debug("Executing rules")
            
      # Check if there is any requisite
      if RS_KEY_REQ in self.rules_tokens:
         requisite = self.rules_tokens[RS_KEY_REQ]
         debug("Checking requisites: {}", requisite)
         for req in requisite:
            reqTarget = RulesLexer.parseTarget(req)
            if not RulesUtils.getTargets(reqTarget, thisCard, reveal = False):
               _extapi.whisper(MSG_AB_MISS_REQ.format(thisCard), Colors.Red)
               playSnd("cancel-2")
               return False
            debug("-- Requisites are met")
            
      targets = None
      if RS_KEY_TARGET in self.rules_tokens:
         targets = self.getTargets(self.rules_tokens[RS_KEY_TARGET])
         if targets == False:
            return False
      
      if RS_KEY_ACTION in self.rules_tokens:
         return self.execAction(self.rules_tokens[RS_KEY_ACTION], targets)
      
      return True

      
   def execAction(self, action, target, isAuto = False, isBranch = False):
      debug("Executing actions: {}, {}, isAuto={}", action, target, isAuto)
      thisCard = Card(self.card_id)
      
      if isinstance(action, list):
         debug("Several actions found, player must choose one")
         actionLabels = []
         cardLabels = self.rules_tokens[RS_KEY_LABEL] if RS_KEY_LABEL in self.rules_tokens else []
         for i, a in enumerate(action):
            # Gets the cmd name as fallback
            label = a["effects"][0][1][0][0]
            # Does the list have the index? (checks if the index is in the range of 0 and the lenght)
            if 0 <= i < len(cardLabels):
               label = cardLabels[i]
            elif label in CMD_LABELS:
               label = CMD_LABELS[label]
            actionLabels.append(label)
         t = askChoice("Select an effect", actionLabels)
         if t == 0:
            return False
         debug("Action chosen: {}", action[t-1])
         action = action[t-1]
         
      addTempVar("tgt", target)
      
      global commander
      if commander is None:
         commander = RulesCommands()
            
      if not isBranch:
         # Add temp variables
         if RS_KEY_VARS in self.rules_tokens:
            vars = self.rules_tokens[RS_KEY_VARS]
            debug("Adding custom vars: {}", vars)
            for var in vars:
               res = evalExpression(var[1], True, getLocals(source = thisCard))
               if res is not None:
                  debug("-- {} := {}", var[0], res)
                  addTempVar(var[0], res)
               
         # The player must pay the cost, or we cancel
         if action["cost"]:
            if not self.payCost(action["cost"]):
               notify(MSG_COST_NOT_PAYED.format(me, thisCard, ("effect", "ability")[isCharacter(thisCard)]))
               playSnd("cancel-2")
               return False
            
      # Apply the effects
      for i, effect in enumerate(action["effects"]):
         revert = False
      
         debug("Executing effect: {}", effect)
         addTempVar("effect", effect)
         targets = []
         currTarget = target
         newTarget = None
         
         # Conditions
         if effect[0]:
            cond = effect[0]
            # MAY condition
            if cond[0] == RS_KW_COND_MAY:
               question = MSG_Q_MAY
               if len(cond) > 1:
                  question = cond[1].capitalize()
               debug("-- Found MAY condition: \"{}\"", question)
               if not confirm(question):
                  debug("--- {} canceled", me)
                  return True
            # IF condition
            elif cond[0] == RS_KW_COND_IF:            
               debug("-- Found IF condition: {}", cond[1])
               res = evalExpression(cond[1], False, getLocals(source = thisCard))
               if not res:
                  debug("--- Condition not matching")
                  if len(cond) > 2:
                     debug("--- Found ELIF/ELSE condition")
                     return self.execAction(cond[2], target, isAuto, True)
                  # Only a failed condition in the first action can stop the execution
                  if i == 0 and len(effect[1]) > 0:
                     notify("Cannot activate the ability because its conditions do not match.")
                  if not isAuto and i == 0:
                     return ERR_NO_EFFECT
                  revert = True  # Remove abilities
               # If there aren't any command, then we return resulting boolean
               if len(effect[1]) == 0:
                  return res
         
         # Additional target
         if effect[2]:
            debug("-- Found additional {}target", "optional" if effect[2]["opt"] else "")
            newTarget = RulesUtils.getTargets(effect[2], source = thisCard)
            if newTarget == False and not effect[2]["opt"]:
               if not isAuto:
                  notify(MSG_ERR_NO_CARDS)
                  playSnd("cancel-2")
               return False
            # Save original target
            if currTarget:
               commander.prevTargets = currTarget
            currTarget = newTarget
         
         if currTarget:
            targets += currTarget
               
         # Run the commands
         if len(effect[1]) > 0:
            debug("-- Applying commands")
            commander.applyAll(effect[1], targets, effect[3], thisCard, revert)
            # Clear visual target
            if targets and not isAuto:
               for obj in targets:
                  if isCard(obj) and obj.targetedBy:
                     obj.target(False)
         waitForAnimation()
            
      if isAuto and not revert:
         if isCharacter(thisCard):
            notify(MSG_AB_AUTO_ACT_CHAR.format(thisCard.controller, thisCard, getGameCard(thisCard).ability))
         else:
            notify(MSG_AB_AUTO_ACT, thisCard.controller, thisCard)
      
      return True

      
   def execAuto(self, auto = None, eventName = None, *args):
      if not auto:
         if not self.rules_tokens[RS_KEY_AUTO]:
            return False
         auto = self.rules_tokens[RS_KEY_AUTO]
      
      debug("Executing auto on event {} ({})", eventName, args)
      
      if eventName:
         thisCard = Card(self.card_id)
         # Non-character cards can have autos with events (Crossover/Grandmaster rule)
         if not isCharacter(thisCard) or getMarker(thisCard, "BP") > 0:
            if isCharacter(thisCard):
               notify(MSG_AB_AUTO_TRIGGER_CHAR, eventName, thisCard, thisCard.controller, thisCard.group.name)
            else:
               notify(MSG_AB_AUTO_TRIGGER, eventName, thisCard, thisCard.controller)
            if not hasMarker(thisCard, "United Attack"):
               targets = [thisCard]
               if RS_KEY_TARGET in self.rules_tokens:
                  newTargets = self.getTargets(self.rules_tokens[RS_KEY_TARGET])
                  if newTargets:
                     targets = newTargets
               # last argument can be the id of the card that triggered the effect
               if len(args) > 0 and isNumber(args[-1]):
                  trigger = Card(args[-1])
                  if hasattr(trigger, "model"):  # It's an actual card
                     addTempVar("trigger", trigger)
               return self.execAction(auto, targets, True)
            else:
               notify(MSG_AB_AUTO_UATTACK, thisCard, thisCard.Ability)
      
      return True
               
   
   def payCost(self, costs):
      thisCard = Card(self.card_id)
      for cost in costs:
         target = None
         if isinstance(cost, basestring):
            type = cost
         else:
            type, target = cost
         debug("-- Cost to pay: {}, {}", type, target)
         
         if type == RS_KW_COST_FREEZE:
            freeze(thisCard, silent = True)
            
         elif type == RS_KW_COST_DISCARD:
            cards = []
            isRandom = False
            if len(me.hand) == 0:
               warning(MSG_ERR_NO_CARDS_HAND)
               return False
            # Target can be a number of cards to discard or null...
            if not target or isNumber(target["types"][0]):
               amount = 1
               if target:
                  amount = int(target["types"][0])
               # Looking exactly for `amount` targeted cards in the hand
               targetedCards = getTargetedCardsFrom(type = None, group = me.hand)
               if len(targetedCards) == amount:
                  cards = targetedCards
               # Should ask for cards?
               if len(cards) == 0:
                  cards = RulesUtils.getCardsFromZone(RS_KW_ZONE_HAND)
                  notify(MSG_PLAYER_LOOKS, me, "their", "hand")
                  cards = showCardDlg(cards, "Select {} card{} from you hand to discard".format(amount, pluralize(amount)), amount, min = amount)
               if cards == None:
                  return False
            # ... or a valid target
            else:
               # The only zone allowed is player's hand
               target["zone"] = ["", RS_KW_ZONE_HAND]
               cards = RulesUtils.getTargets(target, thisCard, MSG_SEL_CARD_DISCARD)
               if cards == False or len(cards) == 0:
                  whisper(MSG_ERR_NO_CARDS_HAND)
                  return False
               # It's a random discard
               if target["qty"] is not None and target["qty"][:1] == "r":
                  isRandom = True
            for card in cards:
               discard(card, isRandom = isRandom)
            # Add discarded cards to action local variables
            addTempVar("discarded", cards)
            
         elif type == RS_KW_COST_SACRIFICE:
            if target:
               # The only zone allowed is player's ring
               target["zone"] = ["", RS_KW_ZONE_RING]
               cards = RulesUtils.getTargets(target, thisCard, MSG_SEL_CARD_SACRIFICE)
               if cards == False or len(cards) == 0:
                  return False
               for card in cards:
                  destroy(card)
               addTempVar("sacrificed", cards)
            else:
               destroy(thisCard)
               addTempVar("sacrificed", [thisCard])
            
         # elif type == RS_KW_COST_EXILE:
         
      return True
