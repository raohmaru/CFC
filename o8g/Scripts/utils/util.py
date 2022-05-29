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
# General functions
#---------------------------------------------------------------------------

def num(s):
   if not s:
      return 0
   try:
      return int(s)
   except ValueError:
      return 0


def toBase(n, base, D = "0123456789abcdefghijklmnopqrstuvwxyz"):
   """
   Number base converter.
   Returns: string
   <https://stackoverflow.com/questions/47758410/convert-from-decimal-to-any-base-number-in-python>
   """
   return (toBase(n//base,base)+D[n%base]).lstrip("0") if n>0 else "0"


def waitForAnimation():
   """
   Delays the next action until all animation is done.
   https://github.com/octgn/OCTGN/issues/412
   https://github.com/octgn/OCTGN/issues/110
   """
   # rnd() is generated by the server and synch with all players
   rnd(100, 10000)
   # Forces any pending networked tasks to complete before executing next line
   # update()


def funcCall(player, func, args = []):
   """
   Invokes a function for the given player.
   """
   if player == me:
      func(*args)
   else:
      remoteCall(player, func.__name__, args)


def unique(seq):
   """
   Returns a list with values not repeated and the order unmodified.
   """
   seen = set()
   # Because Python is dynamic, accessing variables is faster than attribute lookup
   seen_add = seen.add
   return [x for x in seq if not (x in seen or seen_add(x))]


def getGlobalVar(name, player = None):
   """
   Gets a game global variable or a player global variable.
   """
   if player:
      id = player._id
      if not id in PlayerGlobals:
         PlayerGlobals[id] = {}
      if not name in PlayerGlobals[id]:
         PlayerGlobals[id][name] = eval(player.getGlobalVariable(name))
      # Returns a copy so it cannot be modified
      return eval(str(PlayerGlobals[id][name]))
   else:
      if not name in Globals:
         Globals[name] = eval(getGlobalVariable(name))
      # Returns a copy so it cannot be modified
      return eval(str(Globals[name]))


def setGlobalVar(name, value, player = None):
   """
   Sets a game global variable or a player global variable.
   """
   gvar = getGlobalVar(name, player)
   if player:
      PlayerGlobals[player._id][name] = value
   else:
      Globals[name] = value
   if len(players) > 1:
      # Changes in a list variable that contains dicts
      if isinstance(gvar, list):
         if len(gvar) > 0 and isinstance(gvar[0], dict) or len(value) > 0 and isinstance(value[0], dict):
            remov = [v for v in gvar if v not in value]
            added = [v for v in value if v not in gvar]
            value = (remov, added)
      # Changes in a dict variable
      elif isinstance(gvar, dict):
         diff = set(gvar) ^ set(value)
         remov = [k for k in diff if k not in value]
         added = [{k:value[k]} for k in diff if k not in gvar]
         # Possible updated fields
         diff = set(gvar) & set(value)
         added += [{k:value[k]} for k in diff if gvar[k] != value[k]]
         value = (remov, added)
      # 0 is the fake player of the tutorial
      if players[1]._id != 0:
         remoteCall(players[1], "updateSharedGlobals", [name, value, player])


def clearGlobalVar(name, player = None):
   gvar = getGlobalVar(name, player)
   if isinstance(gvar, list):
      del gvar[:]  # Clear list
   elif isinstance(gvar, dict):
      gvar.clear()
   elif isinstance(gvar, basestring):
      gvar = ''
   elif isinstance(gvar, (int, long)):
      gvar = 0
   setGlobalVar(name, gvar, player)
         
         
def updateSharedGlobals(name, value, player = None):
   """
   Replacement for OCTGN global variables, because when simultaneous requests are sent from different players to update a
   global variable, the server does not merge the data and keeps only the last updated version.
   """
   # Merge current variable with the changes from the other player
   if isinstance(value, tuple):
      remov, added = value
      gvar = getGlobalVar(name, player)
      # list
      if isinstance(gvar, list):
         gvar = [v for v in gvar if v not in remov]
         value = gvar + added
      # dict
      elif isinstance(gvar, dict):
         for k in remov:
            del gvar[k]
         for d in added:
            gvar.update(d)
         value = gvar
   if player:
      if not player._id in PlayerGlobals:
         PlayerGlobals[player._id] = {}
      PlayerGlobals[player._id][name] = value
   else:
      Globals[name] = value
