# Python Scripts for the Card Fighters" Clash definition for OCTGN
# Copyright (C) 2022 Raohmaru

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

#------------------------------------------------------------------------------
# Card attachments
#------------------------------------------------------------------------------

def attach(card, target):
   """
   Attaches a card to another card.
   """
   debug(">>> attachCard()")
   target.target(False)
   backups = getGlobalVar("Backups")
   backups[card._id] = target._id
   setGlobalVar("Backups", backups)
   debugBackups()
   debug("<<< attachCard()")
   

def clearAttachLinks(card):
   """
   This function takes care to discard any attachments of a card that left play.
   It also clear the card from the attach dictionary, if it was itself attached to another card.
   """
   debug(">>> clearAttachLinks({})", card)
   backups = getGlobalVar("Backups")
   card_id = card._id
   # Detaches cards that were attached to the current card
   if card_id in backups.values():
      notify("{} clears all backups of {}.", me, card)
      for id in backups:
         if backups[id] == card_id:
            attcard = Card(id)
            debug("Detaching {} from {}.", attcard, card)
            if attcard in table:
               discard(attcard)
            del backups[id]
   # If the card was an attachment, delete the link
   elif backups.has_key(card_id):
      debug("{} is attached to {}. Detaching it.", card, Card(backups[card_id]))
      del backups[card_id]
   setGlobalVar("Backups", backups)
   debugBackups()   
   debug("<<< clearAttachLinks()")
   

def getAttachments(card):
   """
   Returns a list with all the cards attached to this card.
   """
   debug(">>> getAttachments({})", card)
   backups = getGlobalVar("Backups")
   card_id = card._id
   attachs = []
   for id in backups:
      if backups[id] == card_id:
         attachs.append(Card(id))
   debug("{} has {} cards attached", card, len(attachs))
   return attachs
   

def getAcceptedBackups(card):
   return filter(None, [card.properties["Backup 1"], card.properties["Backup 2"], card.properties["Backup 3"]])
