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

def getParsedCard(card):
   debug(">>> getParsedCard()") #Debug
   if not card._id in cards:
      if card.Type == 'Character':
         cards[card._id] = CharCard(card)
      else:
         cards[card._id] = GameCard(card)
   debug("Retrieved parsed card for card {} ({})".format(card._id, card.Name))
   return cards.get(card._id)


class GameCard(object):
   """ A class which stores the card effect name and its parsed rule scripts """   
   rule_id = None
   rules   = None
   
   def __init__(self, card):
      debug(">>> GameCard()") #Debug
      self.rule_id = card.model

         
   def hasEffect(self):
      return True

      
   def activateEffect(self):
      if not self.hasEffect():
         return
      if self.rules == None:
         self.rules = Rules(self.rule_id)
      self.rules.activate()


class CharCard(GameCard):
   """ A class which stores the character card ability name and its parsed rule scripts """   
   
   def __init__(self, card):
      super(self.__class__, self).__init__(card)
      debug(">>> CharCard()") #Debug
   
      ability = Regexps['Ability'].match(card.Rules)
      if ability:
         debug("Found ability {}".format(ability.group(0)))  # Causes weird IronPython error
         self.ability = ability.group(0)
         self.ability_type = ability.group(1)
         self.ability_name = ability.group(2)
      else:
         debug("No ability found")

         
   def hasEffect(self):
      if self.ability != None:
         return True
      return False