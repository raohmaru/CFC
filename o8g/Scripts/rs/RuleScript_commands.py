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
   def applyAll(cmds, targets, restr, source):
      for cmd in cmds:
         RulesCommands.applyCmd(cmd, targets, restr, source)
   
   
   @staticmethod
   def applyCmd(cmd, targets, restr, source):
      funcStr = cmd[0]
      params = cmd[1]
      if funcStr in RulesCommands.cmds:
         debug("-- applying cmd '%s' to targets %s (%s)" % (funcStr, targets, restr))
         # func = RulesCommands.cmds[funcStr]
         func = eval(RulesCommands.cmds[funcStr])  # eval is a necessary evil...
         func(targets, restr, source, *params)
      else:
         debug("-- cmd not found: %s".format(cmd[0]))
      

#---------------------------------------------------------------------------
# Commands functions
#---------------------------------------------------------------------------

def cmdDamage(targets, restr, source, *args):
   debug(">>> cmdDamage({}, {}, {})".format(targets, restr, args)) #Debug      
   # Get additional parameters
   try:
      dmg = int(args[0])
   except:
      return False
   for target in targets:
      dealDamage(dmg, target, source)


RulesCommands.register('damage', 'cmdDamage')