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
         return getOpp()
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
      

   @staticmethod
   def getTargets(target, source=None, msg=None):
      debug("Checking targets")

      types   = target['types']
      zone    = target['zone']
      filters = target['filters']
      
      # If two or more targets, ask for a single target
      if len(types) > 1:
         # Check if there is any keyword in the target types
         kw_types = set(RS_KW_TARGETS) & set(types)
         if len(kw_types) > 0:
            t = askChoice("Select a target:", types)
            if t == 0:
               return False
            types = [types[t-1]]
            debug("-- type selected: %s" % types)
      
      # Get all the cards from the given zone
      debug("-- Getting all cards from zone %s" % ''.join(zone))
      cards = RulesUtils.getCardsFromZone(zone)
      debug("-- Retrieved %s cards" % len(cards))
      
      # Filter targets
      for type in types:
         # If kw is 'player' then must choose between himself or enemy
         if type == RS_KW_TARGET_PLAYER:
            t = askChoice("Select a player:", RS_KW_PLAYERS)
            if t == 0:
               return False
            type = RS_KW_PLAYERS[t-1]      
         targets = RulesUtils.filterTargets(type, filters, zone, cards, source=None, targeted=True, msg=msg)         
         if targets == False:
            return False
      
      return targets
      
      
   @staticmethod
   def filterTargets(type, filters, zone, cards, source=None, targeted=False, msg=None):
      debug("-- filter targets by type '%s' in zone %s" % (type, zone))
      targets = None
      if type == RS_KW_TARGET_THIS and source:
         targets = [source]
      # If target is a player
      elif type in RS_KW_TARGET_IS_PLAYER:
         targets = RulesUtils.filterPlayers(type, filters)
      else:
         # Filter cards with a target
         targets = RulesUtils.filterCards(type, filters, zone, cards, source, targeted, msg)
         
      if isinstance(targets, list):
         debug("-- %s targets retrieved" % len(targets))
         if len(targets) < 10:
            for t in targets:
               debug(" '- target: {}".format(t))
      return targets
      
      
   @staticmethod
   def filterPlayers(type, filters):
      if isinstance(type, basestring):
         if type == RS_KW_TARGET_ME:
            arr = [me]
         elif type == RS_KW_TARGET_OPP:
            arr = [getOpp()]
         elif type == RS_KW_TARGET_PLAYERS:
            arr = [me]
            if len(players) > 1:
               arr.append(players[1])
            
      debug("-- applying {} filters to player {}".format(len(filters), arr))
            
      # Apply filters      
      arr = RulesFilters.applyFiltersTo(arr, filters)
         
      if len(arr) == 0:
         warning(MSG_ERR_NO_FILTERED_PLAYERS)
         return False
      
      return arr
   
   
   @staticmethod
   def filterCards(type, filters, zone, cards, source=None, targeted=False, msg=None):
      debug("-- applying %s filters to %s cards" % (len(filters), len(cards)))
      
      cards_f1 = cards
      multiple = False
            
      # Check for type suffixes
      typeSuffix, type = RulesLexer.getSuffix(RS_SUFFIX_TYPES, type)
      if typeSuffix:
         debug("-- found suffix '%s' in '%s'" % (typeSuffix, type+typeSuffix))
         # Allow multiple selection?
         if typeSuffix == RS_SUFFIX_PLURAL:
            multiple = True
            targeted = False
      
      # Check for type prefixes
      typePrefix, type = RulesLexer.getPrefix(RS_PREFIX_TYPES, type)
      if typePrefix:
         debug("-- found prefix '%s' in '%s'" % (typePrefix, typePrefix+type))
         # Targeting other cards?
         if typePrefix == RS_PREFIX_OTHER:
            # Current card can't be selected
            card = source
            if card in cards_f1:
               whisper(MSG_ERR_TARGET_OTHER.format(card))
               cards_f1.remove(card)
               # return False
            
      if type != RS_KW_ALL:
         # Look for (super) type
         if type in RS_KW_CARD_TYPES:
            debug("-- checking if any card match type '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Type.lower() == type]
            debug( ("{}, " * len(cards_f1)).format(*cards_f1) )
         # Look for subtype
         else:
            debug("-- checking if any card match subtype '%s'" % type)
            cards_f1 = [c for c in cards_f1
               if c.Subtype.lower() == type]
            debug( ("{}, " * len(cards_f1)).format(*cards_f1) )

      # Look for targeted cards
      if targeted:
         if zone[1] in RS_KW_TARGET_ZONES:
            cards_f2 = [c for c in cards_f1
               if c.targetedBy == me]
            if len(cards_f2) == 0:
               # Last chance to select a card
               if not msg:
                  msg = MSG_SEL_CARD_EFFECT
               cards_f1 = showCardDlg(cards_f1, msg.format(zone[1]))
               if cards_f1 == None:
                  # warning(MSG_ERR_NO_CARD_TARGETED)
                  return False
            debug("-- %s cards targeted" % len(cards_f1))
         else:
            targeted = False
         
      # Check if only 1 target has been selected
      if not multiple and targeted and len(cards_f1) > 1:
         warning(MSG_ERR_MULTIPLE_TARGET)
         return False
            
      # Apply filters
      cards_f1 = RulesFilters.applyFiltersTo(cards_f1, filters)
         
      if not multiple:
         if len(cards_f1) == 0:
            warning(MSG_ERR_NO_FILTERED_CARDS)
            return False
         # Check if more than 1 target has been selected
         elif len(cards_f1) > 1:
            if targeted:
               warning(MSG_ERR_MULTIPLE_TARGET)
               return False
            elif zone[1] in RS_KW_ZONES_PILES:
               if not msg:
                  msg = MSG_SEL_CARD
               cards_f1 = showCardDlg(cards_f1, msg.format(zone[1]))
               if cards_f1 == None:
                  # warning(MSG_ERR_NO_CARD_TARGETED)
                  return False
      
      # At this point there are not cards to which apply the effect, but the ability
      # is activated anyway
      if len(cards_f1) == 0:
         notify(MSG_ERR_NO_CARDS)
      
      return cards_f1
      