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
# Custom Windows Forms
#---------------------------------------------------------------------------

try:
   import clr
   clr.AddReference("System.Drawing")
   clr.AddReference("System.Windows.Forms")

   from System.Windows.Forms import *
   from System.Drawing import *
except (IOError, ImportError):
   settings['WinForms'] = False


# Base class for custom forms
class CustomForm(Form):   
   def __init__(self):
      self.bringToFront()
      
   # Try to display the message box as the top-most window 
   def bringToFront(self):
      self.TopMost = True
      self.BringToFront()
	  
   # Return the size of the string when drawn with the specified Font for a fixed width
   def calcStringSize(self, str, width):
      form = Form()
      g = form.CreateGraphics()
      size = g.MeasureString(str, form.Font, width).ToSize()
      g.Dispose()
      form.Dispose()
      return size

   # Escapes some characters that are not otherwise displayed by WinForms, like '&'
   def stringEscape(self, str):
      return str.replace('&', '&&')
   

# This is a WinForm which creates a simple window, with some text and an OK button to close it.
class MessageBoxForm(CustomForm):
   MinWidth = 250
   MaxWidth = 400
   TextPadding = 20

   def __init__(self, msg, title, icon = None):
      super(self.__class__, self).__init__()
   
      labelPanel = Panel()
      buttonPanel = FlowLayoutPanel()
	  
      labelPanel.SuspendLayout()
      buttonPanel.SuspendLayout()
      self.SuspendLayout()
      
      label = Label()
      label.Text = self.stringEscape(msg)
      label.Location = Point(0, 0)
      label.Dock = DockStyle.Fill
      label.Padding = Padding(self.TextPadding)
			
      labelPanel.Dock = DockStyle.Fill
      labelPanel.BackColor = Color.White
      labelPanel.Controls.Add(label)
			
      button = Button()
      button.Text = "OK"
      button.Click += self.button_Click
	  
      buttonPanel.Dock = DockStyle.Bottom
      buttonPanel.FlowDirection = FlowDirection.RightToLeft
      buttonPanel.AutoSize = True;
      buttonPanel.Padding = Padding(5)
      buttonPanel.Controls.Add(button)
      
      formSize = self.calcStringSize(msg, self.MaxWidth + self.TextPadding * 2)
      self.StartPosition = FormStartPosition.CenterScreen
      self.Text = title
      self.Size = Size(max(self.MinWidth, formSize.Width) + self.TextPadding * 2, formSize.Height + buttonPanel.Size.Height + self.TextPadding * 2)
      self.AutoSize = True
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.Icon = icon
      
      self.Controls.Add(labelPanel)
      self.Controls.Add(buttonPanel)
      
      labelPanel.ResumeLayout(False)
      buttonPanel.ResumeLayout(False)
      self.ResumeLayout(False)

   def button_Click(self, sender, args):
      self.Close()


def messageBox(type, msg, title, icon = None):
   debug(">>> messageBox({}) with message: {}", title, msg)
   if settings['WinForms']:
      Application.EnableVisualStyles()
      # Replace card ID with card name
      msg = replIdsWithNames(msg)
      debug(msg)
      form = MessageBoxForm(msg, title, icon)
      playSnd('win-{}'.format(type), True)
      showWinForm(form)
   else:
      if type == 'error':
         _extapi.warning(msg)
      elif type == 'warning':
         _extapi.whisper(msg, Colors.Red)
      else:
         whisper(msg)
   

def information(msg, title = 'Information'):
   messageBox('info', msg, title, SystemIcons.Information)

def warning(msg, title = 'Warning'):
   messageBox('warning', msg, title, SystemIcons.Warning)

def error(msg, title = 'Error'):
   messageBox('error', msg, title, SystemIcons.Error)
   
def notification(msg, color = '#000000', toAll = False, player = None):
   if player:
      remoteCall(player, "notification", [msg, color])
   elif toAll:
      for p in players:
         remoteCall(p, "notification", [msg, color])
   else:
      notifyBar(color, msg + ' ' * 2000)


#---------------------------------------------------------------------------
# Overrides
#---------------------------------------------------------------------------

def confirm(str):
   playSnd('win-confirm', True)
   return _api.Confirm(str)
   
_askChoice_ = askChoice
def askChoice(question, choices = [], colors = [], customButtons = []):
   playSnd('win-ask-2', True)
   return _askChoice_(question, choices, colors, customButtons)
   

# clr.AddReference('WindowsBase')
# System.Windows.Threading.Dispatcher.CurrentDispatcher.Invoke

# clr.AddReferenceByName("PresentationCore, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
# clr.AddReferenceByName("PresentationFramework, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
# Octgn.Play.Gui.Commands.LoadPrebuiltDeck.Execute({}, System.Windows.ContentElement())

# Octgn.WindowManager.PlayWindow.AddHandler(Octgn.Play.Gui.CardControl.CardHoveredEvent, Octgn.Play.Gui.CardEventHandler(btnHover))
