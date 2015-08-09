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

import re

# CONST LANGUAGE DEFINITION
# Regular expressions
AS_RGX_CMD_TARGET   = re.compile(r'^target\s*=\s*')
AS_RGX_TARGET_TYPE  = re.compile(r'\||\[')
AS_RGX_TARGET_RESTR = re.compile(r'\[(.+)\]')
AS_RGX_TARGET_PARAM = re.compile(r'(\w+)\s*([=><]+)\s*(\w+)')
AS_RGX_TARGET_ZONE  = re.compile(r'\|\s*([\w*]+).*$')

# Comments
AS_COMMENT_CHAR = '#'

# Operators
AS_OP_OR    = ','
AS_OP_AND   = '&'
AS_OP_EQUAL = '='
AS_OP_LTE   = '>='
AS_OP_GTE   = '<='

# Prefixes
AS_PREFIX_NOT = '-'
AS_PREFIX_MY  = 'my'
AS_PREFIX_OPP = 'opp'

AS_PREFIX_ZONES = [
   AS_PREFIX_MY,
   AS_PREFIX_OPP
]

AS_PREFIX_RESTRS = [
   AS_PREFIX_NOT
]

# Keywords
AS_KW_ALL = '*'

AS_KW_TARGET_PLAYER   = 'player'
AS_KW_TARGET_ME       = 'me'
AS_KW_TARGET_OPP      = 'opp'
AS_KW_TARGET_THIS     = 'this'
AS_KW_TARGET_CHAR     = 'character'
AS_KW_TARGET_ACTION   = 'action'
AS_KW_TARGET_REACTION = 'reaction'
AS_KW_TARGETS = [
   AS_KW_TARGET_PLAYER,
   AS_KW_TARGET_ME,
   AS_KW_TARGET_OPP,
   AS_KW_TARGET_THIS,
   AS_KW_TARGET_CHAR,
   AS_KW_TARGET_ACTION,
   AS_KW_TARGET_REACTION,
   AS_KW_ALL
]

AS_KW_ZONE_ARENA   = 'arena'
AS_KW_ZONE_RING    = 'ring'
AS_KW_ZONE_HAND    = 'hand'
AS_KW_ZONE_DECK    = 'deck'
AS_KW_ZONE_DISCARD = 'discard'
AS_KW_ZONE_KILL    = 'kill'
AS_KW_ZONES = [
   AS_KW_ZONE_ARENA,
   AS_KW_ZONE_RING,
   AS_KW_ZONE_HAND,
   AS_KW_ZONE_DECK,
   AS_KW_ZONE_DISCARD,
   AS_KW_ZONE_KILL
]

AS_KW_RESTR_BP        = 'bp'
AS_KW_RESTR_SP        = 'sp'
AS_KW_RESTR_BACKED    = 'backed'
AS_KW_RESTR_BACKUP    = 'backup'
AS_KW_RESTR_ATTACK    = 'attack'
AS_KW_RESTR_UATTACK   = 'uattack'
AS_KW_RESTR_BLOCK     = 'block'
AS_KW_RESTR_FREEZED   = 'freezed'
AS_KW_RESTR_FRESH     = 'fresh'
AS_KW_RESTR_POWERLESS = 'powerless'
AS_KW_RESTRS = [
   AS_KW_RESTR_BP,
   AS_KW_RESTR_SP,
   AS_KW_RESTR_BACKED,
   AS_KW_RESTR_BACKUP,
   AS_KW_RESTR_ATTACK,
   AS_KW_RESTR_UATTACK,
   AS_KW_RESTR_BLOCK,
   AS_KW_RESTR_FREEZED,
   AS_KW_RESTR_FRESH,
   AS_KW_RESTR_POWERLESS,
   AS_KW_TARGET_CHAR,
   AS_KW_TARGET_ACTION,
   AS_KW_TARGET_REACTION
]


class Rules():
   """ Rule scripts parser """
   rule_id = ''
   parsed  = False
   target  = None

   def __init__(self, rule):
      self.rule_id = rule
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

      # Get the restrictions
      restrs = AS_RGX_TARGET_RESTR.search(str)
      restrs_arr = []
      if restrs:
         restrs = restrs.group(1).split(AS_OP_OR)
         # Check restrictions
         for restr in restrs:
            # AND restrictions
            restr = restr.split(AS_OP_AND)
            arr = []
            for r in restr:
               r = self.getRestr(r)
               # Check valid restriction kw
               if r[1] not in AS_KW_RESTRS:
                  debug("KeywordError: Invalid restriction '%s'" % r[1])
                  continue
               arr.append(r)
            debug("--- restr: %s" % arr)
            if len(arr) > 0:
               restrs_arr.append(arr if len(arr) > 1 else arr[0])

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
         'restrs': restrs_arr,
         'zone'  : [zone_prefix, zone]
      }


   def activate(self):
      debug("\nExecuting rules")
      if self.target:
         if not self.checkTargets(self.target):
            debug("Targeting canceled")
            return


   def checkTargets(self, target):
      debug("Checking targets")

      types  = target['types']
      zone   = target['zone']
      restrs = target['restrs']

      # Check target type
      # If two or more targets, maybe ask for a single target
      if len(types) > 1:
         # Check if there is any keyword in the target types
         kw_types = set(AS_KW_TARGETS) & set(types)
         if len(kw_types) > 0:
            if 'askChoice' in globals():  # For debug in the terminal
               t = askChoice("Select a target:", types)
            else:
               t = 1
            if t == 0:
               return False
            types = [types[t-1]]
      debug("--- types: %s" % types)
      
      # Get the zone object
      cards = self.getZoneCards(zone)
      debug("--- zone %s cards: %s" % (''.join(zone), cards))
      
      # If target is a player...
      # for type in types:
         # if self.isPlayer(types):
      
      return True
      
   
   def getRestr(self, str):
   # Returns a restriction as an array
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
      
      
   def getPrefixObj(self, prefix):
      if prefix == AS_PREFIX_MY:
         return me
      if prefix == AS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      
   
   def getZoneCards(self, zone):
      prefix  = zone[0]
      zone    = zone[1]
      player  = self.getPrefixObj(prefix)
      targets = []
      
      if zone == AS_KW_ZONE_ARENA:
         targets = [c for c in table]
      
      if zone == AS_KW_ZONE_RING:
         targets = [c for c in table
            if not player
            or c.controller == player]
      
      if zone == AS_KW_ZONE_HAND and player:
         targets = [c for c in player.hand]
      
      if zone == AS_KW_ZONE_DECK and player:
         targets = [c for c in player.Deck]
      
      if zone == AS_KW_ZONE_DISCARD and player:
         targets = [c for c in player.piles['Discard Pile']]
      
      if zone == AS_KW_ZONE_KILL and player:
         targets = [c for c in player.piles['Kill Pile']]
            
      return targets


# Enabled only from the python terminal
# if 'debug' not in globals():
   # def debug(str):
      # print str
      
   # if 'RulesDict' not in globals():
      # from cardsRules import RulesDict 
   # rules = Rules('aa867ea1-89f8-4154-8e20-2263edd00014')
   # rules.activate()