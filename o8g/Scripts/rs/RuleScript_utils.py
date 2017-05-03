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
# Utility class
#---------------------------------------------------------------------------

class RulesUtils():
   """ Class to handle the custom events that happens during the game """

   @staticmethod
   def getObjFromPrefix(prefix):
   # Returns an object of the game from the given prefix
      if prefix == RS_PREFIX_MY:
         return me
      if prefix == RS_PREFIX_OPP:
         return players[1] if len(players) > 1 else me
      return None
      

   @staticmethod
   def getZoneByName(name):
      prefix, name = RulesLexer.getPrefix(RS_PREFIX_ZONES, name)
      player = RulesUtils.getObjFromPrefix(prefix) or me      
      zone = None
      
      if name == RS_KW_ZONE_ARENA or name == RS_KW_ZONE_RING:
         zone =  table
      
      elif name == RS_KW_ZONE_HAND:
         zone = player.hand
      
      elif name == RS_KW_ZONE_DECK:
         zone = player.Deck
      
      elif name == RS_KW_ZONE_DISCARD:
         zone = player.piles['Discard Pile']
      
      elif name == RS_KW_ZONE_KILL:
         zone = player.piles['Removed Pile']
         
      debug("getZoneByName({}) => {}".format(name, zone)) #Debug     
            
      return zone
      

   @staticmethod
   def getCardsFromZone(zone):
   # Get all the cards from the given zone
      if isinstance(zone, basestring):
         prefix  = ''
      else:
         prefix  = zone[0]
         zone    = zone[1]
      player  = RulesUtils.getObjFromPrefix(prefix) or me
      cards = []
      
      if zone == RS_KW_ZONE_ARENA:
         rings = getGlobalVar('Ring', me)
         if len(players) > 1:
            rings += getGlobalVar('Ring', players[1])
         cards = [c for c in table
            if c._id in rings]
      
      elif zone == RS_KW_ZONE_RING:
         ring = getGlobalVar('Ring', player)
         cards = [c for c in table
            if c._id in ring]
      
      elif zone == RS_KW_ZONE_HAND:
         cards = [c for c in player.hand]
      
      elif zone == RS_KW_ZONE_DECK:
         cards = [c for c in player.Deck]
      
      elif zone == RS_KW_ZONE_DISCARD:
         cards = [c for c in player.piles['Discard Pile']]
      
      elif zone == RS_KW_ZONE_KILL:
         cards = [c for c in player.piles['Removed Pile']]
            
      return cards
      