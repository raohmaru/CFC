# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Filter class
#---------------------------------------------------------------------------

class RulesFilters():
   """
   Class to handle the filters that are applied to a set of objects.
   """
   filters = {}

   @staticmethod
   def registerFilter(name, filter):
      RulesFilters.filters[name] = filter
      
   
   @staticmethod   
   def applyFiltersTo(objects, filters):
      if len(filters) > 0:
         res = []
         for filter in filters:
            # filter could be a list of chained filters (&)
            if isinstance(filter[0], list):
               arr = objects
               for f in filter:
                  arr = RulesFilters.applyFilter(f, arr)
               res += arr
            # optional filter (,)
            else:
               res += RulesFilters.applyFilter(filter, objects)
         # res = list(set(res))  # unique values not ordered
         return unique(res)  # unique values ordered
      return objects
   
   
   @staticmethod
   def applyFilter(filter, arr):
      # filter = [prfx, cmd, [args]]
      include = filter[0] not in [RS_PREFIX_MINUS, RS_PREFIX_OTHER]
      cmd = filter[1]
      # Get the filter function
      if   cmd in RulesFilters.filters: func = RulesFilters.filters[cmd]
      elif cmd in RS_KW_CARD_TYPES    : func = filter_type
      else                            : func = filter_subtype
      # Special filtering functions
      args = filter[2]
      if args:
         op, selector = args
         if op == RS_OP_SELECTOR:
            # Gets the lowest value in the array
            if selector == "lowest":
               value = reduce(lambda a, b: min(a, b), [getCardProp(c, cmd) for c in arr])
               args = ("=", value)
      # Apply the filters
      debug("-- applying filter {} to {} object(s)", filter, len(arr))
      res = [c for c in arr
         if func(c, include, cmd, *args)
      ]      
      debug("-- {} object(s) match(es) the filter", len(res))
      return res
      

#---------------------------------------------------------------------------
# Related functions
#---------------------------------------------------------------------------

def getCardProp(card, prop):
   if prop == "bp":
      bp = getMarker(card, "BP")
      if bp == 0:
         bp = card.BP
      return bp
   elif prop == "sp":
      return card.SP
       

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

def filter_bp(card, include, cmd, *args):
   debug(">>> filter_bp({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card) or not isCharacter(card):
      return False
   # Get additional parameters
   try:
      op, value = args
   except ValueError:
      return False
   bp = getCardProp(card, "bp")
   # Compare values
   res = compareValuesByOp(bp, value, op)
   if not include:
      res = not res
   debug("--- {} {} {} -> {}", bp, op, value, res)
   return res
   
   
def filter_sp(card, include, cmd, *args):
   debug(">>> filter_sp({}, {}, {}, {})", card, include, cmd, args)
   # Get additional parameters
   try:
      op, value = args
   except ValueError:
      return False
   sp = card.SP
   # Compare values
   res = compareValuesByOp(sp, value, op)
   if not include:
      res = not res
   debug("--- {} {} {} -> {}", sp, op, value, res)
   return res


def filter_type(card, include, cmd, *args):
   debug(">>> filter_type({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   type = card.Type.lower()
   if include:
      return type == cmd
   else:
      return type != cmd


def filter_subtype(card, include, cmd, *args):
   debug(">>> filter_subtype({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   subtype = card.Subtype.lower()
   if include:
      return subtype == cmd
   else:
      return subtype != cmd


def filter_backedup(card, include, cmd, *args):
   debug(">>> filter_backed({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   backups = getAttachments(card)
   if include:
      return len(backups) > 0
   else:
      return len(backups) == 0
    
   
def filter_attack(card, include, cmd, *args):
   debug(">>> filter_attack({}, {}, {}, {})", card, include, cmd, args)
   res = hasMarker(card, "Attack")
   if include:
      return res
   else:
      return not res
    
    
def filter_unitedAttack(card, include, cmd, *args):
   debug(">>> filter_unitedAttack({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   attacking = card._id in getGlobalVar("UnitedAttack")   
   if include:
      return attacking
   else:
      return not attacking
   
   
def filter_block(card, include, cmd, *args):
   debug(">>> filter_block({}, {}, {}, {})", card, include, cmd, args)
   res = hasMarker(card, "Counter-attack")
   if include:
      return res
   else:
      return not res
   
   
def filter_blocked(card, include, cmd, *args):
   debug(">>> filter_blocked({}, {}, {}, {})", card, include, cmd, args)
   res = hasMarker(card, "Attack") and card._id in getGlobalVar("Blockers")
   if include:
      return res
   else:
      return not res
    
    
def filter_frozen(card, include, cmd, *args):
   debug(">>> filter_frozen({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   frozen = isFrozen(card)
   if include:
      return frozen
   else:
      return not frozen
   
   
def filter_justEntered(card, include, cmd, *args):
   debug(">>> filter_justEntered({}, {}, {}, {})", card, include, cmd, args)
   res = hasMarker(card, "Just Entered")
   if include:
      return res
   else:
      return not res
   
   
def filter_hasAbility(card, include, cmd, *args):
   debug(">>> filter_hasAbility({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   return bool(card.properties["Ability Type"])
   
   
def filter_noAbility(card, include, cmd, *args):
   debug(">>> filter_noAbility({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   return not card.properties["Ability Type"]
      
      
def filter_abilityInstant(card, include, cmd, *args):
   debug(">>> filter_abilityInstant({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   return bool(card.properties["Ability Type"]) and card.properties["Ability Type"] == InstantAbility
      
      
def filter_abilityTrigger(card, include, cmd, *args):
   debug(">>> filter_abilityTrigger({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   return bool(card.properties["Ability Type"]) and card.properties["Ability Type"] == TriggerAbility
      
      
def filter_abilityAuto(card, include, cmd, *args):
   debug(">>> filter_abilityAuto({}, {}, {}, {})", card, include, cmd, args)
   if not isCard(card):
      return False
   return bool(card.properties["Ability Type"]) and card.properties["Ability Type"] == AutoAbility


RulesFilters.registerFilter("bp"       , filter_bp)
RulesFilters.registerFilter("sp"       , filter_sp)
RulesFilters.registerFilter("type"     , filter_type)
RulesFilters.registerFilter("subtype"  , filter_subtype)
RulesFilters.registerFilter("backedup" , filter_backedup)
RulesFilters.registerFilter("attack"   , filter_attack)
RulesFilters.registerFilter("uattack"  , filter_unitedAttack)
RulesFilters.registerFilter("block"    , filter_block)
RulesFilters.registerFilter("blocked"  , filter_blocked)
RulesFilters.registerFilter("frozen"   , filter_frozen)
RulesFilters.registerFilter("fresh"    , filter_justEntered)
RulesFilters.registerFilter("powerful" , filter_hasAbility)
RulesFilters.registerFilter("powerless", filter_noAbility)
RulesFilters.registerFilter("abinstant", filter_abilityInstant)
RulesFilters.registerFilter("abtrigger", filter_abilityTrigger)
RulesFilters.registerFilter("abauto"   , filter_abilityAuto)
