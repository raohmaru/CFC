# Python Scripts for the Card Fighters" Clash definition for OCTGN
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
# Helpers
#---------------------------------------------------------------------------

def isNumber(s):
   if not s or isinstance(s, bool):
      return False
   try:
      float(s)
      return True
   except ValueError:
      return False
        

def isPlayer(obj):
   return isinstance(obj, Player)


def isCard(obj):
   return isinstance(obj, Card)


def isCharacter(card):
   return card.Type == CharType


def isAction(card):
   return card.Type == ActionType


def isReaction(card):
   return card.Type == ReactionType


def isButton(card):
   return card.Type == ButtonType


def isAvatar(card):
   return card.Type == AvatarType


def isUI(card):
   return card.Type in [ButtonType, AvatarType]


def isAttached(card):
   backups = getGlobalVar("Backups")
   return bool(backups.get(card._id))
   
   
def isFrozen(card):
   return card.orientation & Rot90 == Rot90


def isAttacking(card, inUA = True):
   return hasMarker(card, "Attack") or inUA and hasMarker(card, "United Attack")


def isBlocking(card):
   return hasMarker(card, "Counter-attack")


def inUAttack(card):
   uattack = getGlobalVar("UnitedAttack")
   if len(uattack) > 0 and card._id in uattack:
      return True
   return False


def isVisible(card):
   if not card.isFaceUp or card.group.name == "Hand":
      return False
   return True


def isCharInRing(card, player = me):
   ring = getGlobalVar("Ring", player)
   return card._id in ring


def hasFilter(card, filter):
   # card.filter does not have the alpha value (#AARRGGB => #RRGGBB)
   return card.filter and card.filter[1:] == filter[3:]


def canBackup(card):
   # Char just entered the ring?
   if hasMarker(card, "Just Entered") and not getRule("backup_fresh"):
      warning("Characters that just entered the ring this turn can't be backed-up.")
      return
   # Backup limit
   backupsPlayed = getState(me, "backupsPlayed")
   if backupsPlayed >= BackupsPerTurn:
      if getRule("backup_limit") and triggerHook(Hooks.BackupLimit, card._id) != False:
         warning("You can't backup more than {} character per turn.".format(BackupsPerTurn))
         return
   return True