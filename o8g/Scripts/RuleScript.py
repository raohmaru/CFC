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
# RuleScript 0.0.2
#---------------------------------------------------------------------------

class Rules():
   rule_id     = ''
   card_id     = ''
   parsed      = False
   rules_dict  = None

   def __init__(self, rule, cid):
      self.rule_id = rule
      self.card_id = cid


   def parse(self):
      if self.parsed:
         return      
      self.parsed = True
      
      # Get the rules
      rules = RulesDict[self.rule_id.lower()]
      if not rules:
         return
      self.rules_dict = RulesLexer.parse(rules)
      

   def activate(self):
      if not self.parsed:
         self.parse()
   
      debug("Executing rules")
      target = None
      if 'target' in self.rules_dict:
         target = self.getTargets(self.rules_dict['target'])
         if not target:
            debug("Targeting canceled")
            return False
      
      if 'action' in self.rules_dict:
         self.execAbilities(self.rules_dict['action'], target)
      
      return True


   def getTargets(self, target):
      debug("Checking targets")

      types       = target['types']
      zone        = target['zone']
      filters     = target['filters']
      
      # If two or more targets, ask for a single target
      if len(types) > 1:
         # Check if there is any keyword in the target types
         kw_types = set(AS_KW_TARGETS) & set(types)
         if len(kw_types) > 0:
            t = askChoice("Select a target:", types)
            if t == 0:
               return False
            types = [types[t-1]]
            debug("-- type selected: %s" % types)
      
      # Get the zone object
      debug("-- Getting card from zone %s" % ''.join(zone))
      cards = self.getCardsFromZone(zone)
      debug("-- Retrieved %s cards" % len(cards))
      
      if len(cards) == 0:
         warning(ErrStrings[ERR_NO_CARDS])
         return False
      
      # Filter targets
      for type in types:
         # If kw is 'player' then must choose between himself or enemy
         if type == AS_KW_TARGET_PLAYER:
            t = askChoice("Select a player:", AS_KW_PLAYERS)
            if t == 0:
               return False
            type = AS_KW_PLAYERS[t-1]
      
         targets = self.filterTargets(type, filters, zone, cards, targeted=True)
         
         if targets:
            # If an error was returned
            if isinstance(targets, GameException):
               warning(ErrStrings[targets.value])
               return False
            break
            
      # If zone is a Pile, ask for card
      if zone[1] in AS_KW_ZONES_PILES:
         card = askCard(targets, "Select a card from {}".format(zone[1]), "Select a card")
         if not card:
            return False
         debug("{} has selected from {} the card {}".format(me, zone, card))
         targets = [card]
      
      return targets
      
      
   def getObjFromPrefix(self, prefix):
   # Returns an object of the game from the given prefix
      if prefix == AS_PREFIX_MY:
         return me
      if prefix == AS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      
   
   def getCardsFromZone(self, zone):
   # Get all the cards from the given zone
      prefix  = zone[0]
      zone    = zone[1]
      player  = self.getObjFromPrefix(prefix) or me
      cards = []
      
      if zone == AS_KW_ZONE_ARENA:
         cards = [c for c in table]
      
      elif zone == AS_KW_ZONE_RING:
         cards = [c for c in table
            if c.controller == player]
      
      elif zone == AS_KW_ZONE_HAND:
         cards = [c for c in player.hand]
      
      elif zone == AS_KW_ZONE_DECK:
         cards = [c for c in player.Deck]
      
      elif zone == AS_KW_ZONE_DISCARD:
         cards = [c for c in player.piles['Discard Pile']]
      
      elif zone == AS_KW_ZONE_KILL:
         cards = [c for c in player.piles['Removed Pile']]
            
      return cards
      
      
   def filterTargets(self, type, filters, zone, cards, targeted=False):
      debug("-- filter targets by type '%s' in zone %s" % (type, zone))
      if type == AS_KW_TARGET_THIS:
         targets = [Card(self.card_id)]
      # If target is a player
      elif type in AS_KW_TARGET_IS_PLAYER:
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
         if type == AS_KW_TARGET_ME:
            arr = [me]
         elif type == AS_KW_TARGET_OPP:
            arr = [players[1]] if len(players) > 1 else [me]
         elif type == AS_KW_TARGET_PLAYERS:
            arr = [me]
            if len(players) > 1:
               arr.append(players[1])
            
      debug("-- applying {} filters to player {}".format(len(filters), arr))
            
      # Apply filters      
      arr = self.applyFiltersTo(arr, filters)
         
      if len(arr) == 0:
         return GameException(ERR_NO_FILTERED_PLAYERS)
      
      return arr
   
   
   def filterCards(self, type, filters, zone, cards, targeted=False):
      debug("-- applying %s filters to %s cards" % (len(filters), len(cards)))
      
      cards_f1 = cards
      multiple = False

      # Look for targeted cards
      if targeted:
         if zone[1] in AS_KW_TARGET_ZONES:
            cards_f1 = [c for c in cards_f1
               if c.targetedBy == me]
            if len(cards_f1) == 0:
               return GameException(ERR_NO_CARD_TARGETED)
            debug("-- %s cards targeted" % len(filters))
         else:
            targeted = False
      
      # Check for type prefixes
      typePrefix, type = RulesLexer.getPrefix(AS_PREFIX_TYPES, type)
      if typePrefix:
         debug("-- found prefix '%s' in '%s'" % (typePrefix, typePrefix+type))
         # Targetting other cards?
         if typePrefix == AS_PREFIX_OTHER:
            # Current card can't be selected
            if Card(self.card_id) in cards_f1:
               return GameException(ERR_TARGET_OTHER)
            
      # Check for type suffixes
      typeSuffix, type = RulesLexer.getSuffix(AS_SUFFIX_TYPES, type)
      if typeSuffix:
         debug("-- found suffix '%s' in '%s'" % (typeSuffix, type+typeSuffix))
         # Allow multiple selection?
         if typeSuffix == AS_SUFFIX_PLURAL:
            multiple = True        
         
      # Check if only 1 target has been selected
      if not multiple and targeted and len(cards_f1) > 1:
         return GameException(ERR_MULTIPLE_TARGET)
            
      if type != AS_KW_ALL:
         # Look for (super) type
         if type in AS_KW_CARD_TYPES:
            debug("-- checking if any card match type '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Type.lower() == type]
         # Look for subtype
         else:
            debug("-- checking if any card match subtype '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Subtype.lower() == type]
      
      if len(cards_f1) == 0:
         return GameException(ERR_NO_FILTERED_CARDS)
            
      # Apply filters
      cards_f1 = self.applyFiltersTo(cards_f1, filters)
         
      if len(cards_f1) == 0:
         return GameException(ERR_NO_FILTERED_CARDS)
      
      return cards_f1
      
    
   def applyFiltersTo(self, arr, filters):
      if len(filters) > 0:
         for filter in filters:
            # filter could be a list of chained filters
            if isinstance(filter[0], list):
               arr2 = arr
               for f in filter:
                  arr2 = self.applyFilter(f, arr2)
            else:
               arr2 = self.applyFilter(filter, arr)
            # Break on any match
            if len(arr2) > 0:
               break
         arr = arr2
      
      return arr
   
   
   def applyFilter(self, filter, arr):
      # filter = [prfx, cmd, [args]]
      include = filter[0] != AS_PREFIX_NOT
      cmd = filter[1]
      
      # Get the filter function
      if   cmd in RulesFilters    : func = RulesFilters[cmd]
      elif cmd in AS_KW_CARD_TYPES: func = filterType
      else                        : func = filterSubtype
   
      debug("-- applying filter %s to %s objects" % (filter, len(arr)))
      arr = [c for c in arr
         if func(c, include, cmd, *filter[2])
      ]      
      debug("-- %s objects match the filter" % len(arr))
         
      return arr

      
   def execAbilities(self, ability, target):
      return True
      # if ability['effects'][0] == AS_KW_COND_MAY:
         # if not confirm("May {}?".format(question)):
            # break
      
class GameException(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)