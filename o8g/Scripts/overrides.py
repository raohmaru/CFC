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
# Overrides
#---------------------------------------------------------------------------

# Shows a custom confirmation box or the default one
_confirm_ = confirm
def confirm(msg, settingID = None):
   playSnd("win-confirm", True)
   if settingID and settings["WinForms"]:
      # Remember last choice (True: do not show again)
      if settingID in settings["DoNotShow"] and settings["DoNotShow"][settingID] == True:
         return True
      # Custom form with a checkbox
      form = ConfirmForm(msg, "Confirmation", settingID)
      return form.show()
   return _confirm_(msg)


# Add a nice sound effect
_askChoice_ = askChoice
def askChoice(question, choices = [], colors = [], customButtons = []):
   playSnd("win-ask-2", True)
   return _askChoice_(question, choices, colors, customButtons)


# Hides messages
_remoteCall_ = remoteCall
def remoteCall(player, func, args):
   mute()
   _remoteCall_(player, func, args)


# Apply automatic format from the extra arguments
_notify_ = notify
def notify(msg, *args):
   if len(args) > 0:
      msg = msg.format(*args)
   _notify_(msg)
