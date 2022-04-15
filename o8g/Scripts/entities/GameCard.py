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
# GameCard class
#---------------------------------------------------------------------------

class GameCard(object):
   """
   A class which stores the card effect name and its parsed rule scripts.
   """
   
   def __init__(self, card, ruleId = None):
      self.card = card
      self.card_id = card._id
      self.rule_id = ruleId if ruleId else card.model
      self.rules = Rules(self.rule_id, self.card_id)
      self.state = {
         "willHighlight": True,
         "lastBP": NaN,
         "joiningUA": False
      }
      
   def init(self, forceActivateAuto = False):
      if self.hasEffect():
         self.rules.init(forceActivateAuto)
         
   def hasEffect(self):
      return True
      
   def activateEffect(self):
      if not self.hasEffect():
         return
      return self.rules.activate()
      
   def getState(self, name):
      if name in self.state:
         return self.state[name]
      
   def setState(self, name, value):
      debug(">>> GameCard.setState({}, {}, {})", self.card, name, value)
      self.state[name] = value
      debug(self.state)
      
   def destroy(self):
      debug(">>> Delete GameCard {}", self.card)
      del self.card
      self.rules.dispose()
      del self.rules
      
   @property
   def BP(self):
      return NaN  # Compared to a number will return always False
