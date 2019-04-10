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
# Custom Windows Forms
#---------------------------------------------------------------------------

try:
   import clr
   clr.AddReference("System.Drawing")
   clr.AddReference("System.Windows.Forms")

   from System.Windows.Forms import *
   from System.Drawing import *
except:
   automations['WinForms'] = False


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
   Width = 400
   TextPadding = 20

   def __init__(self, msg, title, icon = None):
      super(self.__class__, self).__init__()
   
      labelPanel = Panel()
      buttonPanel = FlowLayoutPanel()
      # self.pictureBox = PictureBox()
	  
      labelPanel.SuspendLayout()
      buttonPanel.SuspendLayout()
      # self.pictureBox.BeginInit()
      self.SuspendLayout()
	  	  
      formSize = self.calcStringSize(msg, self.Width - self.TextPadding * 2)
      self.StartPosition = FormStartPosition.CenterScreen
      self.Text = title
      self.Size = Size(self.Width, formSize.Height + 130)
      self.AutoSize = True
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.Icon = icon
      
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
      buttonPanel.Size = Size(self.ClientSize.Width, button.Height + 15)
      buttonPanel.Padding = Padding(5)
      buttonPanel.Controls.Add(button)
      
      # self.pictureBox.Location = Point(13, 13)
      # self.pictureBox.Size = Size(self.Icon.Width, self.Icon.Height)
      # self.pictureBox.BackColor = Color.Transparent
      # self.pictureBox.Paint += self.pictureBox_Paint

      # self.Controls.Add(self.pictureBox)
      self.Controls.Add(labelPanel)
      self.Controls.Add(buttonPanel)
      
      labelPanel.ResumeLayout(False)
      buttonPanel.ResumeLayout(False)
      # self.pictureBox.EndInit()
      self.ResumeLayout(False)

   def button_Click(self, sender, args):
      self.Close()

   # Drawing graphics only seems to work on click
   # def pictureBox_Paint(self, e):
      # g = self.pictureBox.CreateGraphics()
      # g.DrawIcon(self.Icon, 0, 0)


def messageBox(msg, title, icon = None):
   debug(">>> messageBox({}) with message: {}".format(title, msg))
   if automations['WinForms']:
      Application.EnableVisualStyles()
      form = MessageBoxForm(msg, title, icon)
      showWinForm(form)
   else:
      if icon == SystemIcons.Warning:
         notifyBar("#FF0000", msg.replace("\n", " "))
      whisper(msg)
   

def information(msg, title = 'Information'):
   messageBox(msg, title, SystemIcons.Information)

def warning(msg, title = 'Warning'):
   messageBox(msg, title, SystemIcons.Warning)

def error(msg, title = 'Error'):
   messageBox(msg, title, SystemIcons.Error)