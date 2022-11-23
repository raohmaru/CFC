# Python Scripts for the Card Fighters" Clash definition for OCTGN
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
# Manages UI elements
#---------------------------------------------------------------------------
      
class ui():
   """
   Class to handle the UI cards.
   """
   StatusWidth = _extapi.game.CardSizes["status"].Width
   StatusHeight = _extapi.game.CardSizes["status"].Height
   ActivePlayerModel = "8ca520da-0985-4480-a94b-5b968aebc482"
   activePlayerCard = None

   @staticmethod
   def setActivePlayer():
      """
      Player status visual hint.
      """
      for c in getCards(includeUI = True):
         if c.model == ui.ActivePlayerModel:
            return
      x = CardsCoords["Status"][0] * me.side - ui.StatusWidth/2
      y = fixCardY(CardsCoords["Status"][1], ui.StatusHeight)         
      ui.activePlayerCard = table.create(ui.ActivePlayerModel, x, y, quantity = 1, persist = False)
      # Wait before sending the card to the back, or it will be on top of the avatar
      waitForAnimation()
      ui.activePlayerCard.sendToBack()
      ui.activePlayerCard.anchor = True

   @staticmethod
   def clearActivePlayer():
      if ui.activePlayerCard is not None:
         ui.activePlayerCard.delete()
         ui.activePlayerCard = None