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
   # Enables the colors, fonts, and other visual elements that form an operating system theme
   Application.EnableVisualStyles()
except (IOError, ImportError):
   settings["WinForms"] = False


class CustomForm(Form):   
   """
   Base class for custom forms.
   """
   MinWidth = 300
   MaxWidth = 500
   MinHeight = 180
   TextPadding = 20
   
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
      # MeasureString() returns System.Drawing.SizeF
      size = g.MeasureString(str, form.Font, width).ToSize()
      debug(">>> measureString('{}...', {}) => {}", str[:14], width, size)
      g.Dispose()
      form.Dispose()
      return size

   def stringEscape(self, str):
      """
      Escapes some characters that are otherwise not displayed by WinForms, like "&".
      """
      return str.replace("&", "&&")

   def show(self):
      """
      Returns the dialog result for the form.
      """
      showWinForm(self) # C# method
      debug("Form result: {}", self.DialogResult)
      return self.DialogResult == DialogResult.OK
   

class MessageBoxForm(CustomForm):
   """
   This is a WinForm which creates a simple window, with an icon, text and a button to close it.
   """

   def __init__(self, msg, title, icon = None, boxIcon = None):
      super(self.__class__, self).__init__()
      # Suppress multiple Layout events while adjusting attributes of the controls.
      # This will increase the performance of applications with many controls.
      self.SuspendLayout()
      # Label panel
      labelPanel = self.createLabelPanel(boxIcon)
      self.Controls.Add(labelPanel)
      # Image
      if boxIcon:
         pictureBox = self.createLabelIcon(boxIcon)
         labelPanel.Controls.Add(pictureBox)
      # Label
      label = self.createLabel(msg)
      labelPanel.Controls.Add(label)
      # Buttons
      buttonPanel = self.createButtonPanel()
      self.Controls.Add(buttonPanel)
      button = self.createAcceptButton("OK")
      buttonPanel.Controls.Add(button)
      # Form setup
      formSize = self.measureString(msg, self.MaxWidth)
      self.setup(formSize.Width, formSize.Height + buttonPanel.Height, title, msg, icon)
      # Resumes usual layout logic
      labelPanel.ResumeLayout(False)
      buttonPanel.ResumeLayout(False)
      self.ResumeLayout(False)
      
      
   def createLabelPanel(self, hasIcon = None):
      labelPanel = TableLayoutPanel() if hasIcon else Panel()
      labelPanel.SuspendLayout()
      labelPanel.Dock = DockStyle.Fill
      labelPanel.BackColor = Color.White
      labelPanel.Padding = Padding(self.TextPadding)
      # labelPanel.BorderStyle = BorderStyle.FixedSingle
      if hasIcon:
         labelPanel.ColumnCount = 2
         labelPanel.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 42))  # Image cell
         labelPanel.ColumnStyles.Add(ColumnStyle(SizeType.AutoSize))      # Label cell
      return labelPanel
      
   
   def createButtonPanel(self):
      buttonPanel = TableLayoutPanel()
      buttonPanel.SuspendLayout()
      buttonPanel.Dock = DockStyle.Bottom
      # The control is automatically resized to display its entire contents
      buttonPanel.AutoSize = True
      buttonPanel.Padding = Padding(5)
      # buttonPanel.BorderStyle = BorderStyle.FixedSingle
      return buttonPanel
            
    
   def createLabel(self, msg):
      label = Label()
      label.Text = self.stringEscape(msg)
      label.TextAlign = ContentAlignment.MiddleLeft
      label.Anchor = AnchorStyles.Left | AnchorStyles.Right
      # Fill the available content of the parent
      label.Dock = DockStyle.Fill
      # label.BorderStyle = BorderStyle.FixedSingle
      return label
      
      
   def createLabelIcon(self, icon):
      pictureBox = PictureBox()
      # Fit the image into the PictureBox
      pictureBox.SizeMode = PictureBoxSizeMode.StretchImage
      pictureBox.Size = icon.Size
      pictureBox.Image = icon.ToBitmap()
      pictureBox.Anchor = AnchorStyles.Right
      # pictureBox.BorderStyle = BorderStyle.FixedSingle
      return pictureBox
    
   def createAcceptButton(self, text):
      button = Button()
      # Make button's dialog result OK, triggered on click or by pressing Enter key
      button.DialogResult = DialogResult.OK
      button.Text = text
      button.Anchor = AnchorStyles.Right
      # Set the accept button of the form
      self.AcceptButton = button
      return button
      
    
   def createCancelButton(self, text):
      button = Button()
      # Make button's dialog result Cancel, triggered on click or by pressing Cancel key
      button.DialogResult = DialogResult.Cancel
      button.Text = text
      button.Anchor = AnchorStyles.Left
      # Set the cancel button of the form
      self.CancelButton = button
      return button
   
   
   def setup(self, width, height, title, msg, icon = None):
      self.Size = Size(
         # Rendered dialog width is 20px less because reasons
         max(self.MinWidth,  width) + self.TextPadding * 2 + 20,
         max(self.MinHeight, height + self.TextPadding)
      )
      debug(">>> MessageBoxForm({}/{}, {}/{}) => {}", width, self.MinWidth, height, self.MinHeight, self.Size)
      self.StartPosition = FormStartPosition.CenterScreen
      # Text of the toolbar
      self.Text = title
      # Disables resizing
      self.FormBorderStyle = FormBorderStyle.FixedSingle
      self.MinimizeBox = False
      self.MaximizeBox = False
      # Sets the icon in the toolbar
      if icon:
         self.Icon = icon
      else:
         # Hides the icon in the toolbar
         self.ShowIcon = False


class ConfirmForm(MessageBoxForm):
   """
   Customized confirm form with a checkbox option to choose to do not show again the dialog.
   """

   def __init__(self, msg, title, settingID, icon = SystemIcons.Question):
      self.settingID = settingID
      # Don't init the parent but the grandfather
      super(CustomForm, self).__init__()
      self.SuspendLayout()
      # Checkbox
      checkboxPanel = Panel()
      checkboxPanel.SuspendLayout()
      # checkboxPanel.BorderStyle = BorderStyle.FixedSingle
      checkboxPanel.Dock = DockStyle.Fill
      checkboxPanel.AutoSize = True
      checkboxPanel.BackColor = Color.White
      self.Controls.Add(checkboxPanel)
      self.checkBox = CheckBox()
      self.checkBox.Text = "&Do not show this message again"
      #                               left Top Right           Bottom
      self.checkBox.Padding = Padding(28, 0, self.TextPadding, self.TextPadding)
      self.checkBox.AutoSize = True
      self.checkBox.ForeColor = Color.DimGray
      checkboxPanel.Controls.Add(self.checkBox)
      # Label panel
      labelPanel = self.createLabelPanel(True)
      labelPanel.Dock = DockStyle.Top
      self.Controls.Add(labelPanel)
      # Image
      pictureBox = self.createLabelIcon(icon)
      labelPanel.Controls.Add(pictureBox)
      # Label
      label = self.createLabel(msg)
      labelPanel.Controls.Add(label)
      # Buttons
      buttonPanel = self.createButtonPanel()
      buttonPanel.ColumnCount = 2
      buttonPanel.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50))
      # Will center buttons horizontally
      # buttonPanel.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50))
      self.Controls.Add(buttonPanel)
      button1 = self.createAcceptButton("&Yes")
      buttonPanel.Controls.Add(button1)
      button2 = self.createCancelButton("&No")
      buttonPanel.Controls.Add(button2)
      # Form setup
      formSize = self.measureString(msg, self.MaxWidth - 42)
      # Magic numbers. Magic numbers everywhere.
      self.setup(formSize.Width, max(formSize.Height, 64) + buttonPanel.Height + self.TextPadding, title, msg)
      # If text contains 5 or more lines, it is rendered cropped
      if formSize.Height > 60:
         labelPanel.Height += 2
      # Hide the toolbar
      self.ControlBox = False
      # Resumes usual layout logic
      checkboxPanel.ResumeLayout(False)
      labelPanel.ResumeLayout(False)
      buttonPanel.ResumeLayout(False)
      self.ResumeLayout(False)
      

   def show(self):
      res = super(ConfirmForm, self).show()
      debug("-- checked: {}", self.checkBox.Checked)
      # Remember choice if checked and confirmed
      if res:
         doNotShow = settings["DoNotShow"].copy()
         doNotShow[self.settingID] = self.checkBox.Checked
         switchSetting("DoNotShow", doNotShow)
      return res


#---------------------------------------------------------------------------
# Shortcuts
#---------------------------------------------------------------------------

def messageBox(type, msg, title, icon = None, boxIcon = None):
   debug(">>> messageBox({}, {}, {})", title, icon, boxIcon)
   if settings["WinForms"]:
      # Replace the card ID with the card name
      msg = replIdsWithNames(msg)
      debug(msg)
      if boxIcon:
         # Use native MessageBox
         return MessageBox.Show(msg, title, MessageBoxButtons.OK, boxIcon)
      else:
         # Custom form because in the native MessageBox we cannot add an icon to the toolbar
         playSnd("win-{}".format(type), True)
         form = MessageBoxForm(msg, title, icon)
         return form.show()
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
   messageBox("warning", msg, title, boxIcon = MessageBoxIcon.Warning)


def error(msg, title = "Error"):
   messageBox("error", msg, title, boxIcon = MessageBoxIcon.Error)


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
def confirm(msg, settingID = None):
   playSnd("win-confirm", True)
   if settingID and settings["WinForms"]:
      # Remember last choice (True: do not show again)
      if settingID in settings["DoNotShow"] and settings["DoNotShow"][settingID]:
         return True
      # Custom form with a checkbox
      form = ConfirmForm(msg, "Confirmation", settingID)
      return form.show()
   return _confirm_(msg)


_askChoice_ = askChoice
def askChoice(question, choices = [], colors = [], customButtons = []):
   playSnd("win-ask-2", True)
   return _askChoice_(question, choices, colors, customButtons)


_remoteCall_ = remoteCall
def remoteCall(player, func, args):
   mute()
   _remoteCall_(player, func, args)