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

debugVerbosity = 4 # At -1, means no debugging messages display

Automations = {'Play'      : True, # If True, game will automatically trigger card effects when playing or double-clicking on cards. Requires specific preparation in the sets.
               'Phase'     : True, # If True, game will automatically trigger effects happening at the start of the player's turn, from cards they control.
               'WinForms'  : True} # If True, game will use the custom Windows Forms for displaying multiple-choice menus and information pop-ups


#---------------------------------------------------------------------------
# Misc
#---------------------------------------------------------------------------

def resetAll(): # Clears all the global variables in order to start a new game.
   # Import all our global variables and reset them.
   global playerside, strikeCount, posSideCount, negSideCount, handsize, playerOutfit
   global wantedDudes, harrowedDudes, jailbrokenDeeds, ValueMemory, debugVerbosity
   debugNotify(">>> resetAll()") #Debug
   setGlobalVariable('Shootout','False')
   playerside = None
   strikeCount = 0
   posSideCount = 0
   negSideCount = 0
   handsize = 5
   shared.Phase = 0
   me.GhostRock = 0 # Wipe the counters
   me.Influence = 0
   me.Control = 0
   me.VictoryPoints = 0
   me.HandRank = 0
   playerOutfit = None
   wantedDudes.clear() # Clear the dictionaries so that you don't remember card memory from the previous games
   harrowedDudes.clear()
   jailbrokenDeeds.clear()
   ValueMemory.clear()
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostCards.clear()
   setGlobalVariable('Host Cards',str(hostCards))
   setGlobalVariable('Called Out','None')
   setGlobalVariable('Shootout','False')
   if len(players) > 1: debugVerbosity = -1 # Reset means normal game.
   elif debugVerbosity != -1 and confirm("Reset Debug Verbosity?"): debugVerbosity = -1
   debugNotify("<<< resetAll()") #Debug


#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------

def modInfluence(count = 1, notification = silent): # A function to modify the players influence counter. Can also notify.
   count = num(count) # We need to make sure we get an integer or we will fail horribly. OCTGN doesn't seem to respect its own definitions.
   me.Influence += count # Now increase the influence by the amount passed to us.
   if notification == 'loud' and count > 0: notify("{}'s influence has increased by {}. New total is {}".format(me, count, me.Influence))
   # We only notify if the function is called as "loud" and we actually modify anything.

def payCost(count = 1, notification = silent): # Same as above for Ghost Rock. However we also check if the cost can actually be paid.
   count = num(count)
   if count == 0 : return # If the card has 0 cost, there's nothing to do.
   if me.GhostRock < count: # If we don't have enough Ghost Rock in the bank, we assume card effects or mistake and notify the player that they need to do things manually.
      if notification == loud:
         if not confirm("You do not seem to have enough Ghost Rock in your bank to play this card. Are you sure you want to proceed? \
         \n(If you do, your GR will go to the negative. You will need to increase it manually as required.)"): return 'ABORT'
         notify("{} was supposed to pay {} Ghost Rock but only has {} in their bank. They'll need to reduce the cost by {} with card effects.".format(me, count, me.GhostRock, count - me.GhostRock))
         me.GhostRock -= num(count)
      else: me.GhostRock -= num(count)
   else: # Otherwise, just take the money out and inform that we did if we're "loud".
      me.GhostRock -= num(count)
      if notification == 'loud': notify("{} has paid {} Ghost Rock. {} is left their bank".format(me, count, me.GhostRock))


#------------------------------------------------------------------------------
# Card Attachments scripts
#------------------------------------------------------------------------------

def attachCard(attachment,host,facing = 'Same'):
   debugNotify(">>> attachCard(){}".format(extraASDebug())) #Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostCards[attachment._id] = host._id
   setGlobalVariable('Host Cards',str(hostCards))
   orgAttachments(host,facing)
   debugNotify("<<< attachCard()", 3)

def clearAttachLinks(card,type = 'Discard'):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the host dictionary, if it was itself attached to another card
# If the card was hosted by a Daemon, it also returns the free MU token to that daemon
   debugNotify(">>> clearAttachLinks()") #Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   cardAttachementsNR = len([att_id for att_id in hostCards if hostCards[att_id] == card._id])
   if cardAttachementsNR >= 1:
      hostCardSnapshot = dict(hostCards)
      for attachmentID in hostCardSnapshot:
         if hostCardSnapshot[attachmentID] == card._id:
            if Card(attachmentID) in table:
               debugNotify("Attachment exists. Trying to remove.", 2)
               if type == 'Discard': discard(Card(attachmentID))
               else: ace(Card(attachmentID))
            del hostCards[attachmentID]
   debugNotify("Checking if the card is attached to unlink.", 2)
   if hostCards.has_key(card._id):
      hostCard = Card(hostCards[card._id])
      del hostCards[card._id] # If the card was an attachment, delete the link
      setGlobalVariable('Host Cards',str(hostCards)) # We store it before calling orgAttachments, so that it has the updated list of hostCards.
      orgAttachments(hostCard)
   else: setGlobalVariable('Host Cards',str(hostCards))
   debugNotify("<<< clearAttachLinks()", 3) #Debug

def makeChoiceListfromCardList(cardList,includeText = False):
# A function that returns a list of strings suitable for a choice menu, out of a list of cards
# Each member of the list includes a card's name, traits, resources, markers and, if applicable, combat icons
   debugNotify(">>> makeChoiceListfromCardList()")
   debugNotify("cardList: {}".format([c.name for c in cardList]), 2)
   targetChoices = []
   debugNotify("About to prepare choices list.", 2)# Debug
   for T in cardList:
      debugNotify("Checking {}".format(T), 4)# Debug
      markers = 'Counters:'
      if T.markers[mdict['WantedMarker']] and T.markers[mdict['WantedMarker']] >= 1: markers += "Wanted,".format(T.markers[mdict['Advancement']])
      if T.markers[mdict['HarrowedMarker']] and T.markers[mdict['HarrowedMarker']] >= 1: markers += "Harrowed,".format(T.markers[mdict['Credits']])
      if markers != 'Counters:': markers += '\n'
      else: markers = ''
      debugNotify("Finished Adding Markers. Adding stats...", 4)# Debug
      stats = ''
      stats += "Cost: {}. ".format(T.Cost)
      if num(T.Upkeep): stats += "Upkeep: {}.\n".format(T.Upkeep)
      if num(T.Production): stats += "Production: {}.\n".format(T.Production)
      if num(T.Bullets): stats += "Bullets: {}.".format(T.Bullets)
      if num(T.Influence): stats += "Influence: {}.".format(T.Influence)
      if num(T.Control): stats += "CP: {}.".format(T.Control)
      if includeText: cText = '\n' + T.Text
      else: cText = ''
      debugNotify("Finished Adding Stats. Going to choice...", 4)# Debug
      choiceTXT = "{}\n{}\n{}{}{}".format(T.name,T.Type,markers,stats,cText)
      targetChoices.append(choiceTXT)
   debugNotify("<<< makeChoiceListfromCardList()", 3)
   return targetChoices

#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------

def TrialError(group, x=0, y=0): # Debugging
   global debugVerbosity
   mute()
   # Testing Corner
   #findTarget('Targeted-atVehicle_and_Fighter_or_Character_and_nonWookie')
   #BotD.moveToTable(0,0)
   # End Testing Corner
   #notify("### Setting Debug Verbosity")
   if debugVerbosity >=0:
      if debugVerbosity == 0:
         debugVerbosity = 1
         #ImAProAtThis() # At debug level 1, we also disable all warnings
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
