# Python Scripts for the Card Fighters' Clash definition for OCTGN
# Based in the Python Scripts for the Doomtown CCG definition for OCTGN, by Konstantine Thoukydides
# Copyright (C) 2013  Raohmaru

# This python script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.


#---------------------------------------------------------------------------
# Button
#---------------------------------------------------------------------------

def buttonAction(btn):
   if btn._id in buttons:
      if buttons[btn._id] == 'BlockDone':
         nextPhase()
      
      
def addButton(name):
   cards = queryCard({"Name": name}, True)
   if cards:
      x = CardsCoords['Button'][0] * playerSide - _extapi.game.CardSizes["button"].Width/2
      y = fixCardY(CardsCoords['Button'][1])
      btn = table.create(cards[0], x, y, quantity=1, persist=False)
      btn.anchor = True
      buttons[btn._id] = btn.Name
      # Removes the model so the button image is not shown in the preview
      icard = _extapi.getCardIdentityById(btn._id)
      if icard:
         update()
         icard.Model = None
      
      
def removeButton(name):
   id = None
   for key, v in buttons.iteritems():
      if name == v:
         id = key
         break
   if id:
      for c in table:
         if c._id == id:
            del buttons[id]
            c.delete()
            break
         