# Python Scripts for the Card Fighters' Clash definition for OCTGN
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

import re

#---------------------------------------------------------------------------
# Card automation functions
#---------------------------------------------------------------------------

def parseCard(card, ruleId = None, init = True, dryRun = False):
   """ Wrapper for a Card object. Should only be called for cards added to the table or when its effect changes. """
   debug(">>> parseCard({}, {}, {}, {})".format(card, ruleId, init, dryRun))
   if not card._id in parsedCards or dryRun:
      if isCharacter(card):
         gc = CharCard(card, ruleId)
      else:
         gc = GameCard(card, ruleId)
      if not dryRun:
         parsedCards[card._id] = gc
      if init:
         gc.init()
      if dryRun:
         return gc
   return parsedCards.get(card._id)
   

def getParsedCard(card):
   debug("Retrieve parsed card for ID {} ({})".format(card._id, card))
   ruleId = None
   if card.controller != me:
      CharsAbilities = getGlobalVar('CharsAbilities')
      if card._id in CharsAbilities:
         ruleId = CharsAbilities[card._id]
      pcard = parsedCards.get(card._id)
      if pcard and ruleId and pcard.rule_id != ruleId:
         debug("Updating opp parsed card")
         removeParsedCard(card)
   return parseCard(card, ruleId, False)
   

def removeParsedCard(card):
   debug("Removed parsed card for ID {} ({})".format(card._id, card))
   removeGameEventListener(card._id)
   gc = parsedCards.pop(card._id, None)
   if gc:
      del gc.card
      del gc


class GameCard(object):
   """ A class which stores the card effect name and its parsed rule scripts """
   card    = None
   card_id = None
   rule_id = None
   rules   = None
   
   def __init__(self, card, ruleId = None):
      self.card = card
      self.card_id = card._id
      self.rule_id = ruleId if ruleId else card.model
      self.rules = Rules(self.rule_id, self.card_id)
      
   def init(self):
      if self.hasEffect():
         self.rules.init()
         
   def hasEffect(self):
      return True
      
   def activateEffect(self):
      if not self.hasEffect():
         return
      return self.rules.activate()
      
   @property
   def BP(self):
      return float('nan')  # Compared to a number will return always False


class CharCard(GameCard):
   """ A class which stores the character card ability name and its parsed rule scripts """
   ability = None
   lastBP = 0
   
   def __init__(self, card, ruleId = None):
      super(self.__class__, self).__init__(card, ruleId)
   
      ability = Ability(card, ruleId = ruleId)
      if ability.name:
         debug("Found ability {}".format(ability))
         self.ability = ability
      else:
         debug("No ability found")
         
   def hasEffect(self):
      return self.ability != None

   @property
   def BP(self):
      _BP = getMarker(self.card, 'BP')
      if _BP == 0 and self.card.group != table:
         _BP = int(self.card.BP) / BPDivisor
      return _BP


class Ability:
   """ A class that represents an ability """   
   ability = ""
   type    = ""
   name    = ""
   
   @property
   def unicodeChar(self):
      # Returns a unicode symbol for the type (for window forms)
      if self.type == InstantAbility: return InstantUniChar
      if self.type == TriggerAbility: return TriggerUniChar
      if self.type == AutoAbility   : return AutoUniChar
      return ""
   
   def __init__(self, obj, rules = None, ruleId = None):
      if isinstance(obj, basestring):
         ability = Regexps['ability'].match(obj)
         if ability:
            self.ability = ability.group(0)
            self.type    = ability.group(1)
            self.name    = ability.group(2)
            self.rules   = rules
      elif ruleId:
         cardData  = _extapi.getCardDataByModel(ruleId)
         cardProps = _extapi.getCardProperties(cardData)
         self.ability = cardProps['Ability']
         self.type    = cardProps['Ability Type']
         self.name    = cardProps['Ability Name']
         self.rules   = cardProps['Rules']
      elif obj.Ability:
         self.ability = obj.Ability
         self.type    = obj.properties['Ability Type']
         self.name    = obj.properties['Ability Name']
         self.rules   = obj.properties['Rules']
         
   def __str__(self):
      return self.ability