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
# RuleScript 0.0.1
#---------------------------------------------------------------------------

class Rules():
   """ Rule scripts parser """
   rule_id = ''
   card_id = ''
   parsed  = False
   target  = None

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
      rules = rules.strip().split('\n')

      for line in rules:
         line = line.strip().lower()
         debug("Parsing line '%s'" % line)

         # Skip comment lines
         if line[0] == AS_COMMENT_CHAR:
            debug("Leading comment char found. Line skipped")
            continue

         # Remove comments at the end of the line
         line = line.split(AS_COMMENT_CHAR)[0].rstrip()

         # Check for target command
         if self.target == None:
            target = AS_RGX_CMD_TARGET.match(line)
            if target:
               self.target = self.parseTarget( line[len(target.group()):] )
         else:
            debug("Target already defined. Line skipped")


   def parseTarget(self, str):
      str    = str.strip()
      debug("Parsing target '%s'" % str)

      # Get the types
      types = AS_RGX_TARGET_TYPE.split(str)
      if not types[0]:
         debug("ParseError: 'target' has no type parameter")
         return False
      types = types[0].split(AS_OP_OR)
      # AS_KW_ALL overrides the rest
      if AS_KW_ALL in types:
         types = [AS_KW_ALL]
      else:
         types = map(String.strip, types)
      debug("--- types: %s" % types)

      # Get the filters
      filters = AS_RGX_TARGET_RESTR.search(str)
      filters_arr = []
      if filters:
         filters = filters.group(1).split(AS_OP_OR)
         # Check filters
         for filter in filters:
            # AND filters
            filter = filter.split(AS_OP_AND)
            arr = []
            for f in filter:
               arr.append(self.getFilter(f))
            debug("--- filter: %s" % arr)
            if len(arr) > 0:
               filters_arr.append(arr if len(arr) > 1 else arr[0])

      # Get the zone
      zone = AS_RGX_TARGET_ZONE.search(str)
      zone_prefix = ''
      if zone:
         zone = zone.group(1)
      else:
         zone = AS_KW_ZONE_ARENA
      # Check for zone prefixes
      if zone != AS_KW_ZONE_ARENA:
         zone_prefix, zone = self.getPrefix(AS_PREFIX_ZONES, zone)
      # Check valid zones
      if zone not in AS_KW_ZONES:
         debug("KeywordError: Invalid zone '%s'. Assuming '%s'" % (zone, AS_KW_ZONE_ARENA))
         zone = AS_KW_ZONE_ARENA
      debug("--- zone prefix: %s" % zone_prefix)
      debug("--- zone: %s" % zone)
      
      return {
         'types'  : types,
         'filters': filters_arr,
         'zone'   : [zone_prefix, zone]
      }


   def activate(self):
      if not self.parsed:
         self.parse()
   
      debug("Executing rules")
      if self.target:
         target = self.getTargets(self.target)
         if not target:
            debug("Targeting canceled")
            return False
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
            debug("--- type selected: %s" % types)
      
      # Get the zone object
      debug("--- Getting card from zone %s" % ''.join(zone))
      cards = self.getZoneCards(zone)
      debug("--- Retrieved %s cards" % len(cards))
      
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
      
   
   def getFilter(self, str):
   # Returns a filter as an array
      str  = str.strip()
      args = ''
      
      # Look for prefixes
      prfx, cmd = self.getPrefix(AS_PREFIX_FILTERS, str)
      
      # Look for parameters
      params = AS_RGX_TARGET_PARAM.match(cmd)
      if params:
         cmd = params.group(1)
         args = params.group(2, 3)
      
      return [prfx, cmd, args]
      
   
   def getPrefix(self, prefixes, str):
   # Get the prefix for a given string
      for p in prefixes:
         if str[:len(p)] == p:
            cmd = str[len(p):].strip()
            return (p, cmd)
      return ('', str)
      
      
   def getSuffix(self, suffixes, str):
   # Get the suffix for a given string
      for p in suffixes:
         if str[-len(p):] == p:
            cmd = str[:-len(p)].strip()
            return (p, cmd)
      return ('', str)
      
      
   def getObjFromPrefix(self, prefix):
   # Returns an object of the game from the given prefix
      if prefix == AS_PREFIX_MY:
         return me
      if prefix == AS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      
   
   def getZoneCards(self, zone):
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
         cards = [c for c in player.piles['Kill Pile']]
            
      return cards
      
      
   def filterTargets(self, type, filters, zone, cards, targeted=False):
      debug("--- filter targets by type '%s' in zone %s" % (type, zone))
      if type == AS_KW_TARGET_THIS:
         targets = [Card(self.card_id)]
      # If target is a player
      elif type in AS_KW_TARGET_IS_PLAYER:
         targets = self.filterPlayers(type, filters)
      else:
         # Filter cards with a target
         targets = self.filterCards(type, filters, zone, cards, targeted)
         
      if isinstance(targets, list):
         debug("--- %s targets retrieved" % len(targets))
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
            
      debug("--- applying {} filters to player {}".format(len(filters), arr))
            
      # Apply filters      
      arr = self.applyFiltersTo(arr, filters)
         
      if len(arr) == 0:
         return GameException(ERR_NO_FILTERED_PLAYERS)
      
      return arr
   
   
   def filterCards(self, type, filters, zone, cards, targeted=False):
      debug("--- applying %s filters to %s cards" % (len(filters), len(cards)))
      
      cards_f1 = cards
      multiple = False

      # Look for targeted cards
      if targeted:
         if zone[1] in AS_KW_TARGET_ZONES:
            cards_f1 = [c for c in cards_f1
               if c.targetedBy == me]
            if len(cards_f1) == 0:
               return GameException(ERR_NO_CARD_TARGETED)
            debug("--- %s cards targeted" % len(filters))
         else:
            targeted = False
      
      # Check for type prefixes
      typePrefix, type = self.getPrefix(AS_PREFIX_TYPES, type)
      if typePrefix:
         debug("--- found prefix '%s' in '%s'" % (typePrefix, typePrefix+type))
         # Targetting other cards?
         if typePrefix == AS_PREFIX_OTHER:
            # Current card can't be selected
            if Card(self.card_id) in cards_f1:
               return GameException(ERR_TARGET_OTHER)
            
      # Check for type suffixes
      typeSuffix, type = self.getSuffix(AS_SUFFIX_TYPES, type)
      if typeSuffix:
         debug("--- found suffix '%s' in '%s'" % (typeSuffix, type+typeSuffix))
         # Allow multiple selection?
         if typeSuffix == AS_SUFFIX_PLURAL:
            multiple = True        
         
      # Check if only 1 target has been selected
      if not multiple and targeted and len(cards_f1) > 1:
         return GameException(ERR_MULTIPLE_TARGET)
            
      if type != AS_KW_ALL:
         # Look for (super) type
         if type in AS_KW_CARD_TYPES:
            debug("--- checking if any card match type '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Type.lower() == type]
         # Look for subtype
         else:
            debug("--- checking if any card match subtype '%s'" % type)
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
   
      debug("--- applying filter %s to %s objects" % (filter, len(arr)))
      arr = [c for c in arr
         if func(c, include, cmd, *filter[2])
      ]      
      debug("--- %s objects match the filter" % len(arr))
         
      return arr


class GameException(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)