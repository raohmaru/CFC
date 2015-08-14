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

def filterBP(card, include, cmp, value):
# Filter card by BP
   if card.markers[MarkersDict['BP']] > 0:
      bp = card.markers[MarkersDict['BP']]
   else:
      bp = num(card.BP)

   if cmp == AS_OP_EQUAL:
      if include:
         return bp == value
      else:
         return bp != value
   elif cmp == AS_OP_LTE:
      return bp <= value
   elif cmp == AS_OP_GTE:
      return bp >= value
      
   return False
      

def filterType(card, include, value):
   type = card.Type.lower()
   if include:
      return type == value
   else
      return type != value
   

def filterSubtype(card, include, value):
   subtype = card.Subtype.lower()
   if include:
      return subtype == value
   else
      return subtype != value