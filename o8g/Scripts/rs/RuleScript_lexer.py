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
target: [
   {
      'filters': [
         ['-', 'bp', ('>=', '800')]
      ],
      'types': ['characters'],
      'typeop': ',',
      'zone': ['opp', 'ring'],
      'pick': -1,
      'qty': ',4',
      'opt': False,
      'selector': (type, expr)
   }
],
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
   effects: [
      [
         ['if', 'expression', {action}],
         [
            ['destroy'],
            ['draw', ['2']],
            ('+', 'unblockable')
         ],
         {
            'filters': [],
            'types': ['character'],
            'zone': ['', 'arena']
         },
         ['opp', 'ueot']
      ]
   ]
},
abilities: [
   'ability', 'ability'
],
auto: {
   [@see action],
   event: [
      ['my', 'handchanges', 'fromthis']
   ]
},
requisite: [
   'char<1>@oppring',
   'char<1>@myring'
],
vars: [
   ['varname', 'value or expr']
],
label: [
   'String label'
]
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

      for rule in rules:
         rule = rule.strip()
         line = rule.lower()
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
               flag = RS_OP_OPT if RS_OP_OPT in match.group() else None
               targets = line[len(match.group()):].split(RS_OP_SEP)
               targetsList = []
               for target in targets:
                  targetsList.append(RulesLexer.parseTarget(target, flag))
               rulesDict[RS_KEY_TARGET] = targetsList
         # else:
            # debug("Target already defined. Line skipped")

         # Check for action command
         match = RS_RGX_KEY_ACTION.match(line)
         if match:
            debug("Action key found!")
            action = RulesLexer.parseAction( line[len(match.group()):] )
            if RS_KEY_ACTION in rulesDict:
               if not isinstance(rulesDict[RS_KEY_ACTION], list):
                  rulesDict[RS_KEY_ACTION] = [rulesDict[RS_KEY_ACTION]]
               rulesDict[RS_KEY_ACTION].append(action)
            else:
               rulesDict[RS_KEY_ACTION] = action
         # else:
            # debug("Action already defined. Line skipped")
            
         # Check for abilities command
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
            
         # Check for conditions command
         if not RS_KEY_REQ in rulesDict:
            match = RS_RGX_KEY_REQ.match(line)
            if match:
               debug("Requisite key found!")
               rulesDict[RS_KEY_REQ] = line[len(match.group()):].split(RS_OP_BOOL_AND)
            
         # Check for variables command
         if not RS_KEY_VARS in rulesDict:
            match = RS_RGX_KEY_VARS.match(line)
            if match:
               debug("Variables key found!")
               rulesDict[RS_KEY_VARS] = RulesLexer.parseVars( line[len(match.group()):] )
            
         # Check for label command
         match = RS_RGX_KEY_LABEL.match(line)
         if match:
            debug("Label key found!")
            label = rule[len(match.group()):].strip('"').strip("'")
            if RS_KEY_LABEL in rulesDict:
               rulesDict[RS_KEY_LABEL].append(label)
            else:
               rulesDict[RS_KEY_LABEL] = [label]
            
      debug("{}".format(rulesDict))
      return rulesDict


   @staticmethod
   def parseTarget(tgtStr, flag=None):
      tgtStr = tgtStr.strip()
      debug("Parsing target: %s" % tgtStr)
      
      # Get the quantity of cards to get
      qty_match = RS_RGX_TARGET_QTY.search(tgtStr)
      qty = None
      if qty_match:
         qty = qty_match.group(1)
         tgtStr = tgtStr.replace(qty_match.group(0), '', 1)
      
      # Get the cards to pick
      pick_match = RS_RGX_TARGET_PICK.search(tgtStr)
      pick = None
      if pick_match:
         pick = int(pick_match.group(1))
         tgtStr = tgtStr.replace(pick_match.group(0), '', 1)
      
      # Get the selector
      sel_match = RS_RGX_KEY_SELECTOR.search(tgtStr)
      selector = None
      if sel_match:
         selector = sel_match.groups()
         tgtStr = tgtStr.replace(sel_match.group(0), '')

      # Get the types
      types = RS_RGX_TARGET_TYPE.split(tgtStr)[:1]
      typeOp = RS_OP_OR
      if not types[0]:
         debug("ParseInfo: 'target' has no type parameter. Defult target is {}".format(RS_KW_ANY))
         types[0] = RS_KW_ANY
      for op in RS_TARGET_OPS:
         if len(types) <= 1:
            types = types[0].split(op)
            typeOp = op
      # RS_KW_ANY overrides the rest
      if RS_KW_ANY in types:
         types = [RS_KW_ANY]
      elif RS_KW_ALL in types:
         types = [RS_KW_ANY + RS_SUFFIX_PLURAL]
      else:
         types = map(str.strip, types)
      debug("-- types: %s" % types)

      # Get the filters
      filters = RS_RGX_TARGET_FILTERS.search(tgtStr)
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
         'qty'     : qty,
         'pick'    : pick,
         'types'   : types,
         'typeop'  : typeOp,
         'filters' : filters_arr,
         'zone'    : [zone_prefix, zone],
         'opt'     : True if flag == RS_OP_OPT else False,
         'selector': selector
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
      firstEffect = None
      match = RS_RGX_AC_EVENT.match(acStr)
      if match:
         acStr = acStr[len(match.group()):]
         event = []
         events = match.group(1).split(',')
         for e in events:
            e = e.strip().replace(' ', '').split(':')
            # Look for prefixes
            prfx, eventName = RulesLexer.getPrefix(RS_PREFIX_EVENTS, e[0])
            if prfx == RS_PREFIX_MY:
               prfx = ''
            # Look for suffixes
            sffx = ''
            if len(e) > 1:
               if e[1] in RS_SUFFIX_EVENTS:
                  sffx = e[1]
               # transform suffiz into an if condition
               else:
                  debug("-- transforming suffix \"{0}\" into [[if {0}]]".format(e[1]))
                  firstEffect = [["if", e[1]], [], None, None]
            debug("-- found event: %s + %s + %s" % (prfx, eventName, sffx))
            event.append([prfx, eventName, sffx])
            
      # Analyze the expression
      effects = []
      expressions = acStr.split(RS_OP_SEP)
      for expr in expressions:
         debug("-- Parsing effect '%s'" % expr)
         if firstEffect:
            debug("---- Found initial effect '%s'" % firstEffect)
            effect = firstEffect
            firstEffect = None
         else:
            effect = [None, None, None, None]
         # Look for up to 1 condition
         match = RS_RGX_COND.search(expr)
         if match:
            kw, params = RulesLexer.extractKeyword(match.group(1), RS_KW_CMD_COND)
            if kw:
               if effect[0]:
                  effect[0][1] += " and " + params
               else:
                  effect[0] = [kw, params]
               debug("---- found condition '%s'" % effect[0])
            expr = re.sub(RS_RGX_COND, '', expr, 1).strip()
            # look for an elif/else condition
            if kw == RS_KW_COND_IF:               
               match = RS_RGX_COND.search(expr)
               if match:
                  kw, params = RulesLexer.extractKeyword(match.group(1), RS_KW_CMD_COND_SUB)
                  if kw:
                     debug("---- found condition '%s'" % kw)
                     subexpr = expr.replace(RS_KW_COND_ELIF, RS_KW_COND_IF)
                     subexpr = subexpr[match.start(0):]
                     effect[0].append(RulesLexer.parseAction(subexpr))
                  expr = expr[:match.start(0)]
            # Remove any invalid condition
            expr = re.sub(RS_RGX_COND, '', expr).strip()
                  
         # Look for up to 1 restriction
         kw, expr = RulesLexer.extractKeyword(expr, RS_KW_CMD_RESTRS, RS_PREFIX_RESTR)
         if kw:
            effect[3] = kw
            debug("---- found restriction %s" % (kw,))
         # Has target?
         match = RS_RGX_AC_TARGET.search(expr)
         if match:
            debug("---- found target '%s'" % match.group(2))
            effect[2] = RulesLexer.parseTarget(match.group(2), match.group(1))
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
               params = filter(None, RS_RGX_AC_ARGS_SEP.split(match.group(2)))
               params = [p.strip() for p in params]
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
   def parseVars(str):
      debug("Parsing vars: %s" % str)
      strArr = str.split(RS_OP_SEP)
      vars = []
      for item in strArr:
         vars.append([v.strip() for v in item.split(RS_OP_ASSIGN)])
      return vars
      
   
   @staticmethod
   def getFilter(str):
   # Returns a filter as an array
      str  = str.strip()
      args = ''
      
      # Look for prefixes
      prfx, cmd = RulesLexer.getPrefix(RS_PREFIX_FILTERS, str)
      
      # Look for parameters
      params = RS_RGX_TARGET_FPARAM.match(cmd)
      if params:
         cmd = params.group(1)
         args = params.group(2, 3)
      
      return [prfx, cmd, args]
      
   
   @staticmethod
   def getPrefix(prefixes, str, defPrefix = ''):
   # Get the prefix for a given string
      for p in prefixes:
         if str[:len(p)] == p:
            cmd = str[len(p):].strip()
            return (p, cmd)
      return (defPrefix, str)
      
      
   @staticmethod
   def getSuffix(suffixes, str):
   # Get the suffix for a given string
      for p in suffixes:
         if str[-len(p):] == p:
            cmd = str[:-len(p)].strip()
            return (p, cmd)
      return ('', str)
      
      
   @staticmethod
   def extractKeyword(str, keywords, prefixes = None):
   # Extract any one keyword that match from the keywords list for the given string
      strArr = str.split(" ")
      for i, kw in enumerate(strArr):
         prefix = ''
         if prefixes:
            prefix, kw = RulesLexer.getPrefix(prefixes, kw)
         if kw in keywords:
            str = str.replace(prefix + kw, "", 1)
            if prefixes:
               kw = (prefix, kw)
            return (kw, str.strip())
      return ('', str)
      