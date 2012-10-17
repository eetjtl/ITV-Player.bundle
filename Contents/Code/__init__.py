#################################################
#                                               #
# ITV Player Plex v9 Plugin                     #
#                                               #
# Version: 	0.2                                 # 
# Author: 	James Gould                         #
# Contributors:                                 #
# Created: 	08th Sept 2010                      #
# Last Updated: 17th Sept 2010                  #
#                                               #
#################################################

# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from Framework import *

import urllib
from xml.dom import minidom

#################################################
#
#
# Parameters
#
#
#################################################

VIDEO_PREFIX            = "/video/itvplayer"

ITV_URL                 = "http://www.itv.com"
ITV_SD_PLAYER_URL       = "%s/itvplayer/video/?Filter=%%s" % ITV_URL

ITV_API_URL             = "http://mercury.itv.com/api/xml/Dotcom"
ITV_API_TOPTEN_URL      = "%s/Episode/TopTen/?callback=doTopTenProgrammes" % ITV_API_URL
ITV_API_MOSTWATCHED_URL = "%s/Episode/MostWatched/?callback=doMostWatched" % ITV_API_URL
ITV_API_CHANNEL_URL     = "%s/Programme/PerChannel/%%s/?callback=doForChannel" % ITV_API_URL
ITV_API_AZ_URL          = "%s/Programme/SearchAtoZ/% %s/?callback=doSearchAtoZ" % ITV_API_URL
ITV_API_PROGRAM_URL     = "%s/Programme/Index/%%s/?callback=doProgramme" % ITV_API_URL
ITV_API_ALLPROG_URL     = "%s/Programme/PerChannel/all/999/?callback=doPerChannel" % ITV_API_URL

ITV_API_DATE_URL        = "%s/Episode/ByDate/%%s/?callback=doProgrammesByDate" % ITV_API_URL

ITV_SD_THUMB_URL        =""

ITV_XML_NS              = "http://schemas.itv.com/2009/05/Mercury/Common/Domain"
ITV_PROGRAMME_XPATH     = "/d:Response/d:Results/d:Groups/d:Group/d:ProgrammeDetails/d:ProgrammeDetail/d:Programme"
ITV_EPISODE_XPATH       = "/d:Response/d:Results/d:Groups/d:Group/d:ProgrammeDetails/d:ProgrammeDetail/d:Episodes/d:Episode"

NAME                    = L('Title')
VIDEO_TITLE             = L('VideoTitle')

TOP_TEN_TITLE           = "Recommended Programmes"
MOST_WATCHED_TITLE      = "Most Watched Shows"
TV_CHANNELS_TITLE       = "TV Channels"
TV_GENRES_TITLE         = "Genres"
TV_DATE_TITLE           = "Date"
A_Z_TITLE               = "A to Z"
SEARCH_TITLE            = "Search Programmes"
SEARCH_SUBTITLE         = "Search for your Programme"
SEARCH_SUMMARY          = "This lets you search for ITV Programmes"

ART                     = 'art-default.png'
ICON                    = 'icon-default.png'

ITV1_LOGO               = "http://www.itv.com/itv1/2b721613-b35d-41d8-afae-b9cb17c43f2c/PreviewFile.jpg.ashx?q=90&v=1&w=2000"
ITV2_LOGO               = "http://www.itv.com/itv2/40a6e9e0-1a41-40e1-809a-f555f232c93c/PreviewFile.jpg.ashx?q=90&v=1&w=2000"
ITV3_LOGO               = "http://www.itv.com/itv3/1e3d6795-2ea0-4a31-bdf9-e8a407241d0b/PreviewFile.jpg.ashx?q=90&v=1&w=2000"
ITV4_LOGO               = "http://www.itv.com/itv4/3399e40e-f4e1-4eaf-a0e1-43285aa25790/PreviewFile.jpg.ashx?q=90&v=1&w=2000"
CITV_LOGO               = "http://www.itv.com/citv/28688633-3c9e-48af-8c43-117db335332a/PreviewFile.jpg.ashx?q=90&v=1&w=2000"

#################################################



#################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, VIDEO_TITLE, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

#################################################

def MainMenu():
    dir = MediaContainer(viewGroup="List")  
    dir.Append(Function(DirectoryItem(RenderEpisodeList, title = TOP_TEN_TITLE, thumb=R(ICON)), url = ITV_API_TOPTEN_URL))
    dir.Append(Function(DirectoryItem(RenderEpisodeList, title = MOST_WATCHED_TITLE, thumb=R(ICON)), url = ITV_API_MOSTWATCHED_URL))   
    dir.Append(Function(DirectoryItem(AddTVChannels, title = TV_CHANNELS_TITLE, thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(AddDateList, title = TV_DATE_TITLE, thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(AddAToZ, title = A_Z_TITLE, thumb=R(ICON)))) 
    dir.Append(Function(InputDirectoryItem(SearchResults,SEARCH_TITLE,SEARCH_SUBTITLE,summary=SEARCH_SUMMARY, thumb=R(ICON))))
    return dir

#################################################

def SearchResults(sender,query=None):   
    dir = RenderProgramList(sender,url = ITV_API_URL + "/Programme/Search/%s/?callback=doSearch" % String.Quote(query))   
    return dir

#################################################

def AddTVChannels(sender, query = None, url = None, subtitle = None, sort_list = None, thumb_url = ICON, player_url = ITV_SD_PLAYER_URL):
    dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Info")
    dir.Append(Function(DirectoryItem(RenderProgramList, title = "ITV1", thumb = ITV1_LOGO), url = ITV_API_CHANNEL_URL % 'ITV1'))
    dir.Append(Function(DirectoryItem(RenderProgramList, title = "ITV2", thumb = ITV2_LOGO), url = ITV_API_CHANNEL_URL % 'ITV2'))
    dir.Append(Function(DirectoryItem(RenderProgramList, title = "ITV3", thumb = ITV3_LOGO), url = ITV_API_CHANNEL_URL % 'ITV3'))
    dir.Append(Function(DirectoryItem(RenderProgramList, title = "ITV4", thumb = ITV4_LOGO), url = ITV_API_CHANNEL_URL % 'ITV4'))
    dir.Append(Function(DirectoryItem(RenderProgramList, title = "CITV", thumb = CITV_LOGO), url = ITV_API_CHANNEL_URL % 'CITV'))
    return dir

#################################################

def AddDateList(sender, query = None, url = None, subtitle = None, sort_list = None, thumb_url = ICON, player_url = ITV_SD_PLAYER_URL):
   dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Info")
   
   today = Datetime.Now()
   
   dir.Append(Function(DirectoryItem(RenderEpisodeList, title = "Today", thumb=''), url = ITV_API_DATE_URL % today.strftime("%Y/%m/%d")))
   date = (today+Datetime.Delta(days = -1))
   dir.Append(Function(DirectoryItem(RenderEpisodeList, title = "Yesterday", thumb=''), url = ITV_API_DATE_URL % date.strftime("%Y/%m/%d")))
   
   
   for number in range (2, 31):
      date = (today+Datetime.Delta(days = -number))
      dir.Append(Function(DirectoryItem(RenderEpisodeList, title = date.strftime("%a, %d %b %Y"), thumb=''), url = ITV_API_DATE_URL % date.strftime("%Y/%m/%d")))
   return dir

#################################################

def RenderProgramList(sender, url = None, sort = None):

   # this function generates the highlights, most popular and sub-category lists from an RSS feed
 
   dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Info")
   Log(url)
   content = XML.ElementFromURL(url, isHTML=False, errors='ignore', cacheTime=1800)
   programmes = content.xpath(ITV_PROGRAMME_XPATH,namespaces={'d' : ITV_XML_NS})

   if len( programmes ) < 1:
    return MessageContainer(
        "No Programmes Found",
        "No Programmes have been found matching your search\nPlease try again."
   )
   
   progs = []
   for p in programmes:
      progs.append(constructProgramme(p))
      
   progs.sort(key=lambda x: x.title)
      
   for prog in progs:
      dir.Append(Function(DirectoryItem(RenderEpisodeList, title = prog.title + ' [' + prog.additionalInfo.episodeCount + ' episodes]', thumb = prog.imageUri, summary = prog.summary() ), url = ITV_API_PROGRAM_URL % prog.id))
            
   if len(dir) <= 0:
      return MessageContainer(
        "No Programmes Found",
        "No Programmes have been found matching your search\nPlease try again."
       )
   
   return dir

#################################################

def RenderEpisodeList(sender, url = None):
   
   dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Info")
   content = XML.ElementFromURL(url, isHTML=False, errors='ignore', cacheTime=1800)

   episodes = content.xpath(ITV_EPISODE_XPATH,namespaces={'d' : ITV_XML_NS})
   
   if len( episodes ) < 1:
    return MessageContainer(
        "No Episodes Found",
        "No Episodes have been found matching your search\nPlease try again."
    )
   test = None
   for e in episodes:
      episode = constructEpisode(e)
      dir.Append(WebVideoItem(url = ITV_SD_PLAYER_URL % episode.id , title = episode.title, subtitle =  episode.subtitle(), thumb = episode.posterFrameUri, summary = episode.summary(), duration = int(episode.duration) * 60 * 1000))  
   
  
   
   return dir
   

#################################################

def AddAToZ(sender, query = None):
  # returns an A-Z list of links to an XML feed for each letter (plus 0-9)
  dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Menu")

  for letter in range (65, 91):
    thisLetter = chr(letter)
    dir.Append(Function(DirectoryItem(RenderProgramList, title = thisLetter, subtitle = sender.itemTitle, thumb=''), url = ITV_API_AZ_URL % thisLetter))
  dir.Append(Function(DirectoryItem(RenderProgramList, title = "0-9", subtitle = sender.itemTitle, thumb=''), url = ITV_API_AZ_URL % "0123456789"))

  return dir

#################################################

def constructProgramme( element ):
   return Programme(
      id                         = element.xpath('./d:Id',namespaces={'d' : ITV_XML_NS})[0].text,
      title                      = element.xpath('./d:Title',namespaces={'d' : ITV_XML_NS})[0].text,
      pageUri                    = element.xpath('./d:PageUri',namespaces={'d' : ITV_XML_NS})[0].text,
      imageUri                   = element.xpath('./d:ImageUri',namespaces={'d' : ITV_XML_NS})[0].text,
      genres                     = element.xpath('./d:Genres',namespaces={'d' : ITV_XML_NS})[0].text,
      shortSynopsis              = element.xpath('./d:ShortSynopsis',namespaces={'d' : ITV_XML_NS})[0].text,
      longSynopsis               = element.xpath('./d:LongSynopsis',namespaces={'d' : ITV_XML_NS})[0].text,
      additionInfoText           = element.xpath('./d:AdditionalInfo/d:Text',namespaces={'d' : ITV_XML_NS})[0].text,
      additionInfoUri            = element.xpath('./d:AdditionalInfo/d:Uri',namespaces={'d' : ITV_XML_NS})[0].text,
      additionInfoEpisodeCount   = element.xpath('./d:AdditionalInfo/d:EpisodeCount',namespaces={'d' : ITV_XML_NS})[0].text,
      additionHeaderText         = element.xpath('./d:AdditionalInfo/d:AdditionalHeaderText',namespaces={'d' : ITV_XML_NS})[0].text,
      additionalSynopsisText     = element.xpath('./d:AdditionalInfo/d:AdditionalSynopsisText',namespaces={'d' : ITV_XML_NS})[0].text,
      channel                    = element.xpath('./d:AdditionalInfo/d:Channel',namespaces={'d' : ITV_XML_NS})[0].text,
      latestEpisodeId            = element.xpath('./d:LatestEpisode/d:Id',namespaces={'d' : ITV_XML_NS})[0].text,
      latestEpisodeDate          = element.xpath('./d:LatestEpisode/d:Date',namespaces={'d' : ITV_XML_NS})[0].text,
      latestEpisodeTime          = element.xpath('./d:LatestEpisode/d:Time',namespaces={'d' : ITV_XML_NS})[0].text        
   )


def constructEpisode( element ):
   return Episode(
      id                         = element.xpath('./d:Id',namespaces={'d' : ITV_XML_NS})[0].text,
      title                      = element.xpath('./d:Title',namespaces={'d' : ITV_XML_NS})[0].text,
      episodeNumber              = element.xpath('./d:EpisodeNumber',namespaces={'d' : ITV_XML_NS})[0].text,
      genres                    = element.xpath('./d:Genres',namespaces={'d' : ITV_XML_NS})[0].text,
      duration                   = element.xpath('./d:Duration',namespaces={'d' : ITV_XML_NS})[0].text,
      lastBroadcast              = element.xpath('./d:LastBroadcast',namespaces={'d' : ITV_XML_NS})[0].text,
      lastBroadcastTime          = element.xpath('./d:LastBroadcastTime',namespaces={'d' : ITV_XML_NS})[0].text,
      daysRemaining              = element.xpath('./d:DaysRemaining',namespaces={'d' : ITV_XML_NS})[0].text,
      shortSynopsis              = element.xpath('./d:ShortSynopsis',namespaces={'d' : ITV_XML_NS})[0].text,
      LongSynopsis               = element.xpath('./d:LongSynopsis',namespaces={'d' : ITV_XML_NS})[0].text,
      posterFrameUri             = element.xpath('./d:PosterFrameUri',namespaces={'d' : ITV_XML_NS})[0].text,
      channel                    = element.xpath('./d:AdditionalInfo/d:Channel',namespaces={'d' : ITV_XML_NS})[0].text,
      channelLogoUrl             = element.xpath('./d:AdditionalInfo/d:ChannelLogoUrl',namespaces={'d' : ITV_XML_NS})[0].text,
      dentonId                   = element.xpath('./d:Denton/d:DentonId',namespaces={'d' : ITV_XML_NS})[0].text,
      customerRating             = element.xpath('./d:Denton/d:Rating',namespaces={'d' : ITV_XML_NS})[0].text   
   )
   

    