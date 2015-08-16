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
# Filter functions
#---------------------------------------------------------------------------

def filterBP(card, include, cmd, *args):
   debug(">>> filterBP({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
   
   if not isCard(card):
      return False
      
   # Get additional parameters
   try:
      op, value = args
   except:
      return False
   value = num(value)

   if getMarker(card, 'BP') > 0:
      bp = getMarker(card, 'BP')
   else:
      bp = num(card.BP)
      
   # Compare values
   res = compareValuesByOp(bp, value, op)
   if not include:
      res = not res
   return res

   
def filterSP(card, include, cmd, *args):
   debug(">>> filterSP({}, {}, {}, {})".format(card, include, cmd, args)) #Debug
      
   # Get additional parameters
   try:
      op, value = args
   except:
      return False
   value = num(value)

   sp = num(card.SP)
      
   # Compare values
   res = compareValuesByOp(sp, value, op)
   if not include:
      res = not res
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

   if not isCard(card):
      return False
      
   attacking = MarkersDict['Attack'] in card.markers
   if include:
      return attacking
   else:
      return not attacking
      
      
def filterUnitedAttack(card, include, cmd, *args):
   debug(">>> filterUnitedAttack({}, {}, {}, {})".format(card, include, cmd, args)) #Debug

   if not isCard(card):
      return False
      
   attacking = card._id in getGlobalVar('UnitedAttack')   
   if include:
      return attacking
   else:
      return not attacking
      

#---------------------------------------------------------------------------
# Helpers
#---------------------------------------------------------------------------

def isPlayer(obj):
   return isinstance(obj, Player)


def isCard(obj):
   return isinstance(obj, Card)


def isAttached(card):
   backups = getGlobalVar('Backups')
   return bool(backups.get(card._id))


def compareValuesByOp(v1, v2, op):
   if op == AS_OP_EQUAL:
      return v1 == v2
   elif op == AS_OP_LTE:
      return v1 <= v2
   elif op == AS_OP_GTE:
      return v1 >= v2
      
   return False
