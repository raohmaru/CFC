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
      self.parse()


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
         debug("\nParsing line '%s'" % line)

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
      debug("-- types: %s" % types)

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
               f = self.getFilter(f)
               # Check valid filter kw
               if f[1] not in AS_KW_FILTERS:
                  debug("KeywordError: Invalid filter '%s'" % f[1])
                  continue
               arr.append(f)
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
         'types' : types,
         'filters': filters_arr,
         'zone'  : [zone_prefix, zone]
      }


   def activate(self):
      debug("\nExecuting rules")
      if self.target:
         target = self.checkTargets(self.target)
         if not target:
            debug("Targeting canceled")
            return


   def checkTargets(self, target):
      debug("Checking targets")

      types  = target['types']
      zone   = target['zone']
      filters = target['filters']

      # Check target type
      # If two or more targets, maybe ask for a single target
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
      debug("--- Retrieved %s cards" % len(zone))
      
      # Filter targets
      for type in types:
         # If kw player then must choose between himself or enemy
         if type == AS_KW_TARGET_PLAYER:
            t = askChoice("Select a player:", AS_KW_PLAYERS)
            if t == 0:
               return False
            type = AS_KW_PLAYERS[t-1]
      
         target = self.getTarget(type, filters, zone, cards)
         debug("--- target: %s" % target)
         
         if target:
            # If an error was returned
            if isinstance(target, Exception):
               warning(ErrStrings[str(target)])
               return False
            break
      
      return target
      
   
   def getFilter(self, str):
   # Returns a filter as an array
      str  = str.strip()
      args = ''
      
      # Look for prefixes
      prfx, cmd = self.getPrefix(AS_PREFIX_RESTRS, str)
      
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
      
      
   def getObjFromPrefix(self, prefix):
      if prefix == AS_PREFIX_MY:
         return me
      if prefix == AS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      
   
   def getZoneCards(self, zone):
      prefix  = zone[0]
      zone    = zone[1]
      player  = self.getObjFromPrefix(prefix)
      cards = []
      
      if zone == AS_KW_ZONE_ARENA:
         cards = [c for c in table]
      
      if zone == AS_KW_ZONE_RING:
         cards = [c for c in table
            if not player
            or c.controller == player]
      
      if zone == AS_KW_ZONE_HAND and player:
         cards = [c for c in player.hand]
      
      if zone == AS_KW_ZONE_DECK and player:
         cards = [c for c in player.Deck]
      
      if zone == AS_KW_ZONE_DISCARD and player:
         cards = [c for c in player.piles['Discard Pile']]
      
      if zone == AS_KW_ZONE_KILL and player:
         cards = [c for c in player.piles['Kill Pile']]
            
      return cards
      
      
   def getTarget(self, type, filters, zone, cards):
      if type == AS_KW_TARGET_THIS:
         return Card(self.card_id)
      # If target is a player
      elif type in AS_KW_TARGET_IS_PLAYER:
         return self.applyFilterToPlayer(type, filters)
      else:
         # Filter cards with a target
         return self.applyFilterToCards(type, filters, zone, cards)
      
      
   def applyFilterToPlayer(type, filters):
      if isinstance(type, basestring):
         if type == AS_KW_TARGET_ME:
            player = me
         if type == AS_KW_TARGET_OPP:
            player = players[1] if len(players) > 1 else me
            
      # TODO Apply filters
      # for f in filters:
         
      return player
   
   
   def applyFilterToCards(type, filters, zone, cards):
      cards_f1 = []
      cards_f2 = []

      # Look for targeted cards
      if zone[1] in AS_KW_TARGET_ZONES:
         cards_f1 = [c for c in cards
            if c.targetedBy == me]
         if len(cards_f1) == 0:
            return Exception(ERR_NO_CARD_TARGETED)
            
      if type != AS_KW_ALL:
         # Look for (super) type
         if type in AS_KW_CARD_TYPES:
            cards_f1 = [c for c in cards
               if c.Type.lower() == type]
         # Look for subtype
         else:
            cards_f1 = [c for c in cards
               if c.Subtype.lower() == type]
      
      if len(cards_f1) == 0:
         return Exception(ERR_NO_CARDS)
            
      for filter in filters:
         # filter could be a list of chained filters
         if isinstance(filter[0], list):
            cards_f2 = cards_f1
            for f in filter:
               cards_f2 = self.applyFilter(f, cards_f2)
         else:
            cards_f2 = self.applyFilter(filter, cards_f1)
         # Break on any match
         if len(cards_f2) > 0:
            break
         
      if len(cards_f2) == 0:
         return Exception(ERR_NO_CARDS)
      return cards_f2
   
   
   def applyFilter(self, filter, cards):
      include = filter[0] != AS_PREFIX_NOT
      kw = filter[1]
   
      cards = [c for c in cards
         # filter = [prfx, cmd, [args]]
         if kw == AS_KW_FILTER_BP   and filterBP(c, include, *filter[2])
         or kw in AS_KW_CARD_TYPES and filterType(c, include, kw)
         or                            filterSubtype(c, include, kw)
      ]
         
      return cards
