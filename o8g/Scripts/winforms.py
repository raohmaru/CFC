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
   clr.AddReference("System.Drawing")
   clr.AddReference("System.Windows.Forms")

   from System.Windows.Forms import *
   from System.Drawing import Color
except:
   automations['WinForms'] = False
   
def calcStringLabelSize(str): 
# A function which returns a slowly expansing size for a label. The more characters, the more the width expands to allow more characters on the same line.
   newlines = str.count('\n')
   STRINGwidth = 200 + (len(str) / 4)
   STRINGheight = 30 + 20 * newlines + 10 * (STRINGwidth / 100)
   return (STRINGwidth, STRINGheight)

def calcStringButtonHeight(str): 
# A function which returns a slowly expansing size for a label. The more characters, the more the width expands to allow more characters on the same line.
   newlines = str.count('\n')
   STRINGheight = 30 + (8 * newlines) + (7 * (len(str) / 20))
   return STRINGheight
   
def formStringEscape(str): # A function to escape some characters that are not otherwise displayed by WinForms, like amperasands '&'
   return str.replace('&', '&&')

class OKWindow(Form): # This is a WinForm which creates a simple window, with some text and an OK button to close it.
   def __init__(self, InfoTXT, title='Information'):
      self.StartPosition = FormStartPosition.CenterScreen
      (STRwidth, STRheight) = calcStringLabelSize(InfoTXT)
      FORMheight = 130 + STRheight
      FORMwidth = 100 + STRwidth
      self.Text = title
      self.Height = FORMheight
      self.Width = FORMwidth
      self.AutoSize = True
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.TopMost = True
      
      labelPanel = Panel()
      labelPanel.Dock = DockStyle.Top
      labelPanel.AutoSize = True
      labelPanel.BackColor = Color.White

      self.timer_tries = 0
      self.timer = Timer()
      self.timer.Interval = 200
      self.timer.Tick += self.onTick
      self.timer.Start()
      
      label = Label()
      label.Text = formStringEscape(InfoTXT)
      label.Top = 30
      label.Left = (self.ClientSize.Width - STRwidth) / 2
      label.Height = STRheight
      label.Width = STRwidth
      labelPanel.Controls.Add(label)
      #label.AutoSize = True #Well, that's shit.

      button = Button()
      button.Text = "OK"
      button.Width = 100
      button.Top = FORMheight - 80
      button.Left = (FORMwidth - 100) / 2
      button.Anchor = AnchorStyles.Bottom

      button.Click += self.buttonPressed

      self.Controls.Add(labelPanel)
      self.Controls.Add(button)

   def buttonPressed(self, sender, args):
      self.timer.Stop()
      self.Close()

   def onTick(self, sender, event):
      if self.timer_tries < 3:
         self.TopMost = False
         self.Focus()
         self.Activate()
         self.TopMost = True
         self.timer_tries += 1
            
def information(Message):
   debugNotify(">>> information() with message: {}".format(Message))
   if automations['WinForms']:
      Application.EnableVisualStyles()
      form = OKWindow(Message)
      form.BringToFront()
      form.ShowDialog()
   else: 
      whisper(Message)
   
   
class SingleChoiceWindow(Form):
 
   def __init__(self, BoxTitle, BoxOptions, type, defaultOption, pages = 0, cancelButtonBool = True, cancelName = 'Cancel'):
      self.Text = "Select an Option"
      self.index = 0
      self.confirmValue = None
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.StartPosition = FormStartPosition.CenterScreen
      self.AutoSize = True
      self.TopMost = True
      
      (STRwidth, STRheight) = calcStringLabelSize(BoxTitle)
      self.Width = STRwidth + 50

      self.timer_tries = 0
      self.timer = Timer()
      self.timer.Interval = 200
      self.timer.Tick += self.onTick
      self.timer.Start()
      
      labelPanel = Panel()
      labelPanel.Dock = DockStyle.Top
      labelPanel.AutoSize = True
      labelPanel.BackColor = Color.White
      
      separatorPanel = Panel()
      separatorPanel.Dock = DockStyle.Top
      separatorPanel.Height = 20
      
      choicePanel = Panel()
      choicePanel.Dock = DockStyle.Top
      choicePanel.AutoSize = True

      self.Controls.Add(labelPanel)
      labelPanel.BringToFront()
      self.Controls.Add(separatorPanel)
      separatorPanel.BringToFront()
      self.Controls.Add(choicePanel)
      choicePanel.BringToFront()

      label = Label()
      label.Text = formStringEscape(BoxTitle)
      label.Top = 30
      label.Left = (self.ClientSize.Width - STRwidth) / 2
      label.Height = STRheight
      label.Width = STRwidth
      labelPanel.Controls.Add(label)
      
      bufferPanel = Panel() # Just to put the radio buttons a bit more to the middle
      bufferPanel.Left = (self.ClientSize.Width - bufferPanel.Width) / 2
      bufferPanel.AutoSize = True
      choicePanel.Controls.Add(bufferPanel)
            
      for option in BoxOptions:
         if type == 'radio':
            btn = RadioButton()
            if defaultOption == self.index: btn.Checked = True
            else: btn.Checked = False
            btn.CheckedChanged += self.checkedChanged
         else: 
            btn = Button()
            btn.Height = calcStringButtonHeight(formStringEscape(option))
            btn.Click += self.choiceMade
         btn.Name = str(self.index)
         self.index = self.index + 1
         btn.Text = formStringEscape(option)
         btn.Dock = DockStyle.Top
         bufferPanel.Controls.Add(btn)
         btn.BringToFront()

      button = Button()
      button.Text = "Confirm"
      button.Width = 100
      button.Dock = DockStyle.Bottom
      button.Click += self.buttonPressed
      if type == 'radio': self.Controls.Add(button) # We only add the "Confirm" button on a radio menu.
 
      buttonNext = Button()
      buttonNext.Text = "Next Page"
      buttonNext.Width = 100
      buttonNext.Dock = DockStyle.Bottom
      buttonNext.Click += self.nextPage
      if pages > 1: self.Controls.Add(buttonNext) # We only add the "Confirm" button on a radio menu.

      cancelButton = Button() # We add a bytton to Cancel the selection
      cancelButton.Text = cancelName # We can rename the cancel button if we want to.
      cancelButton.Width = 100
      cancelButton.Dock = DockStyle.Bottom
      #button.Anchor = AnchorStyles.Bottom
      cancelButton.Click += self.cancelPressed
      if cancelButtonBool: self.Controls.Add(cancelButton)
      
   def buttonPressed(self, sender, args):
      self.timer.Stop()
      self.Close()

   def nextPage(self, sender, args):
      self.confirmValue = "Next Page"
      self.timer.Stop()
      self.Close()
 
   def cancelPressed(self, sender, args): # The function called from the cancelButton
      self.confirmValue = None # It replaces the choice list with an ABORT message which is parsed by the calling function
      self.timer.Stop()
      self.Close() # And then closes the form
      
   def checkedChanged(self, sender, args):
      self.confirmValue = sender.Name
      
   def choiceMade(self, sender, args):
      self.confirmValue = sender.Name
      self.timer.Stop()
      self.Close()
      
   def getIndex(self):
      return self.confirmValue

   def onTick(self, sender, event):
      if self.timer_tries < 3:
         self.TopMost = False
         self.Focus()
         self.Activate()
         self.TopMost = True
         self.timer_tries += 1

def SingleChoice(title, options, type = 'button', default = 0, cancelButton = True, cancelName = 'Cancel'):
   debugNotify(">>> SingleChoice()".format(title))
   if automations['WinForms']:
      optChunks=[options[x:x+7] for x in xrange(0, len(options), 7)]
      optCurrent = 0
      choice = "New"
      while choice == "New" or choice == "Next Page" or (not choice and not cancelButton):
         Application.EnableVisualStyles()
         form = SingleChoiceWindow(title, optChunks[optCurrent], type, default, pages = len(optChunks), cancelButtonBool = cancelButton, cancelName = cancelName)
         form.BringToFront()
         form.ShowDialog()
         choice = form.getIndex()
         debugNotify("choice is: {}".format(choice), 2)
         if choice == "Next Page": 
            debugNotify("Going to next page", 3)
            optCurrent += 1
            if optCurrent >= len(optChunks): optCurrent = 0
         elif choice != None: 
            choice = num(form.getIndex()) + (optCurrent * 7) # if the choice is not a next page, then we convert it to an integer and give that back, adding 8 per number of page passed
   else:
      concatTXT = title + '\n\n'
      for iter in range(len(options)):
         concatTXT += '{}:--> {}\n'.format(iter,options[iter])
      choice = askInteger(concatTXT,0)
   debugNotify("<<< SingleChoice() with return {}".format(choice), 3)
   return choice

   
class MultiChoiceWindow(Form):
 # This is a windows form which creates a multiple choice form, with a button for each choice. 
 # The player can select more than one, and they are then returned as a list of integers
   def __init__(self, FormTitle, FormChoices,CPType, pages = 0,currPage = 0, existingChoices = []): # We initialize our form, expecting 3 variables. 
                                                      # FormTitle is the title of the window itself
                                                      # FormChoices is a list of strings which we use for the names of the buttons
                                                      # CPType is combined with FormTitle to give a more thematic window name.
      self.Text = CPType # We just store the variable locally
      self.index = 0 # We use this variable to set a number to each button
      self.MinimizeBox = False # We hide the minimize button
      self.MaximizeBox = False # We hide the maximize button
      self.StartPosition = FormStartPosition.CenterScreen # We start the form at the center of the player's screen
      self.AutoSize = True # We allow the form to expand in size depending on its contents
      self.TopMost = True # We make sure our new form will be on the top of all other windows. If we didn't have this here, fullscreen OCTGN would hide the form.
      self.origTitle = formStringEscape(FormTitle) # Used when modifying the label from a button
      
      self.confirmValue = existingChoices
      debugNotify("existingChoices = {}".format(self.confirmValue))
      self.nextPageBool = False  # self.nextPageBool is just remembering if the player has just flipped the page.
      self.currPage = currPage
      
      self.timer_tries = 0 # Ugly hack to fix the form sometimes not staying on top of OCTGN
      self.timer = Timer() # Create a timer object
      self.timer.Interval = 200 # Speed is at one 'tick' per 0.2s
      self.timer.Tick += self.onTick # Activate the event function on each tick
      self.timer.Start() # Start the timer.
      
      (STRwidth, STRheight) = calcStringLabelSize(FormTitle) # We dynamically calculate the size of the text label to be displayed as info to the player.
      labelPanel = Panel() # We create a new panel (e.g. container) to store the label.
      labelPanel.Dock = DockStyle.Top # We Dock the label's container on the top of the form window
      labelPanel.Height = STRheight # We setup the dynamic size
      labelPanel.Width = STRwidth
      labelPanel.AutoSize = True # We allow the panel to expand dynamically according to the size of the label
      labelPanel.BackColor = Color.White
      
      choicePanel = Panel() # We create a panel to hold our buttons
      choicePanel.Dock = DockStyle.Top # We dock this below the label panel
      choicePanel.AutoSize = True # We allow it to expand in size dynamically
      #radioPanel.BackColor = Color.LightSalmon # Debug

      separatorPanel = Panel() # We create a panel to separate the labels from the buttons
      separatorPanel.Dock = DockStyle.Top # It's going to be docked to the middle of both
      separatorPanel.Height = 20 # Only 20 pixels high

      self.Controls.Add(labelPanel) # The panels need to be put in the form one by one
      labelPanel.BringToFront() # This basically tells that the last panel we added should go below all the others that are already there.
      self.Controls.Add(separatorPanel)
      separatorPanel.BringToFront() 
      self.Controls.Add(choicePanel) 
      choicePanel.BringToFront() 

      self.label = Label() # We create a label object which will hold the multiple choice description text
      #if len(self.confirmValue): self.label.Text = formStringEscape(FormTitle) + "\n\nYour current choices are:\n{}".format(self.confirmValue) # We display what choices we've made until now to the player.
      self.label.Text = formStringEscape(FormTitle) # We escape any strings that WinForms doesn't like, like ampersand and store it in the label
      self.label.Top = 30 # We place the label 30 pixels from the top size of its container panel, and 50 pixels from the left.
      self.label.Left = 50
      self.label.Height = STRheight # We set its dynamic size
      self.label.Width = STRwidth
      labelPanel.Controls.Add(self.label) # We add the label to its container
      
      choicePush = Panel() # An extra secondary container for the buttons, that is not docked, to allow us to slightly change its positioning
      choicePush.Left = (self.ClientSize.Width - choicePush.Width) / 2 # We move it 50 pixels to the left
      choicePush.AutoSize = True # We allow it to expand dynamically
      choicePanel.Controls.Add(choicePush) # We add it to its parent container
      
      for option in FormChoices: # We dynamically add as many buttons as we have options
         btn = Button() # We initialize a button object
         btn.Name = str(self.index) # We name the button equal to its numeric value, plus its effect.
         btn.Text = str(self.index) + ':--> ' + formStringEscape(option)
         self.index = self.index + 1 # The internal of the button is also the choice that will be put in our list of integers. 
         btn.Dock = DockStyle.Top # We dock the buttons one below the other, to the top of their container (choicePush)
         btn.AutoSize = True # Doesn't seem to do anything
         btn.Height = calcStringButtonHeight(formStringEscape(option))
         btn.Click += self.choiceMade # This triggers the function which records each choice into the confirmValue[] list
         choicePush.Controls.Add(btn) # We add each button to its panel
         btn.BringToFront() # Add new buttons to the bottom of existing ones (Otherwise the buttons would be placed in reverse numerical order)

      buttonNext = Button()
      buttonNext.Text = "Next Page"
      buttonNext.Width = 100
      buttonNext.Dock = DockStyle.Bottom
      buttonNext.Click += self.nextPage
      if pages > 1: self.Controls.Add(buttonNext) # We only add the "Confirm" button on a radio menu.

      finishButton = Button() # We add a button to Finish the selection
      finishButton.Text = "Finish Selection"
      finishButton.Width = 100
      finishButton.Dock = DockStyle.Bottom # We dock it to the bottom of the form.
      #button.Anchor = AnchorStyles.Bottom
      finishButton.Click += self.finishPressed # We call its function
      self.Controls.Add(finishButton) # We add the button to the form
 
      cancelButton = Button() # We add a bytton to Cancel the selection
      cancelButton.Text = "Cancel"
      cancelButton.Width = 100
      cancelButton.Dock = DockStyle.Bottom
      #button.Anchor = AnchorStyles.Bottom
      cancelButton.Click += self.cancelPressed
      self.Controls.Add(cancelButton)

   def nextPage(self, sender, args):
      self.nextPageBool = True
      self.timer.Stop()
      self.Close()
 
   def finishPressed(self, sender, args): # The function called from the finishButton.
      self.timer.Stop()
      self.Close()  # It just closes the form

   def cancelPressed(self, sender, args): # The function called from the cancelButton
      self.confirmValue = 'ABORT' # It replaces the choice list with an ABORT message which is parsed by the calling function
      self.timer.Stop()
      self.Close() # And then closes the form
 
   def choiceMade(self, sender, args): # The function called when pressing one of the choice buttons
      self.confirmValue.append((self.currPage * 7) + int(sender.Name)) # We append the button's name to the existing choices list
      self.label.Text = self.origTitle + "\n\nYour current choices are:\n{}".format(self.confirmValue) # We display what choices we've made until now to the player.
 
   def getIndex(self): # The function called after the form is closed, to grab its choices list
      if self.nextPageBool: 
         self.nextPageBool = False
         return "Next Page"
      else: return self.confirmValue

   def getStoredChoices(self): # The function called after the form is closed, to grab its choices list
      return self.confirmValue

   def onTick(self, sender, event): # Ugly hack required because sometimes the winform does not go on top of all
      if self.timer_tries < 3: # Try three times to bring the form on top
         if debugVerbosity >= 2: self.label.Text = self.origTitle + '\n\n### Timer Iter: ' + str(self.timer_tries)
         self.TopMost = False # Set the form as not on top
         self.Focus() # Focus it
         self.Activate() # Activate it
         self.TopMost = True # And re-send it to top
         self.timer_tries += 1 # Increment this counter to stop after 3 tries.

def multiChoice(title, options,card): # This displays a choice where the player can select more than one ability to trigger serially one after the other
   debugNotify(">>> multiChoice()".format(title))
   if automations['WinForms']: # If the player has not disabled the custom WinForms, we use those
      optChunks=[options[x:x+7] for x in xrange(0, len(options), 7)]
      optCurrent = 0
      choices = "New"
      currChoices = []
      while choices == "New" or choices == "Next Page":
         Application.EnableVisualStyles() # To make the window look like all other windows in the user's system
         CPType = 'Control Panel'
         debugNotify("About to open form")
         form = MultiChoiceWindow(title, optChunks[optCurrent], CPType, pages = len(optChunks), currPage = optCurrent, existingChoices = currChoices) # We create an object called "form" which contains an instance of the MultiChoice windows form.
         form.ShowDialog() # We bring the form to the front to allow the user to make their choices
         choices = form.getIndex() # Once the form is closed, we check an internal variable within the form object to grab what choices they made
         if choices == "Next Page": 
            debugNotify("Going to next page", 3)
            optCurrent += 1
            if optCurrent >= len(optChunks): optCurrent = 0
            currChoices = form.getStoredChoices()
            debugNotify("currChoices = {}".format(currChoices))            
   else: # If the user has disabled the windows forms, we use instead the OCTGN built-in askInteger function
      concatTXT = title + "\n\n(Tip: You can put multiple abilities one after the the other (e.g. '110'). Max 9 at once)\n\n" # We prepare the text of the window with a concat string
      for iter in range(len(options)): # We populate the concat string with the options
         concatTXT += '{}:--> {}\n'.format(iter,options[iter])
      choicesInteger = askInteger(concatTXT,0) # We now ask the user to put in an integer.
      if not choicesInteger: choices = 'ABORT' # If the user just close the window, abort.
      else: 
         choices = list(str(choicesInteger)) # We convert our number into a list of numeric chars
         for iter in range(len(choices)): choices[iter] = int(choices[iter]) # we convert our list of chars into a list of integers      
   debugNotify("<<< multiChoice() with list: {}".format(choices), 3)
   return choices # We finally return a list of integers to the previous function. Those will in turn be iterated one-by-one serially.
