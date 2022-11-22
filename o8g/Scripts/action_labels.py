# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Copyright (C) 2013 Raohmaru

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
# Functions that alter the label name of an action from the contextual menu
#---------------------------------------------------------------------------

def aclb_Freeze(args, x = 0, y = 0):
   card = args[0]
   if isFrozen(card):
      return "Unfreeze"
   else:
      return "Freeze"


def aclb_Default(args, x = 0, y = 0):
   card = args[0]
   phaseIdx = getCurrentPhase()
   if isCharacter(card):
      if me.isActive and phaseIdx == AttackPhase:
         if isAttacking(card):
            return "Remove from attack"
         else:
            return "Attack"

      if (not me.isActive or tutorial) and phaseIdx == BlockPhase:
         if isBlocking(card):
            return "Remove from combat"
         else:
            return "Counter-attack"

      return "Use ability"

   elif isButton(card):
      return "Activate"
   elif isAvatar(card):
      return "Change avatar"
   else:
      return "Resolve"


def aclb_ChangeSlot(args, x = 0, y = 0):
   card = args[0]
   targets = getTargetedCardsFrom(card, True, card.controller == me)
   if len(targets) > 0:
      return "Swap slot"
   else:
      return "Change slot"


def aclb_Ability(args, x = 0, y = 0):
   card = args[0]
   if card.alternate == "noability":
      return "Restore abilities"
   else:
      return "Lose abilities"


def aclb_Destroy(args, x = 0, y = 0):
   card = args[0]
   if isCharacter(card):
      return "KO"
   else:
      return "Discard"


def aclb_RevealTopDeck(group, x = 0, y = 0):
   if len(group) > 0:
      if group[0].isFaceUp:
         return "Hide top card"
      else:
         return "Reveal top card"
         return "Discard"


def aclb_PlayAuto(group, x = 0, y = 0):
   return aclb_setting("Play automation", "PlayAuto")


def aclb_PhaseAuto(group, x = 0, y = 0):
   return aclb_setting("Phase auto advance", "PhaseAuto")


def aclb_ActivateAuto(group, x = 0, y = 0):
   return aclb_setting(u"Activate {} abilities and effects".format(InstantUniChar), "Activate")


def aclb_WinForms(group, x = 0, y = 0):
   return aclb_setting("Show alert messages", "WinForms")


def aclb_Sounds(group, x = 0, y = 0):
   return aclb_setting("Game sounds", "Sounds")


def aclb_WelcomeScreen(group, x = 0, y = 0):
   return aclb_setting("Show welcome screen on start", "WelcomeScreen")


def aclb_NextOrPass(group, x = 0, y = 0):
   if me.isActive:
      return "Next phase"
   else:
      return "Pass"


def aclb_unitedAttack(group, x = 0, y = 0):
   if getGlobalVar("UnitedAttack"):
      return "Join United Attack"
   else:
      return "United Attack"


def aclb_RemovedDefault(group, x = 0, y = 0):
   if me.isActive and getCurrentPhase() == MainPhase and getRule("play_removed"):
      return "Play card"


def aclb_SetupOrStart(group, x = 0, y = 0):
   if me.setupDone:
      return "Start game"


#---------------------------------------------------------------------------
# Helpers
#---------------------------------------------------------------------------

def aclb_setting(label, setting):
   return "{}{}".format(u"\u2714 " if settings[setting] else u" \u2002 \u2002 ", label)