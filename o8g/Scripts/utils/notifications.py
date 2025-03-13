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

import re

#---------------------------------------------------------------------------
# Notifications functions
#---------------------------------------------------------------------------

def notifyWinner(player):
   """
   Notifies to all player who is the winner of the game.
   """
   msg = MSG_HINT_WIN.format(player).upper()
   _extapi.notify(msg, Colors.Orange, True)
   if not debugging:
      notification(msg, playerList = players)
   track_event("game_end", Octgn.Play.Player.LocalPlayer.Name)
   

def notifyAbility(target_id, source_id = None, msg = None, restr = "", isWarning = False):
   """
   Shows a notification related to a card ability.
   """
   obj = getPlayerOrCard(target_id)
   source = obj
   if source_id is not None:
      source = Card(source_id)
   if msg is not None:
      func = warning if isWarning else notify
      name = obj
      if isPlayer(obj) or isWarning:
         if isPlayer(obj) and isWarning:
            name = "You"
         else:
            name = getObjName(obj)
      func(msg.format(name, source.Name, source.properties["Ability Name"], restr))


def askForEmptySlot(player = me):
   ring = getGlobalVar("Ring", player)
   if ring.count(None) == 0:
      warning(MSG_ERR_NO_EMPTY_SLOTS)
      return -1
   # Prompt the player to select an empty slot
   slots = []
   for i, id in enumerate(ring):
      if id == None:
         slots.append(str(i + 1))
   # Don't ask if only one slot is empty
   if len(slots) == 1:
      return int(slots[0]) - 1
   slotIdx = askChoice("Select an empty slot in your ring:", slots)
   debug("Selected option {} ({})", slotIdx, slotIdx - 1)
   if slotIdx == 0:
      return -1
   return int(slots[slotIdx - 1]) - 1