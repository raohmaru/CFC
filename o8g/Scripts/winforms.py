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

import re

try:
   import os
   if os.environ['RUNNING_TEST_SUITE'] == 'TRUE':
      from meta import automations
      Form = object
except ImportError:
   pass

#---------------------------------------------------------------------------
# Custom Windows Forms
#---------------------------------------------------------------------------

try:
   import clr
   clr.AddReference("System.Windows.Forms")
   from System.Windows.Forms import *
except:
   automations['WinForms'] = False

def messageBox(msg, title, icon):
   debugNotify(">>> messageBox() with message: {}".format(msg))
   if automations['WinForms']:
      Application.EnableVisualStyles()
      # Trying to display the message box as the top-most window 
      form = Form()
      form.TopMost = True
      form.BringToFront()
      MessageBox.Show(msg, title, MessageBoxButtons.OK, icon)
      form.Close()
   else: 
      whisper(msg)

def information(msg, title = 'Information'):
   messageBox(msg, title, MessageBoxIcon.Information);

def warning(msg, title = 'Warning'):
   messageBox(msg, title, MessageBoxIcon.Warning);

def error(msg, title = 'Error'):
   messageBox(msg, title, MessageBoxIcon.Error);