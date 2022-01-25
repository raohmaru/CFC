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
   settings["WinForms"] = False


class CustomForm(Form):   
   """
   Base class for custom forms.
   """
   def __init__(self):
      self.bringToFront()
      
   def bringToFront(self):
      """
      Try to display the message box as the top-most window.
      """
      self.TopMost = True
      self.BringToFront()
	  
   def measureString(self, str, width):
      """
      Return the size of the string when drawn with the specified Font for a fixed width.
      """
      form = Form()
      g = form.CreateGraphics()
      # System.Drawing.SizeF
      size = g.MeasureString(str, form.Font, width).ToSize()
      g.Dispose()
      form.Dispose()
      return size

   def stringEscape(self, str):
      """
      Escapes some characters that are otherwise not displayed by WinForms, like "&".
      """
      return str.replace("&", "&&")
   

class MessageBoxForm(CustomForm):
   """
   This is a WinForm which creates a simple window, with some text and an OK button to close it.
   """
   MinWidth = 250
   MaxWidth = 400
   TextPadding = 20

   def __init__(self, msg, title, icon = None):
      super(self.__class__, self).__init__()
   
      labelPanel = Panel()
      buttonPanel = FlowLayoutPanel()
	  
      # Suppress multiple Layout events while adjusting attributes of the controls
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
      
      formSize = self.measureString(msg, self.MaxWidth + self.TextPadding * 2)
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
   debug(">>> messageBox({}, {})", title, icon)
   if settings["WinForms"]:
      # Enables the colors, fonts, and other visual elements that form an operating system theme
      Application.EnableVisualStyles()
      # Replace the card ID with the card name
      msg = replIdsWithNames(msg)
      debug(msg)
      form = MessageBoxForm(msg, title, icon)
      playSnd("win-{}".format(type), True)
      showWinForm(form)
   else:
      if type == "error":
         _extapi.warning(msg)
      elif type == "warning":
         _extapi.whisper(msg, Colors.Red)
      else:
         whisper(msg)
   

def information(msg, title = "Information"):
   messageBox("info", msg, title, SystemIcons.Information)


def warning(msg, title = "Warning"):
   messageBox("warning", msg, title, SystemIcons.Warning)


def error(msg, title = "Error"):
   messageBox("error", msg, title, SystemIcons.Error)


def notification(msg, color = Colors.Black, playerList = None):
   """
   Shows the notification bar for the given players.
   """
   if playerList:
      for player in playerList:
         remoteCall(player, "notification", [msg, color])
   else:
      # Right padding to push outside the window the previous message
      notifyBar(color, msg + " " * 2000)


#---------------------------------------------------------------------------
# Overrides
#---------------------------------------------------------------------------

_confirm_ = confirm
def confirm(str):
   playSnd("win-confirm", True)
   return _confirm_(str)


_askChoice_ = askChoice
def askChoice(question, choices = [], colors = [], customButtons = []):
   playSnd("win-ask-2", True)
   return _askChoice_(question, choices, colors, customButtons)


_remoteCall_ = remoteCall
def remoteCall(player, func, args):
	mute()
	_remoteCall_(player, func, args)