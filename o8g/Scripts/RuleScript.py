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
AS_KW_ALL    = '*'

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
   AS_KW_ZONE_KILL,
   AS_KW_ALL
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
   parsed       = False
   has_target   = False

   def __init__(self, rule):
      self.rule_id = rule
      self.parse()


   def parse(self):
      if self.parsed:
         return      
      self.parsed = True
      
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
         if self.has_target != False:
            debug("Target already defined. Line skipped")
            continue
         self.has_target = AS_RGX_CMD_TARGET.match(line)
         if self.has_target:
            res = self.parseTarget( line[len(self.has_target.group()):] )
            if not res:
               self.has_target = None


   def parseTarget(self, str):
      str = str.strip()
      debug("Parsing target '%s'" % str)

      # Get the type
      type = AS_RGX_TARGET_TYPE.split(str)
      if not type[0]:
         debug("ParseError: 'target' has no type parameter")
         return False
      self.target_types = type[0].split(AS_OP_OR)
      if AS_KW_ALL in self.target_types:
         self.target_types = [AS_KW_ALL]
      debug("-- types: %s" % self.target_types)

      # get the restrictions
      self.target_restrs = AS_RGX_TARGET_RESTR.search(str)
      if self.target_restrs:
         self.target_restrs = self.target_restrs.group(1).split(AS_OP_OR)
         debug("-- restrictions: %s" % self.target_restrs)

      # get the zone
      zone = AS_RGX_TARGET_ZONE.search(str)
      if zone:
         self.target_zone = zone.group(1)
      else:
         self.target_zone = AS_KW_ZONE_ARENA
      debug("-- zone: '%s'" % self.target_zone)

      return True


   def activate(self):
      debug("\nExecuting rules")
      if self.has_target:
         if not self.getTarget():
            debug("Targeting canceled")
            return


   def getTarget(self):
      debug("Checking targets")

      types       = self.target_types
      zone        = self.target_zone
      zone_prefix = ''
      restrs      = self.target_restrs

      # Check for zone prefixes
      if zone != AS_KW_ALL:
         zone_prefix, zone = self.getPrefix(AS_PREFIX_ZONES, zone)
      debug("--- zone prefix: %s" % zone_prefix)
      debug("--- zone: %s" % zone)

      # Check valid zones
      if not zone in AS_KW_ZONES:
         debug("KeywordError: Invalid zone '%s'. Assuming '%s'" % (zone, AS_KW_ZONE_ARENA))
         zone = AS_KW_ZONE_ARENA

      # Check target type
      # If two or more targets, maybe ask for a target
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
      
      # Check restrictions
      if restrs:
         for restr in restrs:
            # AND restrictions
            restr = restr.split(AS_OP_AND)
            for r in restr:
               r = self.getRestr(r)
               debug("--- restr: %s" % r)
      
      return True
      
   
   def getRestr(self, str):
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
      for p in prefixes:
         if str[:len(p)] == p:
            cmd = str[len(p):].strip()
            return (p, cmd)
      return ('', str)
      


# Enabled only from the python terminal
# if 'debug' not in globals():
   # def debug(str):
      # print str
      
   # from cardsRules import RulesDict
   # rules = Rules('aa867ea1-89f8-4154-8e20-2263edd00014')
   # rules.activate()