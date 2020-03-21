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
# RuleScript
#---------------------------------------------------------------------------

class Rules():
   """ A class to parse, hold and execute the rules of a card """

   def __init__(self, rule, cid):
      self.rule_id = rule.lower()
      self.card_id = cid
      self.rules_tokens = None
      self.parsed = False
      self.has_events = False


   def parse(self):
      """ Parses the rules if they exists in RulesDict """
      # Get the rules
      if self.rule_id in RulesDict:
         rules = RulesDict[self.rule_id]
      else:
         return
      debug("Parsing rule id {}".format(self.rule_id))
      self.rules_tokens = RulesLexer.tokenize(rules)
      self.parsed = True

         
   def init(self):
      if not self.parsed:
         self.parse()
   
      if not self.rules_tokens:
         return
      
      # Add any abilities to the game, to trigger when needed
      if RS_KEY_ABILITIES in self.rules_tokens:
         RulesAbilities.addAll(self.rules_tokens[RS_KEY_ABILITIES], self.card_id)
      
      # Register events for the 'auto' key
      if RS_KEY_AUTO in self.rules_tokens:
         auto = self.rules_tokens[RS_KEY_AUTO]
         if auto['event']:
            for event in auto['event']:
               self.addEvent(event)
         else:
            self.addEventsFromIfCond()
         # If it does not have events, then it has commands that must be executed
         if not self.has_events:
            self.execAction(auto, [Card(self.card_id)], True)
         
         
   def addEvent(self, event):
      eventName = event[0] + event[1]
      addGameEventListener(eventName, self.card_id, self.card_id)
      if event[1] in GameEventsExecOnAdded:
         self.execAuto(self.rules_tokens[RS_KEY_AUTO], eventName)
      self.has_events = True
         
         
   def addEventsFromIfCond(self):
      """ If an if conditions is found, adds events according to the variables that are used """
      auto = self.rules_tokens[RS_KEY_AUTO]
      for effect in auto['effects']:         
         # Conditions
         if effect[0]:
            cond = effect[0]
            if cond[0] == RS_KW_COND_IF:
               leftCond = Regexps['LeftCond'].match(cond[1])
               if leftCond:
                  event = RulesLexer.getPrefix(RS_PREFIX_EVENTS, leftCond.group())
                  if event[1] in GameEventsFromVars:
                     self.addEvent((event[0], GameEventsFromVars[event[1]]))
   
      
   def activate(self):
      # Just in case
      if not self.parsed:
         self.init()
         
      if not self.rules_tokens:
         whisper("{}'s ability has not been scripted yet. You need to apply manually its effects.".format(Card(self.card_id)))
         return True
   
      debug("Executing rules")
      target = None
      if RS_KEY_TARGET in self.rules_tokens:
         targetList = self.rules_tokens[RS_KEY_TARGET]
         target = RulesUtils.getTargets(targetList, source=Card(self.card_id))
         if target == False and not targetList['opt']:
            debug("Targeting cancelled")
            return False
      
      if RS_KEY_ACTION in self.rules_tokens:
         req = self.rules_tokens[RS_KEY_REQ] if RS_KEY_REQ in self.rules_tokens else None
         return self.execAction(self.rules_tokens[RS_KEY_ACTION], target, requisite=req)
      
      return True

      
   def execAction(self, action, target, isAuto=False, requisite=None):
      debug("Executing actions: {}, {}, isAuto={}".format(action, target, isAuto))
      
      if isinstance(action, list):
         debug("Several actions found, player must choose one")
         actionLabels = []
         for a in action:
            label = a['effects'][0][1][0][0]
            if label in CMD_LABELS:
               label = CMD_LABELS[label]
            actionLabels.append(label)
         t = askChoice("Select an effect", actionLabels)
         if t == 0:
            return False
         debug("Action chosen: {}".format(action[t-1]))
         action = action[t-1]
            
      thisCard = Card(self.card_id)
      
      global commander
      if commander is None:
         commander = RulesCommands()
            
      # Check if there is any requisite
      if requisite:
         debug("Checking requisites: {}".format(requisite))
         for req in requisite:
            target = RulesLexer.parseTarget(req)
            if not RulesUtils.getTargets(target):
               notify(MSG_AB_MISS_REQ.format(thisCard))
               return False
            debug("-- Requisites are met")
            
      # The player must pay the cost, or we cancel
      if action['cost']:
         if not self.payCost(action['cost']):
            notify(MSG_COST_NOT_PAYED.format(me, thisCard, ('effect', 'ability')[isCharacter(thisCard)]))
            return False
            
      # Apply the effects
      for i, effect in enumerate(action['effects']):
         revert = False
      
         if len(effect[1]) > 0:
            debug("Executing effect: {}".format(effect))
            targets = []
            currTarget = target
            newTarget = None
            
            # Conditions
            if effect[0]:
               cond = effect[0]
               if cond[0] == RS_KW_COND_MAY:
                  question = MSG_MAY_DEF
                  if len(cond) > 1:
                     question = cond[1].strip('"\'').capitalize()
                  debug("-- Found MAY condition: {}".format(question))
                  if not confirm(question):
                     debug("--- {} cancelled".format(me))
                     return False
               elif cond[0] == RS_KW_COND_IF:            
                  debug("-- Found IF condition: {}".format(cond[1]))
                  res = evalExpression(cond[1], False, getLocals())
                  if not res:
                     debug("-- Condition not matching")
                     notify("Cannot activate the ability because its condition does not match.")
                     if not isAuto:
                        return ERR_NO_EFFECT
                     revert = True
            
            # Additional target
            if effect[2]:
               debug("-- Found additional {}target".format('optional' if effect[2]['opt'] else ''))
               newTarget = RulesUtils.getTargets(effect[2], source=thisCard)
               if newTarget == False and not effect[2]['opt']:
                  if not isAuto:
                     notify(MSG_ERR_NO_CARDS)
                  return False
               # Save original target
               if currTarget:
                  commander.prevTargets = currTarget
               currTarget = newTarget
            
            if currTarget:
               targets += currTarget
               
            # For auto with events that adds abilities, if the ability were already granted, check if any char has lost
            # it (it is not in in targets), then remove abilities of those chars
            if isAuto and action['event']:
               abTargets = getTargetofSourceEvent(self.card_id)
               newTargets = []
               for t in abTargets:
                  if not t in targets:
                     newTargets.append(t)
               if len(newTargets) > 0:
                  targets = newTargets
                  revert = True
                  debug("-- Following targets will lose an ability: {}".format(targets))
                  
            debug("-- Applying commands")
            commander.applyAll(effect[1], targets, effect[3], thisCard, revert)
            # Clear visual target
            if targets and not isAuto:
               for obj in targets:
                  if isCard(obj):
                     obj.target(False)
            rnd(10, 1000) # Wait between effects until all animation is done
      
      # Reset action local variables
      clearGlobalVar('ActionTempVars')
      
      # if not targets:
         # notify(MSG_AB_NO_EFFECT.format(thisCard, getParsedCard(thisCard).ability))
         
      if isAuto and not revert:
         notify(MSG_AB_AUTO_ACTIVATION.format(thisCard.controller, thisCard, getParsedCard(thisCard).ability))
      
      return True

      
   def execAuto(self, auto=None, eventName=None, *args):
      if not auto:
         if not self.rules_tokens[RS_KEY_AUTO]:
            return
         auto = self.rules_tokens[RS_KEY_AUTO]
      
      debug("Executing auto on event {} ({})".format(eventName, args))
      
      if eventName:
         thisCard = Card(self.card_id)
         if getMarker(thisCard, 'BP') > 0:
            notify("Event \"{}\" triggered. Now trying to activate {}'s auto ability from {}'s ring.".format(eventName, thisCard, thisCard.controller))
            if not MarkersDict['United Attack'] in thisCard.markers:
               target = [thisCard]
               if RS_KEY_TARGET in self.rules_tokens:
                  targetList = self.rules_tokens[RS_KEY_TARGET]
                  target = RulesUtils.getTargets(targetList, thisCard)
               self.execAction(auto, target, True)
            else:
               notify(MSG_AB_AUTO_UATTACK.format(thisCard, thisCard.Ability))
               
   
   def payCost(self, costs):
      thisCard = Card(self.card_id)
      for cost in costs:
         target = None
         if isinstance(cost, basestring):
            type = cost
         else:
            type, target = cost
         debug("-- Cost to pay: {}, {}".format(type, target))
         if type == RS_KW_COST_FREEZE:
            freeze(thisCard, silent = True)
            
         elif type == RS_KW_COST_DISCARD:
            cards = []
            isRandom = False
            if len(me.hand) == 0:
               warning(MSG_ERR_NO_CARDS_HAND)
               return False
            # Target can be a number of cards to discard or null...
            if not target or isNumber(target['types'][0]):
               max = 1
               if target:
                  max = int(target['types'][0])
               cards = RulesUtils.getCardsFromZone(RS_KW_ZONE_HAND)
               cards = showCardDlg(cards, "Select {} card{} from you hand to discard".format(max, plural(max)), max, min=max)
               if cards == None:
                  return False
            # ... or a valid target
            else:
               # The only zone allowed is player's hand
               target['zone'] = ['', RS_KW_ZONE_HAND]
               cards = RulesUtils.getTargets(target, thisCard, MSG_SEL_CARD_DISCARD)
               if cards == False or len(cards) == 0:
                  whisper(MSG_ERR_NO_CARDS_HAND)
                  return False
               # It's a random discard
               if target['qty'] is not None and target['qty'][:1] == 'r':
                  isRandom = True
            for card in cards:
               discard(card, isRandom = isRandom)
            # Add discarded cards to action local variables
            addActionTempVars('discarded', cards)
            
         elif type == RS_KW_COST_SACRIFICE:
            if target:
               # The only zone allowed is player's ring
               target['zone'] = ['', RS_KW_ZONE_RING]
               cards = RulesUtils.getTargets(target, thisCard, MSG_SEL_CARD_SACRIFICE)
               if cards == False or len(cards) == 0:
                  return False
               for card in cards:
                  destroy(card)
               addActionTempVars('sacrificed', cards)
            else:
               destroy(thisCard)
               addActionTempVars('sacrificed', [thisCard])
            
         # elif type == RS_KW_COST_EXILE:
         
      return True
