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
# String functions
#---------------------------------------------------------------------------

def fromWhereStr(group, srcPlayer = me):
   """
   Returns a textual representation of the player's group from where an effect takes place.
   """
   if group == table:
      return "from the ring"
   else:
      ctrl = "its"
      # If the source of the effect is not the current player, then the name of the current player
      # is used to avoid confusion in the log
      if group.controller == me and srcPlayer != me:
         ctrl = "{}'s".format(me)
      elif srcPlayer != me:
         ctrl = "{}'s".format(srcPlayer)
      elif group.controller != me:
         ctrl = "{}'s".format(group.controller)
      # Gets the current ongoing effect
      effect = getTempVar("effect")
      if effect and effect[2] and effect[2]["pick"] is not None and effect[2]["pick"] < 0:
         ctrl = "the bottom of " + ctrl
         
      return "from {} {}".format(ctrl, group.name)

   
def sanitizeStr(str):
   """
   Strips the string, replaces spaces with dashes and removes characters not in [a-z0-9\-].
   """
   valid_chars = "-abcdefghijklmnopqrstuvwxyz0123456789"
   str = str.strip().lower().replace(" ", "-")
   str = "".join(c for c in str if c in valid_chars)
   return str
   

def pluralize(num):
   if num == 1:
      return ""
   return "s"
   

def cardsAsNamesListStr(cards):
   """
   Returns a string with the names of the cards separated by commas.
   """
   if not cards:
      return ""
   if len(cards) == 1:
      return "{}".format(cards[0])
   arr = list(cards[:-1])
   str = ("{}, " * len(arr)).format(*arr)[:-2]
   str += " and {}".format(cards[-1])
   return str
      

def replIdsWithNames(string):
   """
   Replaces a card ID in the given string (e.g. {#66526}) with the card name, to be used in forms.
   """
   return re.sub(Regexps["cardid"], lambda match: Card(int(match.group(1))).Name, string)
   
   
def stringify(obj):
   """
   Converts an object into a string representation prefixed by its type.
   """
   if isCard(obj):
      return "{c}" + str(obj._id)
   elif isPlayer(obj):
      return "{p}" + str(obj._id)
   else:
      return obj


def objectify(value):
   """
   Converts a formated string into an object.
   """
   if isinstance(value, basestring):
      if value[:3] == "{c}":
         return Card(int(value[3:]))
      elif value[:3] == "{p}":
         return Player(int(value[3:]))
   return value
   
      
def getTextualRestr(restr):
   """
   Gets an human readable string of the given restriction.
   """
   if not restr:
      return ""
   if restr[1] in MSG_RESTR_LABELS:
      player = me
      if restr[0] == RS_PREFIX_OPP:
         player = getOpp()
      return " " + MSG_RESTR_LABELS[restr[1]].format(player)
   return restr(1)
   
   
def expandAbbr(abbr):
   return ABBR[abbr] if abbr in ABBR else abbr