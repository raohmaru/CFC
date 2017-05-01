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


   def getTargets(self, target):
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
      cards = self.getCardsFromZone(zone)
      debug("-- Retrieved %s cards" % len(cards))
      
      # Filter targets
      for type in types:
         # If kw is 'player' then must choose between himself or enemy
         if type == RS_KW_TARGET_PLAYER:
            t = askChoice("Select a player:", RS_KW_PLAYERS)
            if t == 0:
               return False
            type = RS_KW_PLAYERS[t-1]
      
         targets = self.filterTargets(type, filters, zone, cards, targeted=True)
         
         if targets == False:
            return False
            
      # If zone is a Pile, ask for card
      if zone[1] in RS_KW_ZONES_PILES:
         card = askCard(targets, "Select a card from {}".format(zone[1]), "Select a card")
         if not card:
            return False
         debug("{} has selected from {} the card {}".format(me, zone, card))
         targets = [card]
      
      return targets
      
      
   def getObjFromPrefix(self, prefix):
   # Returns an object of the game from the given prefix
      if prefix == RS_PREFIX_MY:
         return me
      if prefix == RS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      
   
   def getCardsFromZone(self, zone):
   # Get all the cards from the given zone
      if isinstance(zone, basestring):         
         prefix  = ''
      else:
         prefix  = zone[0]
         zone    = zone[1]
      player  = self.getObjFromPrefix(prefix) or me
      cards = []
      
      if zone == RS_KW_ZONE_ARENA:
         rings = getGlobalVar('Ring', me)
         if len(players) > 1:
            rings += getGlobalVar('Ring', players[1])
         cards = [c for c in table
            if c._id in rings]
      
      elif zone == RS_KW_ZONE_RING:
         ring = getGlobalVar('Ring', player)
         cards = [c for c in table
            if c._id in ring]
      
      elif zone == RS_KW_ZONE_HAND:
         cards = [c for c in player.hand]
      
      elif zone == RS_KW_ZONE_DECK:
         cards = [c for c in player.Deck]
      
      elif zone == RS_KW_ZONE_DISCARD:
         cards = [c for c in player.piles['Discard Pile']]
      
      elif zone == RS_KW_ZONE_KILL:
         cards = [c for c in player.piles['Removed Pile']]
            
      return cards
      
      
   def filterTargets(self, type, filters, zone, cards, targeted=False):
      debug("-- filter targets by type '%s' in zone %s" % (type, zone))
      targets = None
      if type == RS_KW_TARGET_THIS:
         targets = [Card(self.card_id)]
      # If target is a player
      elif type in RS_KW_TARGET_IS_PLAYER:
         targets = self.filterPlayers(type, filters)
      else:
         # Filter cards with a target
         targets = self.filterCards(type, filters, zone, cards, targeted)
         
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
   
   
   def filterCards(self, type, filters, zone, cards, targeted=False):
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

      # Look for targeted cards
      if targeted:
         if zone[1] in RS_KW_TARGET_ZONES:
            cards_f1 = [c for c in cards_f1
               if c.targetedBy == me]
            if len(cards_f1) == 0:
               # Last chance to select a card
               cards_f1 = showCardDlg(cards, "Select a card from the {} to which apply the effect".format(zone[1]))
               if cards_f1 == None:
                  # warning(MSG_ERR_NO_CARD_TARGETED)
                  return False
            debug("-- %s cards targeted" % len(filters))
         else:
            targeted = False      
      
      # At this point there are not cards to which apply the effect, but the ability
      # is activated anyway
      if len(cards_f1) == 0:
         notify(MSG_ERR_NO_CARDS)
         return cards_f1
      
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
               # return False
         
      # Check if only 1 target has been selected
      if not multiple and targeted and len(cards_f1) > 1:
         warning(MSG_ERR_MULTIPLE_TARGET)
         return False
            
      if type != RS_KW_ALL:
         # Look for (super) type
         if type in RS_KW_CARD_TYPES:
            debug("-- checking if any card match type '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Type.lower() == type]
         # Look for subtype
         else:
            debug("-- checking if any card match subtype '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Subtype.lower() == type]
            
      # Apply filters
      cards_f1 = RulesFilters.applyFiltersTo(cards_f1, filters)
         
      if not multiple and len(cards_f1) == 0:
         warning(MSG_ERR_NO_FILTERED_CARDS)
         return False
      
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
         if not self.payCost(*action['cost']):
            notify(MSG_COST_NOT_PAYED.format(me))
            return False
            
      # Finally apply the effects
      card = Card(self.card_id)
      for i, effect in enumerate(action['effects']):
         if len(effect[1]) > 0:
            debug("-- Applying commands")
            RulesCommands.applyAll(effect[1], targets[i], effect[3], card, inverse)
            for obj in targets[i]:
               if isCard(obj):
                  obj.target(False)
            
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
               
   
   def payCost(self, type, target=None):
      debug("-- Cost to pay: {}, {}".format(type, target))
      
      if type == RS_KW_COST_FREEZE:
         freeze(Card(self.card_id), silent = True)
         
      elif type == RS_KW_COST_SACRIFICE:
         return True
         
      elif type == RS_KW_COST_DISCARD:
         cards = []
         if len(me.hand) == 0:
            warning(MSG_ERR_NO_CARDS_HAND)
            return False
         # Target can be a number of cards to discard or null...
         if not target or is_number(target['types']):
            max = 1
            if target:
               max = int(target['types'])
            cards = self.getCardsFromZone(RS_KW_ZONE_HAND)
            cards = showCardDlg(cards, "Select {} card{} from you hand to discard".format(max, getPlural(max)), max)
            if cards == None:
               return False
         # ... or a valid target
         else:
            # The only zone allowed is player's hand
            target['zone'] = ['', RS_KW_ZONE_HAND]
            cards = self.getTargets(target)
            if cards == False or len(cards) == 0:
               warning(MSG_ERR_NO_CARDS_HAND)
               return False         
         for card in cards:
            discard(card)
         
      elif type == RS_KW_COST_EXILE:
         return True
         
      return True
