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
# Ability class
#---------------------------------------------------------------------------

class Ability:
   """
   A class that represents an ability or an effect of a card.
   """
   __slots__ = ("ability", "type", "name", "rules")
   # Class (static) variables, which are also the default values for each instance
   ability = ""
   type    = ""
   name    = ""
   rules   = ""
   
   def __init__(self, obj, rules = None, ruleId = None):
      # Ability can be defined from a string...
      if isinstance(obj, basestring):
         ability = Regexps["ability"].match(obj)
         if ability:
            self.ability = ability.group(0)
            self.type    = ability.group(1)
            self.name    = ability.group(2)
            self.rules   = rules
      # ... a card model
      elif ruleId:
         cardData  = _extapi.getCardDataByModel(ruleId)
         cardProps = _extapi.getCardProperties(cardData)
         self.ability = cardProps["Ability"]
         self.type    = cardProps["Ability Type"]
         self.name    = cardProps["Ability Name"]
         self.rules   = cardProps["Rules"]
      # ... or a card-like object
      elif obj.Ability:
         self.ability = obj.Ability
         self.type    = obj.properties["Ability Type"]
         self.name    = obj.properties["Ability Name"]
         self.rules   = obj.properties["Rules"]
   
   @property
   def unicodeChar(self):
      # Returns a Unicode symbol for the type (for window forms)
      if self.type == InstantAbility: return InstantUniChar
      if self.type == TriggerAbility: return TriggerUniChar
      if self.type == AutoAbility   : return AutoUniChar
      return ""
         
   def __str__(self):
      return self.ability