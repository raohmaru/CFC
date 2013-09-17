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

def setHandSize(group):  # A function to modify a player's hand size.
   global handsize
   handsize = askInteger("What is your current hand size?", handsize)
   if handsize == None: handsize = 5
   notify("{} sets their hand size to {}".format(me, handsize))

def resetAll(): # Clears all the global variables in order to start a new game.
   # Import all our global variables and reset them.
   global playerside, handsize, debugVerbosity
   debugNotify(">>> resetAll()") #Debug
   playerside = None
   handsize = 5
   me.SP = 0 # Wipe the counters
   backups = eval(getGlobalVariable('Backups'))
   backups.clear()
   setGlobalVariable('Backups',str(backups))
   if len(players) > 1: debugVerbosity = -1 # Reset means normal game.
   elif debugVerbosity != -1 and confirm("Reset Debug Verbosity?"): debugVerbosity = -1
   debugNotify("<<< resetAll()") #Debug
   

#---------------------------------------------------------------------------
# Card Placement functions
#---------------------------------------------------------------------------

def cwidth(card = None, divisor = 10):
# This function is used to always return the width of the card plus an offset that is based on the percentage of the width of the card used.
# The smaller the number given, the less the card is divided into pieces and thus the larger the offset added.
# For example if a card is 80px wide, a divisor of 4 will means that we will offset the card's size by 80/4 = 20.
# In other words, we will return 1 + 1/4 of the card width.
# Thus, no matter what the size of the table and cards becomes, the distances used will be relatively the same.
# The default is to return an offset equal to 1/10 of the card width. A divisor of 0 means no offset.
   if divisor == 0: offset = 0
   else: offset = CardWidth / divisor
   return (CardWidth + offset)

def cheight(card = None, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = CardHeight / divisor
   return (CardHeight + offset)

def placeCard(card, type = None, dudecount = 0):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   if playeraxis == Xaxis:
      if type == 'Character':
         card.moveToTable(homeDistance(card) + cardDistance(card) + playerside * cwidth(card), 0)
      else: card.moveToTable(0,0)
   else: card.moveToTable(0,0)

def homeDistance(card):
# This function retusn the distance from the middle each player's home will be setup towards their playerSide.
# This makes the code more readable and allows me to tweak these values from one place
   if playeraxis == Xaxis:
      return (playerside * cwidth(card) * 5) # players on the X axis, are placed 5 times a card's width towards their side (left or right)
   elif playeraxis == Yaxis:
      return (playerside * cheight(card) * 3) # players on the Y axis, are placed 3 times a card's height towards their side (top or bottom)

def cardDistance(card):
# This function returns the size of the card towards a player's side.
# This is useful when playing cards on the table, as you can always manipulate the location
#   by multiples of the card distance towards your side
# So for example, if a player is playing on the bottom side. This function will always return a positive cardheight.
#   Thus by adding this in a moveToTable's y integer, the card being placed will be moved towards your side by one multiple of card height
#   While if you remove it from the y integer, the card being placed will be moved towards the centre of the table by one multiple of card height.
   if playeraxis == Xaxis:
      return (playerside * cwidth(card))
   elif playeraxis == Yaxis:
      return (playerside * cheight(card))


#---------------------------------------------------------------------------
# Markers functions
#---------------------------------------------------------------------------

def findMarker(card, markerDesc): # Goes through the markers on the card and looks if one exist with a specific description
   if debugVerbosity >= 1: notify(">>> findMarker(){}".format(extraASDebug())) #Debug
   foundKey = None
   if markerDesc in mdict: markerDesc = mdict[markerDesc][0] # If the marker description is the code of a known marker, then we need to grab the actual name of that.
   for key in card.markers:
      if debugVerbosity >= 3: notify("### Key: {}\nmarkerDesc: {}".format(key[0],markerDesc)) # Debug
      if re.search(r'{}'.format(markerDesc),key[0]) or markerDesc == key[0]:
         foundKey = key
         if debugVerbosity >= 2: notify("### Found {} on {}".format(key[0],card))
         break
   if debugVerbosity >= 3: notify("<<< findMarker() by returning: {}".format(foundKey))
   return foundKey

def changeMarker(cards, marker, question):
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

def modSP(count = 1, notification = silent): # A function to modify the players SP counter. Can also notify.
   count = num(count) # We need to make sure we get an integer or we will fail horribly. OCTGN doesn't seem to respect its own definitions.
   me.SP += count # Now increase the SP by the amount passed to us.
   if notification == 'loud' and count > 0: notify("{}'s SP has modified by {}. New total is {}.".format(me, count, me.SP))
   # We only notify if the function is called as "loud" and we actually modify anything.

def payCost(count = 1, notification = silent): # Pay an SP cost. However we also check if the cost can actually be paid.
   count = num(count)
   if count == 0 : return # If the card has 0 cost, there's nothing to do.
   if me.SP < count: # If we don't have enough SP, we assume card effects or mistake and notify the player that they need to do things manually.
      if notification == loud:
         if not confirm("You do not seem to have enough SP to play this card. Are you sure you want to proceed? \
         \n(If you do, your SP will go to the negative. You will need to increase it manually as required.)"): return 'ABORT'
         notify("{} was supposed to pay {} SP but only has {}. They'll need to reduce the cost by {} with card effects.".format(me, count, me.SP, count - me.SP))
         me.SP -= num(count)
      else: me.SP -= num(count)
   else: # Otherwise, just take the SP out and inform that we did if we're "loud".
      me.SP -= num(count)
      if notification == loud: notify("{} has paid {} SP. New total is {}.".format(me, count, me.SP))


#------------------------------------------------------------------------------
# Card Attachments
#------------------------------------------------------------------------------

def attach(card, target):
   debugNotify(">>> attachCard(){}".format(extraASDebug())) #Debug
   backups = eval(getGlobalVariable('Backups'))
   backups[card._id] = target._id
   target.target(False)
   setGlobalVariable('Backups', str(backups))
   debugNotify("<<< attachCard()", 3)
   
def dettach(card):
   debugNotify(">>> dettach(){}".format(extraASDebug())) #Debug
   mute()
   backups = eval(getGlobalVariable('Backups'))
   card.target(False)
   if card._id in dict([(v, k) for k, v in backups.iteritems()]):
      card2 = [k for k, v in backups.iteritems() if v == card._id]
      for card3 in card2:
         del backups[card3]
         notify("{} unattaches {} from {}.".format(me, Card(card3), card))
   elif card._id in backups:
      card2 = backups[card._id]
      del backups[card._id]
      notify("unattaching {} from {}".format(card, Card(card2)))
   else:
      return
   setGlobalVariable('Backups', str(backups))
   debugNotify("<<< dettach()")

def clearAttachLinks(card):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the attach dictionary, if it was itself attached to another card
   debugNotify(">>> clearAttachLinks()") #Debug
   backups = eval(getGlobalVariable('Backups'))
   attachements = [att_id for att_id in backups if backups[att_id] == card._id]
   if len(attachements) >= 1:
      for att_id in attachements:
         if attachements[att_id] == card._id:
            if Card(att_id) in table:
               debugNotify("Attachment exists. Trying to remove.", 2)
               discard(Card(att_id))
            del backups[att_id]
   debugNotify("Checking if the card is attached to unlink.", 2)
   if backups.has_key(card._id):
      del backups[card._id] # If the card was an attachment, delete the link
   setGlobalVariable('Backups', str(backups))
   debugNotify("<<< clearAttachLinks()") #Debug


#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def debugNotify(msg = 'Debug Ping!', level = 1):
   if not re.search(r'<<<',msg) and not re.search(r'>>>',msg):
      hashes = '#'
      for iter in range(level): hashes += '#' # We add extra hashes at the start of debug messages equal to the level of the debug+1, to make them stand out more
      msg = hashes + ' ' +  msg
   if re.search(r'<<<',msg): level = 3 # We always request level debug logs to display function exist notifications.
   if debugVerbosity >= level: notify(msg)

def TrialError(group, x=0, y=0): # Debugging
   global debugVerbosity
   mute()
   if debugVerbosity >=0:
      if debugVerbosity == 0:
         debugVerbosity = 1
      elif debugVerbosity == 1: debugVerbosity = 2
      elif debugVerbosity == 2: debugVerbosity = 3
      elif debugVerbosity == 3: debugVerbosity = 4
      else: debugVerbosity = 0
      notify("Debug verbosity is now: {}".format(debugVerbosity))
      return
   notify("### Checking Players")
   for player in players:
      if player.name == 'raohmaru': debugVerbosity = 0
   notify("### Checking Debug Validity")
   if not (len(players) == 1 or debugVerbosity >= 0):
      whisper("This function is only for development purposes")
      return
   notify("### Setting Table Side")
   if not playerside:  # If we've already run this command once, don't recreate the cards.
      chooseSide()

def extraASDebug(Autoscript = None):
   if Autoscript and debugVerbosity >= 3: return ". Autoscript:{}".format(Autoscript)
   else: return ''
