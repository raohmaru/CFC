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
   rule_id      = ''
   card_id      = ''
   rules_tokens = None
   prevTargets  = None

   def __init__(self, rule, cid):
      self.rule_id = rule.lower()
      self.card_id = cid
      self.parse()


   def parse(self):
      """ Parses the rules if they exists in RulesDict """
      # Get the rules
      if self.rule_id in RulesDict:
         rules = RulesDict[self.rule_id]
      else:
         return
      debug("Parsing rule id {}".format(self.rule_id))
      self.rules_tokens = RulesLexer.tokenize(rules)

         
   def init(self):
      if not self.rules_tokens:
         return
      
      # Add any abilities to the game, to trigger when needed
      if RS_KEY_ABILITIES in self.rules_tokens:
         RulesAbilities.addAll(self.rules_tokens[RS_KEY_ABILITIES], self.card_id)
      
      # Register an event for the 'auto' key
      if RS_KEY_AUTO in self.rules_tokens:
         auto = self.rules_tokens[RS_KEY_AUTO]
         if auto['event']:
            for event in auto['event']:
               self.addEvent(event)
         self.addEventsFromIfCond()
         
         
   def addEvent(self, event):
      eventName = event[0] + event[1]
      addGameEventListener(eventName, self.card_id, self.card_id)
      if event[1] in GameEventsExecOnAdded:
         self.execAuto(self.rules_tokens[RS_KEY_AUTO], eventName)
         
         
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
      if not self.rules_tokens:
         whisper("The ability of {} has not been scripted yet".format(Card(self.card_id)))
         return True
   
      debug("Executing rules")
      target = None
      if RS_KEY_TARGET in self.rules_tokens:
         target = RulesUtils.getTargets(self.rules_tokens[RS_KEY_TARGET], source=Card(self.card_id))
         if target == False:
            debug("Targeting cancelled")
            return False
      
      if RS_KEY_ACTION in self.rules_tokens:
         return self.execAction(self.rules_tokens[RS_KEY_ACTION], target)
      
      return True

      
   def execAction(self, action, target, isAuto=False):
      debug("Executing actions: {}, {}, isAuto={}".format(action, target, isAuto))
            
      thisCard = Card(self.card_id)
      inverse = False
      # First we get valid targets or we cancel
      targets = []
      for effect in action['effects']:
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
               res = evalExpression(cond[1])
               if not res:
                  debug("-- Condition not matching")
                  if not isAuto:
                     return False
                  inverse = True
         
         # Additional target
         if effect[2]:
            debug("-- Found additional target")
            newTarget = RulesUtils.getTargets(effect[2], source=thisCard)
            if newTarget == False:
               if not isAuto:
                  whisper(MSG_ERR_NO_CARDS)
               return False
            currTarget = newTarget
         targets.append(currTarget)
            
      # Then the player must pay the cost, or we cancel
      if action['cost']:
         if not self.payCost(action['cost']):
            notify(MSG_COST_NOT_PAYED.format(me))
            return False
            
      # For auto with events that adds abilities, if no matching then remove abilities
      if isAuto and action['event']:
         if not [t for t in targets if bool(t)] and self.prevTargets:
            targets = self.prevTargets
            self.prevTargets = None
            inverse = True
         else:
            self.prevTargets = targets
            
      # Finally apply the effects
      for i, effect in enumerate(action['effects']):
         if len(effect[1]) > 0:
            debug("-- Applying commands")
            RulesCommands.applyAll(effect[1], targets[i], effect[3], thisCard, inverse)
            # Clear visual target
            if targets[i] and not isAuto:
               for obj in targets[i]:
                  if isCard(obj):
                     obj.target(False)
            rnd(1, 100) # Wait between effects until all animation is done
            
      if not targets:
         notify(MSG_AB_NO_EFFECT.format(thisCard, getParsedCard(thisCard).ability))
         
      if isAuto and not inverse:
         notify(MSG_AB_AUTO_ACTIVATION.format(thisCard, getParsedCard(thisCard).ability))
      
      return True

      
   def execAuto(self, auto=None, eventName=None, *args):
      if not auto:
         if not self.rules_tokens[RS_KEY_AUTO]:
            return
         auto = self.rules_tokens[RS_KEY_AUTO] 
      debug("Executing auto on event {} ({})".format(eventName, args))
      
      if eventName:
         thisCard = Card(self.card_id)
         self.execAction(auto, [thisCard], True)
               
   
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
            if len(me.hand) == 0:
               warning(MSG_ERR_NO_CARDS_HAND)
               return False
            # Target can be a number of cards to discard or null...
            if not target or isNumber(target['types'][0]):
               max = 1
               if target:
                  max = int(target['types'][0])
               cards = RulesUtils.getCardsFromZone(RS_KW_ZONE_HAND)
               cards = showCardDlg(cards, "Select {} card{} from you hand to discard".format(max, getPlural(max)), max, min=max)
               if cards == None:
                  return False
            # ... or a valid target
            else:
               # The only zone allowed is player's hand
               target['zone'] = ['', RS_KW_ZONE_HAND]
               cards = RulesUtils.getTargets(target, MSG_SEL_CARD_DISCARD, source=thisCard)
               if cards == False or len(cards) == 0:
                  whisper(MSG_ERR_NO_CARDS_HAND)
                  return False
            for card in cards:
               discard(card)
            
         elif type == RS_KW_COST_SACRIFICE:
            if target:
               # The only zone allowed is player's ring
               target['zone'] = ['', RS_KW_ZONE_RING]
               cards = RulesUtils.getTargets(target, MSG_SEL_CARD_SACRIFICE, source=thisCard)
               if cards == False or len(cards) == 0:
                  return False
               for card in cards:
                  destroy(card)
            else:
               destroy(thisCard)
            
         # elif type == RS_KW_COST_EXILE:
         
      return True
