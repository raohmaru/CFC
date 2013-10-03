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

import re, time

#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------

def num(s):
# This function reads the value of a card and returns an integer. For some reason integer values of cards are not processed correctly
# see bug 373 https://octgn.16bugs.com/projects/3602/bugs/188805
# This function will also return 0 if a non-integer or an empty value is provided to it as it is required to avoid crashing your functions.
#   if s == '+*' or s == '*': return 0
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0

def delayed_whisper(text): # Because whispers for some reason execute before notifys
   rnd(1,10)
   whisper(text)

def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   if playerside == None:  # Has the player selected a side yet? If not, then...
      if Table.isTwoSided():
         playeraxis = Yaxis
         if me.hasInvertedTable():
            playerside = -1
         else:
            playerside = 1
      else:
         playeraxis = Yaxis
         if confirm("Will you play on the bottom side?"): # Ask which side they want
            playerside = 1 # This is used to swap between the two halves of the X axis of the play field. Positive is on the right.
         else:
            playerside = -1 # Negative is on the left.

def resetAll(): # Clears all the global variables in order to start a new game.
   # Import all our global variables and reset them.
   global playerside, handsize, debugVerbosity, slots
   debugNotify(">>> resetAll()") #Debug
   playerside = None
   handsize = 5
   slots = {}
   me.HP = 30  # Wipe the counters
   me.SP = 0
   backups = eval(getGlobalVariable('Backups'))
   backups.clear()
   setGlobalVariable('Backups',str(backups))
   if len(players) > 1: debugVerbosity = -1 # Reset means normal game.
   elif debugVerbosity != -1 and confirm("Reset Debug Verbosity?"): debugVerbosity = -1
   debugNotify("<<< resetAll()") #Debug

def switchAutomation(type, command = None):
   debugNotify(">>> switchAutomation({})".format(type)) #Debug
   global automations
   if not type in automations:
      return
   if command == None:
      automations[type] = not automations[type]
   else:
      automations[type] = command
   notify("--> {}'s {} automations are {}.".format(me, type, automations[type]))

#---------------------------------------------------------------------------
# Card Placement functions
#---------------------------------------------------------------------------

def cwidth(card, divisor = 10):
# This function is used to always return the width of the card plus an offset that is based on the percentage of the width of the card used.
# The smaller the number given, the less the card is divided into pieces and thus the larger the offset added.
# For example if a card is 80px wide, a divisor of 4 will means that we will offset the card's size by 80/4 = 20.
# In other words, we will return 1 + 1/4 of the card width.
# Thus, no matter what the size of the table and cards becomes, the distances used will be relatively the same.
# The default is to return an offset equal to 1/10 of the card width. A divisor of 0 means no offset.
   if divisor == 0: offset = 0
   else: offset = card.width() / divisor
   return (card.width() + offset)

def cheight(card, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = card.height() / divisor
   return (card.height() + offset)

def placeCard(card, type = None, action = None, target = None):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   debugNotify(">>> placeCard()") #Debug
   if automations['Play']:
      if type == 'Character' and action != None:
         coords = (0,0)
         if action == 'play':
            coords = CardsCoords['Slot'+`target`]
         elif action == 'backup':
            cx,cy = target.position
            backups = eval(getGlobalVariable('Backups'))
            numBkps = len([id for id in backups if backups[id] == target._id])
            coords = (cx, cy-(15*numBkps))
         card.moveToTable(coords[0], coords[1])
      else:
         card.moveToTable(-cwidth(card,0)/2, 0)
   else:
      card.moveToTable(0,0)
   debugNotify("<<< placeCard()")

#---------------------------------------------------------------------------
# Markers functions
#---------------------------------------------------------------------------

def findMarker(card, markerDesc): # Goes through the markers on the card and looks if one exist with a specific description
   debugNotify(">>> findMarker()") #Debug
    # If the marker description is the code of a known marker, then we need to grab the actual name of that.
   if markerDesc in mdict:
      markerDesc = mdict[markerDesc][0]
   debugNotify("### Searching for marker {}".format(markerDesc), 2) # Debug
   for key in card.markers:
      if markerDesc == key[0] or re.search(r'{}'.format(markerDesc),key[0]):
         debugNotify("### Found {} on {}".format(key[0], card), 2)
         debugNotify("<<< findMarker()")
         return True
   debugNotify("<<< findMarker() key not found")
   return False

def changeMarker(cards, marker, question):  # Changes the number of markers in one or more cards
   n = 0
   for c in cards:
      if c.markers[marker] > n:
	     n = c.markers[marker]
   count = askInteger(question, n)
   if count == None: return
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = count
      dif = count-n
      if dif >= 0: dif = "+" + str(dif)   
      notify("{} sets {}'s {} to {}({}).".format(me, c, marker[0], count, dif))


#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def modSP(count = 1, silent = False): # A function to modify the players SP counter. Can also notify.
   count = num(count) # We need to make sure we get an integer or we will fail horribly. OCTGN doesn't seem to respect its own definitions.
   me.SP += count # Now increase the SP by the amount passed to us.
   if not silent and count != 0:
      action = "gains" if count >= 0 else "loses"
      notify("{} {} {} SP. New total is {}.".format(me, action, count, me.SP))

def payCostSP(count = 1, silent = False): # Pay an SP cost. However we also check if the cost can actually be paid.
   count = num(count)
   if count >= 0:
      modSP(count, silent)
   else:
      if me.SP+count < 0: # If we don't have enough SP, we assume card effects or mistake and notify the player that they need to do things manually.
         if not silent:
            if not confirm("You do not seem to have enough SP to play this card. Are you sure you want to proceed? \
            \n(If you do, your SP will go to the negative. You will need to increase it manually as required.)"):
               return 'ABORT'
            notify("{} was supposed to pay {} SP but only has {}.".format(me, count, me.SP))
      me.SP += count
      if not silent: notify("{} has spent {} SP. New total is {}.".format(me, count, me.SP))


#------------------------------------------------------------------------------
# Card Attachments
#------------------------------------------------------------------------------

def attach(card, target):
   debugNotify(">>> attachCard()") #Debug
   target.target(False)
   backups = eval(getGlobalVariable('Backups'))
   backups[card._id] = target._id
   setGlobalVariable('Backups', str(backups))
   debugBackups()
   debugNotify("<<< attachCard()")
   
def dettach(card):
   debugNotify(">>> dettach()") #Debug
   mute()
   card.target(False)
   backups = eval(getGlobalVariable('Backups'))
   # Next line causes an error
   # attachements = [att_id for att_id in backups if backups[att_id] == card._id]
   attach_len = len([id for id in backups if backups[id] == card._id])
   # Delete links of cards that were attached to the card
   if attach_len > 0:
      for id in backups:
         if backups[id] == card._id:
            del backups[id]
            notify("{} unattaches {} from {}.".format(me, Card(id), card))
   # Or, if the card was an attachment, delete the link
   elif card._id in backups:
      del backups[card._id]
      notify("Unattaching {} from {}".format(card, Card(backups[card._id])))
   else:
      return
   setGlobalVariable('Backups', str(backups))
   debugBackups()
   debugNotify("<<< dettach()")

def clearAttachLinks(card):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the attach dictionary, if it was itself attached to another card
   debugNotify(">>> clearAttachLinks({})".format(card)) #Debug
   
   backups = eval(getGlobalVariable('Backups'))
   # Next line causes an error
   # attachements = [k for k, v in backups.iteritems() if v == card._id]
   attach_len = len([id for id in backups if backups[id] == card._id])
   # Dettach cards that were attached to the card
   if attach_len > 0:
      for id in backups:
         if backups[id] == card._id:
            attcard = Card(id)
            debugNotify("Unattaching {} from {}.".format(attcard, card))
            if attcard in table:
               discard(attcard)
            del backups[id]
   # If the card was an attachment, delete the link
   if backups.has_key(card._id):
      debugNotify("{} is attached to {}. Unattaching.".format(card, Card(backups[card._id])))
      del backups[card._id] # If the card was an attachment, delete the link
   setGlobalVariable('Backups', str(backups))
   
   debugBackups()   
   debugNotify("<<< clearAttachLinks()") #Debug
   
def freeSlot(card):
# Frees a slot of the ring. It normally happens when a character leaves the ring
   debugNotify(">>> freeSlot({})".format(card)) #Debug
   
   myRing = eval(me.getGlobalVariable('Ring'))
   if card._id in myRing:
      myRing[myRing.index(card._id)] = None
   
   debugNotify("{}'s ring: {}".format(me, myRing))
   me.setGlobalVariable('Ring', str(myRing))
   
   debugNotify("<<< freeSlot()") #Debug

#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def debugNotify(msg = 'Debug Ping!', level = 2):
   if not re.search(r'<<<',msg) and not re.search(r'>>>',msg):
      msg = '#' * level + ' ' +  msg  # We add extra hashes at the start of debug messages equal to the level of the debug, to make them stand out more
   else:
      level = 1
   if debugVerbosity >= level:
      notify(msg)

def TrialError(group, x=0, y=0):
   global debugVerbosity
   mute()
   if debugVerbosity >= 0:
      debugVerbosity += 1
      if debugVerbosity > 4:
         debugVerbosity = 0
      whisper("Debug verbosity is now: {}".format(debugVerbosity))
      return
   delayed_whisper("### Checking Players")
   if me.name == 'raohmaru':
      debugVerbosity = 0
   delayed_whisper("### Checking Debug Validity")
   if not (len(players) == 1 or debugVerbosity >= 0):
      whisper("This function is only for development purposes")
      return
   delayed_whisper("### Setting Table Side")
   if not playerside:  # If we've already run this command once, don't recreate the cards.
      chooseSide()

def debugBackups():
   backups = eval(getGlobalVariable('Backups'))
   debugNotify("BACKUPS ({})".format(len(backups)))
   for id in backups:
      debugNotify("   {} backups {}".format(Card(id), Card(backups[id])))
   