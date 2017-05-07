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

         
   def initAuto(self):
      if not self.rules_tokens:
         return
      
      # Add any abilities to the game, to trigger when needed
      if RS_KEY_ABILITIES in self.rules_tokens:
         RulesAbilities.addAll(self.rules_tokens[RS_KEY_ABILITIES], self.card_id)
      
      # Register an event for the 'auto' key
      if RS_KEY_AUTO in self.rules_tokens:
         auto = self.rules_tokens[RS_KEY_AUTO]
         event = auto['event'][0] + auto['event'][1]
         addGameEventListener(event, self.card_id, self.card_id)
         if auto['event'][1] in GameEventsExecOnAdded:
            self.execAuto(auto, event)
         
      
   def activate(self):
      if not self.rules_tokens:
         whisper("The ability of %s has not been scripted yet".format(Card(self.card_id)))
         return True
   
      debug("Executing rules")
      target = None
      if RS_KEY_TARGET in self.rules_tokens:
         target = self.getTargets(self.rules_tokens[RS_KEY_TARGET])
         if target == False:
            debug("Targeting cancelled")
            return False
      
      if RS_KEY_ACTION in self.rules_tokens:
         return self.execAction(self.rules_tokens[RS_KEY_ACTION], target)
      
      return True


   def getTargets(self, target, msg=None):
      debug("Checking targets")

      types       = target['types']
      zone        = target['zone']
      filters     = target['filters']
      
      # If two or more targets, ask for a single target
      if len(types) > 1:
         # Check if there is any keyword in the target types
         kw_types = set(RS_KW_TARGETS) & set(types)
         if len(kw_types) > 0:
            t = askChoice("Select a target:", types)
            if t == 0:
               return False
            types = [types[t-1]]
            debug("-- type selected: %s" % types)
      
      # Get all the cards from the given zone
      debug("-- Getting all cards from zone %s" % ''.join(zone))
      cards = RulesUtils.getCardsFromZone(zone)
      debug("-- Retrieved %s cards" % len(cards))
      
      # Filter targets
      for type in types:
         # If kw is 'player' then must choose between himself or enemy
         if type == RS_KW_TARGET_PLAYER:
            t = askChoice("Select a player:", RS_KW_PLAYERS)
            if t == 0:
               return False
            type = RS_KW_PLAYERS[t-1]      
         targets = self.filterTargets(type, filters, zone, cards, targeted=True, msg=msg)         
         if targets == False:
            return False
      
      return targets
      
      
   def filterTargets(self, type, filters, zone, cards, targeted=False, msg=None):
      debug("-- filter targets by type '%s' in zone %s" % (type, zone))
      targets = None
      if type == RS_KW_TARGET_THIS:
         targets = [Card(self.card_id)]
      # If target is a player
      elif type in RS_KW_TARGET_IS_PLAYER:
         targets = self.filterPlayers(type, filters)
      else:
         # Filter cards with a target
         targets = self.filterCards(type, filters, zone, cards, targeted, msg)
         
      if isinstance(targets, list):
         debug("-- %s targets retrieved" % len(targets))
         if len(targets) < 10:
            for t in targets:
               debug(" '- target: {}".format(t))
      return targets
      
      
   def filterPlayers(self, type, filters):
      if isinstance(type, basestring):
         if type == RS_KW_TARGET_ME:
            arr = [me]
         elif type == RS_KW_TARGET_OPP:
            arr = [players[1]] if len(players) > 1 else [me]
         elif type == RS_KW_TARGET_PLAYERS:
            arr = [me]
            if len(players) > 1:
               arr.append(players[1])
            
      debug("-- applying {} filters to player {}".format(len(filters), arr))
            
      # Apply filters      
      arr = RulesFilters.applyFiltersTo(arr, filters)
         
      if len(arr) == 0:
         warning(MSG_ERR_NO_FILTERED_PLAYERS)
         return False
      
      return arr
   
   
   def filterCards(self, type, filters, zone, cards, targeted=False, msg=None):
      debug("-- applying %s filters to %s cards" % (len(filters), len(cards)))
      
      cards_f1 = cards
      multiple = False
            
      # Check for type suffixes
      typeSuffix, type = RulesLexer.getSuffix(RS_SUFFIX_TYPES, type)
      if typeSuffix:
         debug("-- found suffix '%s' in '%s'" % (typeSuffix, type+typeSuffix))
         # Allow multiple selection?
         if typeSuffix == RS_SUFFIX_PLURAL:
            multiple = True
            targeted = False
      
      # Check for type prefixes
      typePrefix, type = RulesLexer.getPrefix(RS_PREFIX_TYPES, type)
      if typePrefix:
         debug("-- found prefix '%s' in '%s'" % (typePrefix, typePrefix+type))
         # Targeting other cards?
         if typePrefix == RS_PREFIX_OTHER:
            # Current card can't be selected
            card = Card(self.card_id)
            if card in cards_f1:
               whisper(MSG_ERR_TARGET_OTHER.format(card))
               cards_f1.remove(card)
               # return False
            
      if type != RS_KW_ALL:
         # Look for (super) type
         if type in RS_KW_CARD_TYPES:
            debug("-- checking if any card match type '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Type.lower() == type]
            debug(cards_f1)
         # Look for subtype
         else:
            debug("-- checking if any card match subtype '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Subtype.lower() == type]
            debug(cards_f1)

      # Look for targeted cards
      if targeted:
         if zone[1] in RS_KW_TARGET_ZONES:
            cards_f2 = [c for c in cards_f1
               if c.targetedBy == me]
            if len(cards_f2) == 0:
               # Last chance to select a card
               if not msg:
                  msg = MSG_SEL_CARD
               cards_f1 = showCardDlg(cards_f1, msg.format(zone[1]))
               if cards_f1 == None:
                  # warning(MSG_ERR_NO_CARD_TARGETED)
                  return False
            debug("-- %s cards targeted" % len(cards_f1))
         else:
            targeted = False
         
      # Check if only 1 target has been selected
      if not multiple and targeted and len(cards_f1) > 1:
         warning(MSG_ERR_MULTIPLE_TARGET)
         return False
            
      # Apply filters
      cards_f1 = RulesFilters.applyFiltersTo(cards_f1, filters)
         
      if not multiple:
         if len(cards_f1) == 0:
            warning(MSG_ERR_NO_FILTERED_CARDS)
            return False
         # Check if only 1 target has been selected
         if targeted and len(cards_f1) > 1:
            warning(MSG_ERR_MULTIPLE_TARGET)
            return False
      
      # At this point there are not cards to which apply the effect, but the ability
      # is activated anyway
      if len(cards_f1) == 0:
         notify(MSG_ERR_NO_CARDS)
      
      return cards_f1

      
   def execAction(self, action, target, inverse=False):
      debug("Executing actions")
            
      # First we get valid targets or we cancel
      targets = []
      for effect in action['effects']:
         currTarget = target
         newTarget = None
         
         # Conditions
         # if ability['effects'][0] == RS_KW_COND_MAY:
            # if not confirm("May {}?".format(question)):
               # break
         
         # Additional target
         if effect[2]:
            debug("-- Found additional target")
            newTarget = self.getTargets(effect[2])
            if newTarget == False:
               notify(MSG_ERR_NO_CARDS)
               return False
            currTarget = newTarget
         targets.append(currTarget)
            
      # Then the player must pay the cost, or we cancel
      if action['cost']:
         if not self.payCost(action['cost']):
            notify(MSG_COST_NOT_PAYED.format(me))
            return False
            
      # Finally apply the effects
      card = Card(self.card_id)
      for i, effect in enumerate(action['effects']):
         if len(effect[1]) > 0:
            debug("-- Applying commands")
            RulesCommands.applyAll(effect[1], targets[i], effect[3], card, inverse)
            if targets[i]:
               for obj in targets[i]:
                  if isCard(obj):
                     obj.target(False)
            rnd(1, 100) # Wait between effects until all animation is done
            
      return True

      
   def execAuto(self, auto=None, eventName=None, *args):
      if not auto:
         if not self.rules_tokens[RS_KEY_AUTO]:
            return
         auto = self.rules_tokens[RS_KEY_AUTO]
      debug("Executing auto on event {} ({})".format(eventName, args))
      
      if eventName:
         eventChecked = RulesEvents.check(eventName, auto['event'], *args)
         if eventChecked != None:
            self.execAction(auto, [Card(self.card_id)], not eventChecked)
               
   
   def payCost(self, costs):
      for cost in costs:
         target = None
         if isinstance(cost, basestring):
            type = cost
         else:
            type, target = cost
         debug("-- Cost to pay: {}, {}".format(type, target))
         if type == RS_KW_COST_FREEZE:
            freeze(Card(self.card_id), silent = True)
            
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
               cards = self.getTargets(target, MSG_SEL_CARD_DISCARD)
               if cards == False or len(cards) == 0:
                  whisper(MSG_ERR_NO_CARDS_HAND)
                  return False
            for card in cards:
               discard(card)
            
         elif type == RS_KW_COST_SACRIFICE:
            if target:
               # The only zone allowed is player's ring
               target['zone'] = ['', RS_KW_ZONE_RING]
               cards = self.getTargets(target, MSG_SEL_CARD_SACRIFICE)
               if cards == False or len(cards) == 0:
                  return False
               for card in cards:
                  destroy(card)
            else:
               destroy(Card(self.card_id))
            
         # elif type == RS_KW_COST_EXILE:
         
      return True
