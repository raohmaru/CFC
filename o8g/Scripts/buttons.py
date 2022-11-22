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

# Get the size from the game definition
ButtonSize = _extapi.game.CardSizes["button"].Width

def buttonAction(btn):
   if btn._id in buttons:
      if buttons[btn._id] == Buttons[StartButton]:
         if len(me.Deck) == 0:
            warning(MSG_ACTION_LOAD_DECK)
            return
         if not me.setupDone:
            setup()
         me.setActive()
         track_event("click", StartButton)
         
      elif buttons[btn._id] == Buttons[NextButton]:
         nextPhase(True)

      
def addButton(name):
   mute()
   if name in buttons.values():
      return
   model = Buttons[name]
   x = CardsCoords[name][0] * me.side - ButtonSize/2
   y = fixCardY(CardsCoords[name][1], ButtonSize)
   btn = table.create(model, x, y, quantity = 1, persist = False)
   # Nail it to the table thus preventing players from manually moving it
   btn.anchor = True
   buttons[btn._id] = model
   # Change alternate to show a more descriptive name
   btn.alternate = "alt"
      
      
def removeButton(name):
   mute()
   model = Buttons[name]
   ids = []
   for key, v in buttons.iteritems():
      if model == v:
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
