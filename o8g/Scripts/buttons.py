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
# Button
#---------------------------------------------------------------------------

def buttonAction(btn):
   if btn._id in buttons:
      if buttons[btn._id] == StartButton:
         if len(me.Deck) == 0:
            warning(MSG_ACTION_LOAD_DECK)
            return
         if not setupDone:
            setup()
         me.setActive()
         
      elif buttons[btn._id] == NextButton:
         nextPhase(True)
      
      
def addButton(name):
   mute()
   if name in buttons.values():
      return
   x = CardsCoords[name][0] * playerSide - ButtonSize/2
   y = fixCardY(CardsCoords[name][1], ButtonSize)
   btn = table.create(Buttons[name], x, y, quantity = 1, persist = False)
   # Nail it to the table thus preventing players from manually moving it
   btn.anchor = True
   buttons[btn._id] = btn.Name
   # Removes the model so the button image is not shown in the preview.
   # Unfortunately it loses its type and buttonAction() won't be called
   # icard = _extapi.getCardIdentityById(btn._id)
   # if icard:
      # update()
      # icard.Model = None
      
      
def removeButton(name):
   mute()
   ids = []
   for key, v in buttons.iteritems():
      if name == v:
         ids.append(key)
   if ids:
      for c in table:
         if c._id in ids:
            del buttons[c._id]
            c.delete()


def removeAllButtons():
   """
   Removes all buttons in the game.
   """
   mute()
   for c in table:
      if c._id in buttons:
         del buttons[c._id]
         c.delete()
