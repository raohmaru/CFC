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


import time 

#---------------------------------------------------------------------------
# Sound interface
#---------------------------------------------------------------------------

soundsPlayings = {}

def playSnd(name, isInternal=False):
   if name in soundsPlayings:
      if time.time() - soundsPlayings[name] < 0.3: # in seconds
         return   
   soundsPlayings[name] = time.time()

   if (
      isInternal
      or debugging
      or (me.name == Author and getOpp().name == 'dand')
      or (me.name == 'dand' and getOpp().name == Author)
   ):
      try:
         sound = Octgn.Program.GameEngine.Definition.Sounds[name]
         Octgn.Utils.Sounds.PlayGameSound(sound)
      except KeyError:
         debug("Sound {} does not exist".format(name))
   else:
      playSound(name)