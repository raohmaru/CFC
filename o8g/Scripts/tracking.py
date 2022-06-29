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

#------------------------------------------------------------------------------
# Variables
#------------------------------------------------------------------------------

track_event_tmpl = """{{
   "type": "event",
   "payload": {{
      "website": "{0}",
      "hostname": "{1}",
      "language": "{2}",
      "screen": "{3}x{4}",
      "url": "/{5}{8}",
      "event_type": "{6}",
      "event_value": "{7}"
   }}
}}"""

track_page_tmpl = """{{
   "type": "pageview",
   "payload": {{
      "website": "{0}",
      "hostname": "{1}",
      "language": "{2}",
      "screen": "{3}x{4}",
      "url": "/{5}/{6}",
      "referrer": ""
   }}
}}"""


#------------------------------------------------------------------------------
# Tracking functions
#------------------------------------------------------------------------------

def track_create():
   request = System.Net.WebRequest.CreateHttp("https://umami.raohmaru.com/api/collect")
   request.ContentType = "application/json"
   request.Method = "POST"
   request.Timeout = 3000
   request.UserAgent = "OCTGN/" + version + " (" + System.Environment.OSVersion.VersionString + ") CFC/" + gameVersion
   request.Accept = "*/*"
   return request


def track_send(tmpl, *args):
   if settings["Tracking"] == False:
      return
   request = track_create()
   screenSize = System.Windows.Forms.Screen.PrimaryScreen.Bounds
   hostedGame = Octgn.Program.CurrentHostedGame
   json = tmpl.format(
      WebsiteId,
      "{}:{}".format(hostedGame.Host, hostedGame.Port),
      System.Globalization.CultureInfo.CurrentCulture.ToString(),
      screenSize.Width,
      screenSize.Height,
      hostedGame.Name + "/" + hostedGame.Id.ToString().split("-")[0],
      *args
   )
   debug(">>> track_send({}, {})", json, args)
   streamWriter = System.IO.StreamWriter(request.GetRequestStream())
   streamWriter.Write(json)
   streamWriter.Flush()
   streamWriter.Close()
   try:
      response = request.GetResponseAsync()  # UnwrapPromise[WebResponse]
      # response.Close()
   except SystemError as err:
      debug("{}", err)


def track_event(event, value, url = ""):
   track_send(track_event_tmpl, event, value, url)


def track_page(page = ""):
   track_send(track_page_tmpl, page)
   
   
def track_deck(deck):
   # Qty:  0   1    2    3
   sep = ["", ",", ".", ":"]
   cards = [toBase(c.Gid, 32) for c in deck]
   cardsDict = { i: cards.count(i) for i in cards }
   value = "".join([k + sep[v] for k, v in cardsDict.items()])
   track_event("deck_load", value)

