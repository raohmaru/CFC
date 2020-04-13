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
# Filter class
#---------------------------------------------------------------------------

class RulesFilters():
   """ Class to handle the filters that are applied to a set of objects """
   filters = {}

   @staticmethod
   def registerFilter(name, filter):
      RulesFilters.filters[name] = filter
      
   
   @staticmethod   
   def applyFiltersTo(arr, filters):
      if len(filters) > 0:
         arr2 = []
         for filter in filters:
            # filter could be a list of chained filters (&)
            if isinstance(filter[0], list):
               arr2 = arr
               for f in filter:
                  arr2 = RulesFilters.applyFilter(f, arr2)
            # optional filter (,)
            else:
               arr2 += RulesFilters.applyFilter(filter, arr)
         arr = list(set(arr2))  # unique values
      return arr
   
   
   @staticmethod
   def applyFilter(filter, arr):
      # filter = [prfx, cmd, [args]]
      include = filter[0] != RS_PREFIX_MINUS
      cmd = filter[1]
      
      # Get the filter function
      if   cmd in RulesFilters.filters: func = RulesFilters.filters[cmd]
      elif cmd in RS_KW_CARD_TYPES    : func = filterType
      else                            : func = filterSubtype
      
      # Special filtering functions
      args = filter[2]
      if args:
         op, f = args
         if op == RS_OP_FUNC:
            if f == 'lowest':
               value = reduce(lambda a,b: min(a,b), [getCardProp(c, cmd) for c in arr])
               args = ('=', value)
   
      debug("-- applying filter %s to %s objects" % (filter, len(arr)))
      arr = [c for c in arr
         if func(c, include, cmd, *args)
      ]      
      debug("-- %s objects match the filter" % len(arr))
         
      return arr
      

#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def getCardProp(card, prop):
   if prop == 'bp':
      if getMarker(card, 'BP') > 0:
         return getMarker(card, 'BP')
      else:
         return num(card.BP) / BPMultiplier
   elif prop == 'sp':
      return num(card.SP)
       

def compareValuesByOp(v1, v2, op):
   if op == RS_OP_EQUAL:
      return v1 == v2
   elif op == RS_OP_LTE:
      return v1 <= v2
   elif op == RS_OP_GTE:
      return v1 >= v2
   return False


#---------------------------------------------------------------------------
# Filter functions
#---------------------------------------------------------------------------

def filterBP(card, include, cmd, *args):
   debug(">>> filterBP({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   
   if not isCard(card) or not isCharacter(card):
      return False
      
   # Get additional parameters
   try:
      op, value = args
   except:
      return False
   if op != RS_OP_FUNC:
      value = num(value)

   bp = getCardProp(card, 'bp')
      
   # Compare values
   res = compareValuesByOp(bp, value, op)
   if not include:
      res = not res
   debug("--- {} {} {} -> {}".format(bp, op, value, res))
   return res
   
   
def filterSP(card, include, cmd, *args):
   debug(">>> filterSP({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
      
   # Get additional parameters
   try:
      op, value = args
   except:
      return False
   if op != RS_OP_FUNC:
      value = num(value)

   sp = num(card.SP)
      
   # Compare values
   res = compareValuesByOp(sp, value, op)
   if not include:
      res = not res
   debug("--- {} {} {} -> {}".format(sp, op, value, res))
   return res


def filterType(card, include, cmd, *args):
   debug(">>> filterType({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   
   if not isCard(card):
      return False
      
   type = card.Type.lower()
   if include:
      return type == cmd
   else:
      return type != cmd


def filterSubtype(card, include, cmd, *args):
   debug(">>> filterSubtype({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   
   if not isCard(card):
      return False
      
   subtype = card.Subtype.lower()
   if include:
      return subtype == cmd
   else:
      return subtype != cmd


def filterBackedup(card, include, cmd, *args):
   debug(">>> filterBacked({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
      
   backups = getAttachmets(card)
   if include:
      return len(backups) > 0
   else:
      return len(backups) == 0
    
    
def filterBackup(card, include, cmd, *args):
   debug(">>> filterBackup({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
      
   isBackup = isAttached(card)
   if include:
      return isBackup
   else:
      return not isBackup
   
   
def filterAttack(card, include, cmd, *args):
   debug(">>> filterAttack({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   return hasMarker(card, 'Attack', include)
    
    
def filterUnitedAttack(card, include, cmd, *args):
   debug(">>> filterUnitedAttack({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
      
   attacking = card._id in getGlobalVar('UnitedAttack')   
   if include:
      return attacking
   else:
      return not attacking
   
   
def filterBlock(card, include, cmd, *args):
   debug(">>> filterBlock({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   return hasMarker(card, 'Counter-attack', include)
   
   
def filterBlocked(card, include, cmd, *args):
   debug(">>> filterBlocked({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   return hasMarker(card, 'Attack', include) and card._id in getGlobalVar('Blockers')
    
    
def filterFrozen(card, include, cmd, *args):
   debug(">>> filterFrozen({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
      
   frozen = isFrozen(card)
   if include:
      return frozen
   else:
      return not frozen
   
   
def filterJustEntered(card, include, cmd, *args):
   debug(">>> filterJustEntered({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   return hasMarker(card, 'Just Entered', include)
   
   
def filterHasAbility(card, include, cmd, *args):
   debug(">>> filterHasAbility({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
	  
   return bool(card.properties['Ability Type'])
   
   
def filterNoAbility(card, include, cmd, *args):
   debug(">>> filterNoAbility({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
	  
   return not card.properties['Ability Type']
      
      
def filterAbilityInstant(card, include, cmd, *args):
   debug(">>> filterAbilityInstant({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
	  
   return bool(card.properties['Ability Type']) and card.properties['Ability Type'] == InstantAbility
      
      
def filterAbilityTrigger(card, include, cmd, *args):
   debug(">>> filterAbilityTrigger({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
	  
   return bool(card.properties['Ability Type']) and card.properties['Ability Type'] == TriggerAbility
      
      
def filterAbilityAuto(card, include, cmd, *args):
   debug(">>> filterAbilityAuto({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
	  
   return bool(card.properties['Ability Type']) and card.properties['Ability Type'] == AutoAbility


RulesFilters.registerFilter('bp'       , filterBP)
RulesFilters.registerFilter('sp'       , filterSP)
RulesFilters.registerFilter('type'     , filterType)
RulesFilters.registerFilter('subtype'  , filterSubtype)
RulesFilters.registerFilter('backedup' , filterBackedup)
RulesFilters.registerFilter('backup'   , filterBackup)
RulesFilters.registerFilter('attack'   , filterAttack)
RulesFilters.registerFilter('uattack'  , filterUnitedAttack)
RulesFilters.registerFilter('block'    , filterBlock)
RulesFilters.registerFilter('blocked'  , filterBlocked)
RulesFilters.registerFilter('frozen'   , filterFrozen)
RulesFilters.registerFilter('fresh'    , filterJustEntered)
RulesFilters.registerFilter('powerful' , filterHasAbility)
RulesFilters.registerFilter('powerless', filterNoAbility)
RulesFilters.registerFilter('abinstant', filterAbilityInstant)
RulesFilters.registerFilter('abtrigger', filterAbilityTrigger)
RulesFilters.registerFilter('abauto'   , filterAbilityAuto)
