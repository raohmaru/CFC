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
# RuleScript Parser
#---------------------------------------------------------------------------

# http://www.jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1
   
"""      
target: {
   'filters': [
      ['-', 'bp', ('>=', '800')]
   ],
   'types': ['characters'],
   'zone': ['opp', 'ring']
},
action: {
   cost: [
      [
         'd',
         {
            'filters': [],
            'types': ['action'],
            'zone': ['', 'arena']
         }
      ]
   ],
   event: [
      'my', 'handchanges', '=0'
   ],
   effects: [
      [
         ['may', ["'question?'"]],
         [
            ['destroy'],
            ['draw', ['2']],
            ('+', 'unblockable')
         ],
         {
            'filters': [],
            'types': ['character'],
            'zone': ['',
            'arena']
         },
         'ueot'
      ]
   ],
   abilities: [
      'ability', 'ability'
   ]
}
"""

# Import needed for testing out of OCTGN
if not 'RS_VERSION' in globals():
   from RuleScript_config import *
   
class RulesLexer():
   """ Analyzes the given string and split it into tokens that will be used by the parser """

   @staticmethod
   def tokenize(rules):
      """ Returns an array of tokens fromt the given string """
      debug("Rules to parse: %s" % rules)
      rules = rules.strip().split('\n')
      rulesDict = {}

      for line in rules:
         line = line.strip().lower()
         debug("Parsing line: %s" % line)

         # Skip comment lines
         if line[0] == RS_COMMENT_CHAR:
            debug("Leading comment char found. Line skipped")
            continue

         # Remove comments at the end of the line
         line = line.split(RS_COMMENT_CHAR)[0].rstrip()

         # Check for target command
         if not RS_KEY_TARGET in rulesDict:
            match = RS_RGX_KEY_TARGET.match(line)
            if match:
               debug("Target key found!")
               rulesDict[RS_KEY_TARGET] = RulesLexer.parseTarget( line[len(match.group()):] )
         # else:
            # debug("Target already defined. Line skipped")

         # Check for action command
         if not RS_KEY_ACTION in rulesDict:
            match = RS_RGX_KEY_ACTION.match(line)
            if match:
               debug("Action key found!")
               rulesDict[RS_KEY_ACTION] = RulesLexer.parseAction( line[len(match.group()):] )
         # else:
            # debug("Action already defined. Line skipped")
            
         if not RS_KEY_ABILITIES in rulesDict:
            match = RS_RGX_KEY_ABILITY.match(line)
            if match:
               debug("Abilities key found!")
               rulesDict[RS_KEY_ABILITIES] = RulesLexer.parseAbility( line[len(match.group()):] )

         # Check for auto command
         if not RS_KEY_AUTO in rulesDict:
            match = RS_RGX_KEY_AUTO.match(line)
            if match:
               debug("Auto key found!")
               rulesDict[RS_KEY_AUTO] = RulesLexer.parseAction( line[len(match.group()):] )
         # else:
            # debug("Action already defined. Line skipped")
            
      debug(rulesDict)
      return rulesDict


   @staticmethod
   def parseTarget(tgtStr):
      tgtStr = tgtStr.strip()
      debug("Parsing target: %s" % tgtStr)

      # Get the types
      types = RS_RGX_TARGET_TYPE.split(tgtStr)
      if not types[0]:
         debug("ParseError: 'target' has no type parameter")
         return False
      types = types[0].split(RS_OP_OR)
      # RS_KW_ALL overrides the rest
      if RS_KW_ALL in types:
         types = [RS_KW_ALL]
      else:
         types = map(str.strip, types)
      debug("-- types: %s" % types)

      # Get the filters
      filters = RS_RGX_TARGET_RESTR.search(tgtStr)
      filters_arr = []
      if filters:
         filters = filters.group(1).split(RS_OP_OR)
         # Check filters
         for filter in filters:
            # AND filters
            filter = filter.split(RS_OP_AND)
            arr = []
            for f in filter:
               arr.append(RulesLexer.getFilter(f))
            debug("-- filter: %s" % arr)
            if len(arr) > 0:
               filters_arr.append(arr if len(arr) > 1 else arr[0])

      # Get the zone
      zone = RS_RGX_TARGET_ZONE.search(tgtStr)
      zone_prefix = ''
      if zone:
         zone = zone.group(1)
      else:
         zone = RS_KW_ZONE_ARENA
      # Check for zone prefixes
      if zone != RS_KW_ZONE_ARENA:
         zone_prefix, zone = RulesLexer.getPrefix(RS_PREFIX_ZONES, zone)
      # Check valid zones
      if zone not in RS_KW_ZONES:
         debug("KeywordError: Invalid zone '%s'. Assuming '%s'" % (zone, RS_KW_ZONE_ARENA))
         zone = RS_KW_ZONE_ARENA
      debug("-- zone prefix: %s" % zone_prefix)
      debug("-- zone: %s" % zone)
      
      return {
         'types'  : types,
         'filters': filters_arr,
         'zone'   : [zone_prefix, zone]
      }


   @staticmethod
   def parseAction(acStr):
      acStr = acStr.strip()
      debug("Parsing action: %s" % acStr)
      
      # Get the cost
      cost = None
      match = RS_RGX_AC_COST.match(acStr)
      if match:
         cost = []
         acStr = acStr[len(match.group()):]
         # Remove whitespaces, 1st ({) and last (}) character and split 
         costs = match.group(1).replace(" ", "")[1:-1].split('}{')
         for c in costs:
            debug("-- found cost: %s" % c)
            # Check if cost has a target
            parts = c.split('(')
            if len(parts) > 1:
               c = parts[:2]
               # Remove last ")" character
               c[1] = c[1][:-1]
               debug("-- cost target: %s" % c[1])
               c[1] = RulesLexer.parseTarget(c[1])
            cost.append(c)
      
      # Get the event trigger
      event = None
      match = RS_RGX_AC_EVENT.match(acStr)
      if match:
         acStr = acStr[len(match.group()):]   
         # Look for prefixes
         prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, match.group(1))
         if prfx == RS_PREFIX_MY:
            prfx = ''
         event = [prfx, eventName, None]
         # Event expression
         if match.group(2):
            expr = match.group(2)[1:].replace(" ", "")
            if RulesLexer.isValidExpr(expr):
               event[2] = expr
            else:
               debug("-- expr was ignored: %s" % expr)
         debug("-- found event: %s" % event)
            
      # Analyze the expression
      effects = []
      expressions = acStr.split(RS_OP_SEP)
      for expr in expressions:
         debug("-- Parsing effect '%s'" % expr)
         effect = [None, None, None, None]
         # Look for up to 1 condition
         kw, expr = RulesLexer.extractKeywordWithParams(expr, RS_KW_CMD_COND)
         if kw:
            effect[0] = kw
            debug("---- found condition '%s'" % kw)
         # Look for up to 1 restriction
         kw, expr = RulesLexer.extractKeyword(expr, RS_KW_CMD_RESTRS)
         if kw:
            effect[3] = kw[0]
            debug("---- found restriction '%s'" % kw)
         # Has target?
         match = RS_RGX_AC_TARGET.search(expr)
         if match:
            debug("---- found target '%s'" % match.group(1))
            effect[2] = RulesLexer.parseTarget(match.group(1))
            expr = re.sub(RS_RGX_AC_TARGET, '', expr).strip()
         # Finally, get the commands
         effect[1] = []
         commands = expr.split(RS_OP_AND)
         for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
               continue 
            match = RS_RGX_AC_EFFECT.search(cmd)
            if match:
               params = match.group(2).replace(' ','').split(',')
               effect[1].append([match.group(1), params])
               debug("---- found effect '%s'" % effect[1][-1])
            else:
               cmd = RulesLexer.getPrefix(RS_PREFIX_BONUS, cmd)
               filter(None, cmd)
               effect[1].append(cmd)
         effects.append(effect)
         
      return {
         'cost'   : cost,
         'event'  : event,
         'effects': effects
      }


   @staticmethod
   def parseAbility(abStr):
      debug("Parsing ability: %s" % abStr)
      abilities = abStr.split(RS_OP_OR)
      abilities = [ item.strip() for item in abilities ]
      abilities = filter(None, abilities)
      return abilities
      
   
   @staticmethod
   def getFilter(str):
   # Returns a filter as an array
      str  = str.strip()
      args = ''
      
      # Look for prefixes
      prfx, cmd = RulesLexer.getPrefix(RS_PREFIX_FILTERS, str)
      
      # Look for parameters
      params = RS_RGX_TARGET_PARAM.match(cmd)
      if params:
         cmd = params.group(1)
         args = params.group(2, 3)
      
      return [prfx, cmd, args]
      
   
   @staticmethod
   def getPrefix(prefixes, str):
   # Get the prefix for a given string
      for p in prefixes:
         if str[:len(p)] == p:
            cmd = str[len(p):].strip()
            return (p, cmd)
      return ('', str)
      
      
   @staticmethod
   def getSuffix(suffixes, str):
   # Get the suffix for a given string
      for p in suffixes:
         if str[-len(p):] == p:
            cmd = str[:-len(p)].strip()
            return (p, cmd)
      return ('', str)
      
      
   @staticmethod
   def extractKeyword(str, keywords):
   # Extract any keyword that match from the keywords list for the given string
      kw = []
      matches = [k for k in keywords if k+' ' in str or ' '+k in str or k+'(' in str]
      if len(matches) > 0:
         kw = [matches[0]]
         # Remove keywords from the string
         for k in matches:
            str = str.replace(k, "")
      return (kw, str.strip())
      
      
   @staticmethod
   def extractKeywordWithParams(str, keywords):
   # Extract any keyword that match from the keywords list, and any additional
   # parameter within () for the given string
      kw, str = RulesLexer.extractKeyword(str, keywords)
      if str[0] == '(':
         match = RS_RGX_PARAM.match(str)
         if match:
            params = match.group(1).split(',')
            kw.append(params)
            str = str[len(match.group()):]
      return (kw, str)
      
      
   @staticmethod
   def isValidExpr(expr):
   # Checks if the expression is valid and is well-formed
      return bool(RS_RGX_EXPRESSION.match(expr))