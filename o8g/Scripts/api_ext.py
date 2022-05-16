# Python Scripts for the Card Fighters" Clash definition for OCTGN
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
# Extended API that invokes methods from OCTGN C# API
#---------------------------------------------------------------------------

try:
   import clr
   # Start to hack :)
   clr.AddReference("Octgn")
   clr.AddReference("Octgn.Core")
   clr.AddReference("Octgn.JodsEngine") # 3.4.350.0
   import Octgn
   import System
except (IOError, ImportError):
   settings["ExtAPI"] = False
   whisper("There was an error while starting the game and some functionalities won't be available.\nPlease restart OCTGN.")
   
class ExtendedApi(object):
# An extended API with methods that directly call C# methods from IronPython
   def __init__(self):
      self._game = Octgn.Program.GameEngine.Definition
      self._gameMethods = Octgn.Core.DataExtensionMethods.GameExtensionMethods
      self._cardMethods = Octgn.Core.DataExtensionMethods.CardExtensionMethods
      self._deckMethods = Octgn.Core.DataExtensionMethods.DeckExtensionMethods
      
   @property
   def game(self): return self._game
   
   def getSets(self):
      """
      Gets a list with the sets of the game.
      Returns: [Octgn.DataNew.Entities.Set]
      """
      sets = Octgn.Core.DataManagers.SetManager.Get().Sets
      return [set for set in sets]
      
      
   def getSetByModel(self, setModel):
      """
      Gets a set by its GUID.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._gameMethods.GetSetById(self._game, Guid.Parse(setModel))
      
      
   def getSetByCardData(self, cardData):
      """
      Gets a set by the given card data.
      Returns: Octgn.DataNew.Entities.Set
      """
      return self._cardMethods.GetSet(cardData)
      
      
   def getCardById(self, cardId):
      """
      Gets a card by its internal id.
      Examples: _extapi.getCardById(card._id)
      Returns: Octgn.Play.Card
      """
      return Octgn.Play.Card.Find(cardId)
      
      
   def getCardDataByName(self, cardName):
      """
      Gets a card data by its name.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardByName(self._game, cardName)
      
      
   def getCardDataByModel(self, cardModel):
      """
      Gets a card data by its GUID.
      Returns: Octgn.DataNew.Entities.Card
      """
      return self._gameMethods.GetCardById(self._game, Guid.Parse(cardModel))
      
      
   def getCardIdentityById(self, cardId):
      """
      Gets a card identity by its internal id.
      Examples: _extapi.getCardIdentityById(card._id)
      Returns: Octgn.Play.CardIdentity
      """
      return Octgn.Play.CardIdentity.Find(cardId)
      
      
   def getCardDataById(self, cardId):
      """
      Gets a card data by its internal id.
      Examples: _extapi.getCardDataById(card._id)
      Returns: Octgn.DataNew.Entities.Card
      """
      card = self.getCardIdentityById(cardId)
      if card is None:
         return None
      return card.Model
      
      
   def getCardProperties(self, cardData, propset = ""):
      """
      Gets all properties from a card data given the property set name (aka alternate).
      Returns: dict
      """
      cardPropertySet = cardData.PropertySets[propset]
      props = {}
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      for k in cardPropertySet.Properties.Keys:
         props[k.Name] = cardPropertySet.Properties.Item[k]
      return props
      
      
   def getCardProperty(self, cardData, propName, propset = ""):
      """
      Gets a value of a property from a card data given the property set name (aka alternate).
      Returns: str
      """
      cardPropertySet = cardData.PropertySets[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         return cardPropertySet.Properties.Item[prop[0]]
      return None
      
      
   def setCardProperty(self, cardData, propName, value, propset = ""):
      """
      Sets the value of a property of a card data given the property set name (aka alternate).
      """
      cardPropertySet = cardData.PropertySets[propset]
      # Keys are objects Octgn.DataNew.Entities.PropertyDef
      prop = [p for p in cardPropertySet.Properties.Keys if p.Name == propName]
      if len(prop) > 0:
         cardPropertySet.Properties.Item[prop[0]] = value
         
         
   def getCardProxyURI(self, set, cardData):
      """
      Gets the absolute path to the proxy image of the given card data.
      Returns: str
      """
      return System.Uri(Path.Combine(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png"))
         
         
   def generateProxy(self, cardData, alternate):
      """
      Generates and writes into the disk a new proxy image for the given property set (aka alternate) name.
      """
      currAlternate = cardData.Alternate
      cardData.Alternate = alternate
      set = self.getSetByCardData(cardData)
      uri = self.getCardProxyURI(set, cardData)
      files = Directory.GetFiles(set.ProxyPackUri, self._cardMethods.GetImageUri(cardData) + ".png")
      if files.Length == 0:
         cropPath = Path.Combine(Path.Combine(set.ImagePackUri, "Crops"))
         crop = None
         if Directory.Exists(cropPath):
            crops = Directory.GetFiles(cropPath, cardData.ImageUri + ".jpg")
            try:
               if crops.Length == 0:
                  self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath)
               else:
                  self._gameMethods.GetCardProxyDef(self._game).SaveProxyImage(self._cardMethods.GetProxyMappings(cardData), uri.LocalPath, crops[0])
            except EnvironmentError:
               self.warning("An error occurred while generating the proxy image.")
      cardData.Alternate = currAlternate
      
      
   def addMessage(self, message):
      """
      Uses internal C# method to publish messages with formatted text.
      """
      try:
         Octgn.Program.GameMess.AddMessage(message)
      except AttributeError:
         whisper(message.Message)
      
      
   def warning(self, str):
      self.addMessage(Octgn.Core.Play.WarningMessage(replIdsWithNames(str), {}))
      
            
   def system(self, str):
      self.addMessage(Octgn.Core.Play.SystemMessage(replIdsWithNames(str), {}))
      
      
   def whisper(self, str, color = Colors.Black, bold = False):
      msg = replIdsWithNames(str)
      dummyPlayer = DummyPlayer(color)
      if bold:
         dummyPlayer.name = msg
         msg = ""
      update()  # To make next function work if this has been invoked from a remote call
      self.addMessage(Octgn.Core.Play.PlayerEventMessage(dummyPlayer, msg, {}))
      del dummyPlayer
      
      
   def notify(self, str, color = Colors.Black, bold = False):
      self.whisper(str, color, bold)
      if len(players) > 1:
         remoteCall(players[1], "_extapi_whisper", [str, color, bold])
         
         
   def loadDeck(self, path):
      """
      Creates a Deck object from the given deck file.
      Returns: List[Octgn.DataNew.Entities.MultiCard]
      """
      # Octgn.DataNew.Entities.Deck
      deck = self._gameMethods.CreateDeck(_extapi._game)
      deck = self._deckMethods.Load(deck, _extapi._game, path)
      if self._deckMethods.CardCount(deck) > 0:
         return deck.Sections[0].Cards
         
         
   def getDecksPath(self):
      return self._gameMethods.GetDefaultDeckPath(self._game)
         
         
   def getPreBuiltDecksPath(self):
      # https://github.com/octgn/OCTGN/blob/437b67efaec15729178523fe61de2eae29a8dded/octgnFX/Octgn.JodsEngine/Play/PlayWindow.xaml.cs#L511
      return Path.Combine(self._game.InstallPath, "Decks")
      
      
   def getAppResource(self, file):
      """
      Gets the path of a resource in the app installation folder.
      """
      return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Resources", file)
      

if settings["ExtAPI"]:
   # Make it global
   _extapi = ExtendedApi()
   # Alias to use _extapi.whisper from remoteCall()
   _extapi_whisper = _extapi.whisper

