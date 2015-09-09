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

if not 'AS_VERSION' in globals():
   from RuleScript_config import *

class RulesLexer():

   @staticmethod
   def parse(rules):
      rules = rules.strip().split('\n')
      rulesDict = {}

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
         if not 'target' in rulesDict:
            match = AS_RGX_CMD_TARGET.match(line)
            if match:
               rulesDict['target'] = RulesLexer.parseTarget( line[len(match.group()):] )
         # else:
            # debug("Target already defined. Line skipped")

         # Check for action command
         if not 'action' in rulesDict:
            match = AS_RGX_CMD_ACTION.match(line)
            if match:
               rulesDict['action'] = RulesLexer.parseAbility( line[len(match.group()):] )
         # else:
            # debug("Action already defined. Line skipped")
            
      return rulesDict


   @staticmethod
   def parseTarget(tgtStr):
      tgtStr = tgtStr.strip()
      debug("Parsing target '%s'" % tgtStr)

      # Get the types
      types = AS_RGX_TARGET_TYPE.split(tgtStr)
      if not types[0]:
         debug("ParseError: 'target' has no type parameter")
         return False
      types = types[0].split(AS_OP_OR)
      # AS_KW_ALL overrides the rest
      if AS_KW_ALL in types:
         types = [AS_KW_ALL]
      else:
         types = map(str.strip, types)
      debug("-- types: %s" % types)

      # Get the filters
      filters = AS_RGX_TARGET_RESTR.search(tgtStr)
      filters_arr = []
      if filters:
         filters = filters.group(1).split(AS_OP_OR)
         # Check filters
         for filter in filters:
            # AND filters
            filter = filter.split(AS_OP_AND)
            arr = []
            for f in filter:
               arr.append(RulesLexer.getFilter(f))
            debug("-- filter: %s" % arr)
            if len(arr) > 0:
               filters_arr.append(arr if len(arr) > 1 else arr[0])

      # Get the zone
      zone = AS_RGX_TARGET_ZONE.search(tgtStr)
      zone_prefix = ''
      if zone:
         zone = zone.group(1)
      else:
         zone = AS_KW_ZONE_ARENA
      # Check for zone prefixes
      if zone != AS_KW_ZONE_ARENA:
         zone_prefix, zone = RulesLexer.getPrefix(AS_PREFIX_ZONES, zone)
      # Check valid zones
      if zone not in AS_KW_ZONES:
         debug("KeywordError: Invalid zone '%s'. Assuming '%s'" % (zone, AS_KW_ZONE_ARENA))
         zone = AS_KW_ZONE_ARENA
      debug("-- zone prefix: %s" % zone_prefix)
      debug("-- zone: %s" % zone)
      
      return {
         'types'  : types,
         'filters': filters_arr,
         'zone'   : [zone_prefix, zone]
      }


   @staticmethod
   def parseAbility(abStr):
      abStr = abStr.strip()
      debug("Parsing ability '%s'" % abStr)
      
      # Get the cost
      cost = None
      match = AS_RGX_EF_COST.match(abStr)
      if match:
         abStr = abStr[len(match.group()):]
         cost = match.group(1).replace(" ", "")
         debug("-- found cost: %s" % cost)
         # Check if cost has a target
         parts = cost.split('(')
         if len(parts) > 1:
            cost = parts[:2]
            # Remove last ")" character
            cost[1] = cost[1][:-1]
            debug("-- cost target: %s" % cost[1])
            cost[1] = RulesLexer.parseTarget(cost[1])
            
      # Analyze the expression
      effects = []
      expressions = abStr.split(AS_OP_SEP)
      for expr in expressions:
         debug("-- Parsing effect '%s'" % expr)
         arr = [None] * 4
         # Look for up to 1 condition
         kw, expr = RulesLexer.extractKeywordWithParams(expr, AS_KW_EFFECT_COND)
         if kw:
            arr[0] = kw
            debug("---- found condition '%s'" % kw)
         # Look for up to 1 restriction
         kw, expr = RulesLexer.extractKeyword(expr, AS_KW_EFFECT_RESTRS)
         if kw:
            arr[3] = kw
            debug("---- found restriction '%s'" % kw)
         # Has target?
         match = AS_RGX_EF_TARGET.search(expr)
         if match:
            debug("---- found target '%s'" % match.group(1))
            arr[2] = RulesLexer.parseTarget(match.group(1))
            expr = re.sub(AS_RGX_EF_TARGET, '', expr).strip()
         # Finnaly, get the effects
         match = AS_RGX_EF_EFFECT.findall(expr)
         if match:
            arr[1] = []
            for eff in match:
               params = eff[1].replace(' ','').split(',') if eff[1] else None
               arr[1].append([eff[0], params])
               debug("---- found effect '%s'" % arr[1][-1])
            effects.append(arr)
         
      return {
         'cost'   : cost,
         'effects': effects
      }
      
   
   @staticmethod
   def getFilter(str):
   # Returns a filter as an array
      str  = str.strip()
      args = ''
      
      # Look for prefixes
      prfx, cmd = RulesLexer.getPrefix(AS_PREFIX_FILTERS, str)
      
      # Look for parameters
      params = AS_RGX_TARGET_PARAM.match(cmd)
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
         match = AS_RGX_PARAM.match(str)
         if match:
            params = match.group(1).split(',')
            kw.append(params)
            str = str[len(match.group()):]
            print str
      return (kw, str)