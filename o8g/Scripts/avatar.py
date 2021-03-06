# Python Scripts for the Card Fighters' Clash definition for OCTGN
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
# Avatar
#---------------------------------------------------------------------------

def avatarAction(card):
   model, qty = askCard({'Type': AvatarType}, title = 'Choose your avatar image')
   if qty > 0:
      addAvatar(model)
      
      
def addAvatar(model = None):
   mute()
   if not model:
      if settings['Avatar']:
         cards = queryCard({'name': settings['Avatar']}, True)
         if cards:
            model = cards[0]
      if not model:
         cards = queryCard({'Type': AvatarType}, True)
         model = cards[random.randint(0, len(cards)-1)]
   if model:
      oldAvatar = getAvatar(me)
      if oldAvatar:
         oldAvatar.delete()
         
      x = CardsCoords['Avatar'][0] * playerSide - AvatarWidth/2
      y = fixCardY(CardsCoords['Avatar'][1], AvatarHeight)         
      avatar = table.create(model, x, y, quantity=1, persist=False)
      avatar.anchor = True
      if avatar.Name != settings['Avatar']:
         switchSetting('Avatar', avatar.Name)


def getAvatar(player):
   cards = [c for c in table
            if c.controller == player
            and isAvatar(c)]
   if cards:
      return cards[0]