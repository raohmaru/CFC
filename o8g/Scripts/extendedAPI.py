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
# Extended API
#---------------------------------------------------------------------------

try:
   import clr
   # Start to hacking :)
   clr.AddReference("Octgn")
   clr.AddReference("Octgn.Core")
   # clr.AddReference("Octgn.DataNew")
   import Octgn
   import System

except:
   automations['ExtAPI'] = False
   
class ExtendedApi(object):
# An extended API with methods that directly call C# methods
   def __init__(self):
      self._game = Octgn.Program.GameEngine.Definition  # The game instance
      self._gameMethods = Octgn.Core.DataExtensionMethods.GameExtensionMethods
      self._cardMethods = Octgn.Core.DataExtensionMethods.CardExtensionMethods
      
   @property
   def game(self): return self._game
   
   def getSets(self):
      """Gets a list with the sets of the game.
      Returns: [Octgn.DataNew.Entities.Set]
      """
      sets = Octgn.Core.DataManagers.SetManager.Get().Sets
      return [set for set in sets]
      
   def getSetByModel(self, setModel):
      """Gets a set by its GUID.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._gameMethods.GetSetById(self._game, Guid.Parse(setModel))
      
   def getSetByCardData(self, cardData):
      """Gets a set by the given card data.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._cardMethods.GetSet(cardData)
      
   def getCardById(self, cardId):
      """Gets a card by its internal id.
      Examples: _extapi.getCardById(card._id)
      Returns: Octgn.Play.Card
      """
      return Octgn.Play.Card.Find(cardId)
      
   def getCardDataByName(self, cardName):
      """Gets a card data by its name.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardByName(self._game, cardName)
      
   def getCardDataByModel(self, cardModel):
      """Gets a card data by its GUID.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardById(self._game, Guid.Parse(cardModel))
      
   def getCardDataById(self, cardId):
      """Gets a card data by its internal id.
      Examples: _extapi.getCardDataById(card._id)
      Returns: Octgn.DataNew.Entities.Card
      """
      card = Octgn.Play.CardIdentity.Find(cardId)
      if card is None:
         return None
      return card.Model
      
   def getCardProperty(self, cardData, propName, propset=''):
      """Gets a value of a property from a card data given the property set name (aka alternate).
      Returns: str
      """
      cardPropertySet = cardData.Properties[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         return cardPropertySet.Properties.Item[prop[0]]
      return None
      
   def setCardProperty(self, cardData, propName, value, propset=''):
      """Sets the value of a property of a card data given the property set name (aka alternate).
      """
      cardPropertySet = cardData.Properties[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         cardPropertySet.Properties.Item[prop[0]] = value
         
   def getCardProxyUri(self, set, cardData):
      """Gets the absolute path to the proxy image of the given card data.
      Returns: str
      """
      return System.Uri(Path.Combine(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png"))
         
   def generateProxy(self, cardData, alternate):
      """Generates and writes into the disk a new proxy image for the given property set (aka alternate) name.
      """
      currAlternate = cardData.Alternate
      cardData.Alternate = alternate
      set = self.getSetByCardData(cardData)
      uri = self.getCardProxyUri(set, cardData)
      files = Directory.GetFiles(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png")
      if files.Length == 0:
         cropPath = Path.Combine(Path.Combine(set.ImagePackUri, "Crops"))
         crop = None
         if Directory.Exists(cropPath):
            crops = Directory.GetFiles(cropPath, cardData.ImageUri + ".jpg")
            if crops.Length == 0:
               self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath)
            else:
               self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath, crops[0])
      cardData.Alternate = currAlternate
   
if automations['ExtAPI']:
   _extapi = ExtendedApi()
