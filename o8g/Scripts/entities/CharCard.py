# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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
# CharCard class
#---------------------------------------------------------------------------

class CharCard(GameCard):
   """ A class which stores the character card ability name and its parsed rule scripts """
   ability = None
   
   def __init__(self, card, ruleId = None):
      super(self.__class__, self).__init__(card, ruleId)
      
      self.state["lastBP"] = self.BP
      ability = Ability(card, ruleId = ruleId)
      if ability.name:
         debug("Found ability {}", ability)
         self.ability = ability
      else:
         debug("No ability found")
         
   def hasEffect(self):
      return self.ability != None

   @property
   def BP(self):
      _BP = getMarker(self.card, 'BP')
      if _BP == 0 and self.card.group != table:
         # Even though card property BP is of type Integer, OCTGN returns a String
         _BP = self.card.BP
      return _BP
