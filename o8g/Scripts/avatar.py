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
# Avatar
#---------------------------------------------------------------------------

# Get the dimensions from the game definition
AvatarWidth  = _extapi.game.CardSizes["avatar"].Width
AvatarHeight = _extapi.game.CardSizes["avatar"].Height

def avatarAction(card):
   model, qty = askCard({"Type": AvatarType}, title = "Choose your avatar image")
   if qty > 0:
      setAvatar(model)
      notify("{} changes his avatar image.", me)


def setAvatar(model = None):
   mute()
   if not model:
      if settings["Avatar"]:
         model = settings["Avatar"]
      if not model:
         cards = queryCard({"Type": AvatarType}, True)
         model = cards[random.randInt(0, len(cards)-1)]
   if model:
      oldAvatar = getAvatar(me)
      if oldAvatar:
         oldAvatar.delete()
      x = CardsCoords["Avatar"][0] * p1.side - AvatarWidth/2
      y = fixCardY(CardsCoords["Avatar"][1], AvatarHeight)         
      avatar = table.create(model, x, y, quantity = 1, persist = False)
      # Nail it to the table thus preventing players from manually moving it
      avatar.anchor = True
      # Change the name of the current alternate to show a descriptive text
      _extapi.getCardDataById(avatar._id).PropertySets[""].Name = "Double click to change avatar"
      if avatar.Name != settings["Avatar"]:
         switchSetting("Avatar", model)


def getAvatar(player):
   cards = [c for c in table
            if c.controller == player
            and isAvatar(c)]
   if cards:
      return cards[0]