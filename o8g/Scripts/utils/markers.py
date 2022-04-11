# Python Scripts for the Card Fighters' Clash definition for OCTGN
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

#---------------------------------------------------------------------------
# Marker functions
#---------------------------------------------------------------------------

def hasMarker(card, marker):
   if not isCard(card):
      return False
   return MarkersDict[marker] in card.markers
      
      
def getMarker(card, mkname):
   return card.markers[MarkersDict[mkname]]

      
def changeMarker(cards, marker, question = None, amount = None):
   """
   Changes the number of markers in one or more cards.
   """
   n = 0
   if not amount:
      for c in cards:
         if c.markers[marker] > n:
           n = c.markers[marker]
      amount = askInteger(question, n)
   if amount == None:
      return
   if marker == MarkersDict["BP"]:
      amount = roundBP(amount)
   for c in cards:
      n = c.markers[marker]
      c.markers[marker] = amount
      diff = amount-n
      if diff >= 0:
         diff = "+" + str(diff)
      notify("{} sets {}'s {} to {} ({}).".format(getSourceController(), c, marker[0], amount, diff))


def setMarker(card, mkname, qty = 1):
   card.markers[MarkersDict[mkname]] = qty


def addMarker(card, mkname, qty = 1):
   card.markers[MarkersDict[mkname]] += qty


def removeMarker(card, mkname):
   """
   Removes all marker of the given name from a card.
   """
   if MarkersDict[mkname] in card.markers:
      setMarker(card, mkname, 0)


def toggleMarker(card, mkname):
   if MarkersDict[mkname] in card.markers:
      removeMarker(card, mkname)
   else:
      setMarker(card, mkname, 1)
      
      
def modBP(card, qty, mode = None):
   if mode == RS_MODE_EQUAL:
      changeMarker([card], MarkersDict["BP"], amount = qty)
   elif qty >= 0:
      plusBP([card], amount = qty)
   else:
      minusBP([card], amount = -qty)


def roundBP(n):
   """
   Rounds the number by the hundreds.
   """
   return int(round(n / 100.0)) * 100
