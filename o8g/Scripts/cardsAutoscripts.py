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

import re

#---------------------------------------------------------------------------
# Card automation functions
#---------------------------------------------------------------------------

def parseCard(card, ruleId=None, init=True):
   debug(">>> parseCard({})".format(card)) #Debug
   if not card._id in parsedCards:
      if isCharacter(card):
         parsedCards[card._id] = CharCard(card, ruleId)
      else:
         parsedCards[card._id] = GameCard(card, ruleId)
      if init:
         parsedCards[card._id].init()
   return parsedCards.get(card._id)
   

def getParsedCard(card):
   debug("Retrieved parsed card for ID {} ({})".format(card._id, card))
   return parseCard(card, init=False)
   

def removeParsedCard(card):
   debug("Removed parsed card for ID {} ({})".format(card._id, card))
   parsedCards.pop(card._id, None)
   removeGameEventListener(card._id)


class GameCard(object):
   """ A class which stores the card effect name and its parsed rule scripts """
   card_id = None
   rule_id = None
   rules   = None
   
   def __init__(self, card, ruleId=None):
      debug(">>> GameCard()") #Debug
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


class CharCard(GameCard):
   """ A class which stores the character card ability name and its parsed rule scripts """
   ability = None
   
   def __init__(self, card, ruleId=None):
      super(self.__class__, self).__init__(card, ruleId)
      debug(">>> CharCard()") #Debug
   
      ability = Ability(card)
      if ability.name:
         debug("Found ability {}".format(ability))
         self.ability = ability
      else:
         debug("No ability found")
         
   def hasEffect(self):
      return self.ability != None
      

class Ability:
   """ A class that represents an ability """   
   ability = ""
   type    = ""
   name    = ""
   
   @property
   def unicodeChar(self):
      # Returns a unicode symbol for the type (for window forms)
      if self.type == InstantAbility:   return InstantUniChar
      if self.type == ActivatedAbility: return ActivatedUniChar
      if self.type == AutoAbility:      return AutoUniChar
      return ""
   
   def __init__(self, obj, rules = None):
      if isinstance(obj, basestring):
         ability = Regexps['Ability'].match(obj)
         if ability:
            self.ability = ability.group(0)
            self.type    = ability.group(1)
            self.name    = ability.group(2)
            self.rules   = rules
      elif obj.Ability:
         self.ability = obj.Ability
         self.type    = obj.properties['Ability Type']
         self.name    = obj.properties['Ability Name']
         self.rules   = obj.properties['Rules']
         
   def __str__(self):
      return self.ability