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
# Commands class
#---------------------------------------------------------------------------

class RulesCommands():
   """ Class to handle the filters that are applied to a set of objects """
   cmds = {}

   @staticmethod
   def register(name, cmd):
      RulesCommands.cmds[name] = cmd
      
   
   @staticmethod
   def applyAll(cmds, targets, restr, source, inverse=False):
      for cmd in cmds:
         RulesCommands.applyCmd(cmd, targets, restr, source, inverse)
   
   
   @staticmethod
   def applyCmd(cmd, targets, restr, source, inverse=False):
      debug(">>> applyCmd({}, {}, {}, {}, {})".format(cmd, targets, restr, source, inverse)) #Debug    
      funcStr = cmd[0]
      params = cmd[1]
      # Executing command functions
      if funcStr in RulesCommands.cmds and not inverse:
         debug("-- applying cmd '%s' to targets %s (%s)" % (funcStr, targets, restr))
         # func = RulesCommands.cmds[funcStr]
         func = eval(RulesCommands.cmds[funcStr])  # eval is a necessary evil...
         func(targets, restr, source, *params)
      # Abilities/bonus manipulation
      elif funcStr in RS_PREFIX_BONUS:
         for target in targets:
            if funcStr == RS_PREFIX_PLUS:
               if inverse:
                  RulesAbilities.remove(params, target._id)
               else:
                  RulesAbilities.add(params, target._id, source._id, restr)
      else:
         debug("-- cmd not found: {}".format(cmd[0]))
      

#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmd_damage(targets, restr, source, *args):
   debug(">>> cmd_damage({}, {}, {})".format(targets, restr, args)) #Debug      
   # Get additional parameters
   try:
      dmg = int(args[0])
   except:
      return False
   for target in targets:
      dealDamage(dmg, target, source)

      
def cmd_swapPiles(targets, restr, source, pile1, pile2):
   debug(">>> cmd_swapPiles({}, {}, {})".format(source, pile1, pile2)) #Debug
   pile1 = RulesUtils.getZoneByName(pile1)
   pile2 = RulesUtils.getZoneByName(pile2)
   swapPiles(pile1, pile2)

      
def cmd_shuffle(targets, restr, source, pile):
   if not pile:
      pile = me.Deck
   debug(">>> cmd_shuffle({})".format(pile)) #Debug
   shuffle(pile)


RulesCommands.register('damage',    'cmd_damage')
RulesCommands.register('swappiles', 'cmd_swapPiles')
RulesCommands.register('shuffle',   'cmd_shuffle')