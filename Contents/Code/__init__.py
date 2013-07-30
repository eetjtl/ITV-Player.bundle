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

import MediaItems
import urllib
import re
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

ITV_API_URL             = "http://www.itv.com/ITVPlayer/Top10Videos/?ViewType=5"
ITV_API_POPULAR_URL     = "https://www.itv.com/itvplayer/categories/browse/popular/catch-up"

ITV_API_MOSTWATCHED_URL = "%s/Episode/MostWatched/?callback=doMostWatched" % ITV_API_URL
ITV_API_CHANNEL_URL     = "%s/Programme/PerChannel/%%s/?callback=doForChannel" % ITV_API_URL
ITV_API_AZ_URL          = "%s/Programme/SearchAtoZ/% %s/?callback=doSearchAtoZ" % ITV_API_URL
ITV_API_PROGRAM_URL     = "%s/Programme/Index/%%s/?callback=doProgramme" % ITV_API_URL
ITV_API_ALLPROG_URL     = "%s/Programme/PerChannel/all/999/?callback=doPerChannel" % ITV_API_URL

ITV_API_DATE_URL        = "%s/Episode/ByDate/%%s/?callback=doProgrammesByDate" % ITV_API_URL

ITV_SD_THUMB_URL        =""


ITV_PROGRAMME_XPATH     = "//div[@id='categories-content']/div[@class='item-list']/ul/li"
ITV_EPISODE_XPATH       = "//div[@class='view-content']/div[@class='views-row']"

NAME                    = L('Title')
VIDEO_TITLE             = L('VideoTitle')

POPULAR_TITLE           = "Most Popular Programmes"
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

	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	
	DirectoryObject.thumb = R(ICON)
	
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:17.0) Gecko/20100101 Firefox/17.0'

#################################################

@handler('/video/itv', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)
		
	oc.add(
		DirectoryObject(
			key=Callback(RenderProgramList, url=ITV_API_POPULAR_URL),
			title=POPULAR_TITLE,
			thumb=R(ICON),
		)
	)
	
	#oc.add(Function(DirectoryItem(RenderEpisodeList, title = MOST_WATCHED_TITLE, thumb=R(ICON)), url = ITV_API_MOSTWATCHED_URL))   
	#oc.add(Function(DirectoryItem(AddTVChannels, title = TV_CHANNELS_TITLE, thumb=R(ICON))))
	#oc.add(Function(DirectoryItem(AddDateList, title = TV_DATE_TITLE, thumb=R(ICON))))
	#oc.add(Function(DirectoryItem(AddAToZ, title = A_Z_TITLE, thumb=R(ICON)))) 
	#oc.add(Function(InputDirectoryItem(SearchResults,SEARCH_TITLE,SEARCH_SUBTITLE,summary=SEARCH_SUMMARY, thumb=R(ICON))))
	
	return oc

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

def RenderProgramList(url=None, sort=None):

# this function generates the highlights, most popular and sub-category lists from an RSS feed

	oc = ObjectContainer()
		
	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
	programmes = content.xpath(ITV_PROGRAMME_XPATH)

	if len( programmes ) < 1:
		return MessageContainer(
			"No Programmes Found",
			"No Programmes have been found matching your search\nPlease try again."
		)

	progs = []
	for p in programmes:
		progs.append(constructProgramme(p))
		
	for prog in progs:
	
		title = prog.title
		if (prog.additionalInfo.episodeCount is not None):
			title += ' [' + str(prog.additionalInfo.episodeCount) + ']'
		
		oc.add(
			DirectoryObject(
				key = Callback(RenderEpisodeList, url = ITV_URL + prog.pageUri),
				title = title,
				thumb = prog.imageUri,
			)
		)

	if len(oc) <= 0:
		return MessageContainer(
			"No Programmes Found",
			"No Programmes have been found matching your search\nPlease try again."
		)

	return oc

#################################################

def RenderEpisodeList(url=None):

	oc = ObjectContainer()
	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)

	episodes = content.xpath(ITV_EPISODE_XPATH)

	Log(len(episodes))
	if len( episodes ) < 1:
		return MessageContainer(
			"No Episodes Found",
			"No Episodes have been found matching your search\nPlease try again."
		)
		
	test = None
	for e in episodes:
		episode = constructEpisode(e)
		Log("Adding...." + ITV_URL + episode.id)
		oc.add(
			VideoClipObject(
				url = ITV_URL + episode.id,
				title = episode.title + ' (Season: ' + episode.seasonNumber + ", Ep: " + episode.episodeNumber +")",
				#subtitle =  episode.subtitle(),
				thumb = episode.posterFrameUri,
				summary = episode.summary(),
				duration = int(episode.duration) * 60 * 1000
			)
		)
		
	Log("Returning")

	return oc


#################################################
def AddAToZ(sender, query=None):

	# returns an A-Z list of links to an XML feed for each letter (plus 0-9)
	dir = MediaContainer(title1 = sender.title2, title2 = sender.itemTitle, viewGroup = "Menu")

	for letter in range (65, 91):
		thisLetter = chr(letter)
		dir.Append(Function(DirectoryItem(RenderProgramList, title = thisLetter, subtitle = sender.itemTitle, thumb=''), url = ITV_API_AZ_URL % thisLetter))
		
	dir.Append(Function(DirectoryItem(RenderProgramList, title = "0-9", subtitle = sender.itemTitle, thumb=''), url = ITV_API_AZ_URL % "0123456789"))

	return dir

#################################################
def constructProgramme(element):
	
	imageUri = ''
	if len(element.xpath('.//img/@src')) > 0:
		imageUri = element.xpath('.//img/@src')[0]
		
	additionInfoEpisodeCount = None
	if len(element.xpath(".//span[@class='episode-free']")) > 0:
		additionInfoEpisodeCount = element.xpath(".//span[@class='episode-free']")[0].text
		
	return MediaItems.Programme(
		title                      = element.xpath(".//div[@class='programme-title cell-title']/a")[0].text,
		pageUri                    = element.xpath(".//div[@class='programme-title cell-title']/a/@href")[0],
		imageUri                   = imageUri,
		#genres                     = element.xpath('./d:Genres',namespaces={'d' : ITV_XML_NS})[0].text,
		shortSynopsis              = '',
		#longSynopsis               = element.xpath('./d:LongSynopsis',namespaces={'d' : ITV_XML_NS})[0].text,
		#additionInfoText           = element.xpath('./d:AdditionalInfo/d:Text',namespaces={'d' : ITV_XML_NS})[0].text,
		#additionInfoUri            = element.xpath('./d:AdditionalInfo/d:Uri',namespaces={'d' : ITV_XML_NS})[0].text,
		additionInfoEpisodeCount   = additionInfoEpisodeCount,
		#additionHeaderText         = element.xpath('./d:AdditionalInfo/d:AdditionalHeaderText',namespaces={'d' : ITV_XML_NS})[0].text,
		#additionalSynopsisText     = element.xpath('./d:AdditionalInfo/d:AdditionalSynopsisText',namespaces={'d' : ITV_XML_NS})[0].text,
		#channel                    = element.xpath('./d:AdditionalInfo/d:Channel',namespaces={'d' : ITV_XML_NS})[0].text,
		#latestEpisodeId            = element.xpath('./d:LatestEpisode/d:Id',namespaces={'d' : ITV_XML_NS})[0].text,
		latestEpisodeDate          = '',
		latestEpisodeTime          = '',
	)

def constructEpisode(element):
	
	return MediaItems.Episode(
		id                         = element.xpath(".//div[contains(@class, 'node-episode')]/a[1]/@href")[0],
		title                      = element.xpath("//h2[@class='title episode-title']")[0].text,
		seasonNumber               = element.xpath(".//div[contains(@class, 'field-name-field-season-number')]//text()")[0],
		episodeNumber              = element.xpath(".//div[contains(@class, 'field-name-field-episode-number')]//text()")[0],
		#genres                     = element.xpath('./d:Genres',namespaces={'d' : ITV_XML_NS})[0].text,
		duration                   = re.search("(\\d*)",element.xpath(".//div[contains(@class, 'field-name-field-duration')]//text()")[0].strip()).groups()[0],
		lastBroadcast              = element.xpath(".//div[contains(@class, 'field-name-field-broadcastdate')]//span/@content")[0],
		#lastBroadcastTime          = element.xpath('./d:LastBroadcastTime',namespaces={'d' : ITV_XML_NS})[0].text,
		daysRemaining              = re.search("(\\d*)",element.xpath(".//div[@class='offer-duration']")[0].text.strip()).groups()[0],
		shortSynopsis              = element.xpath(".//div[contains(@class,'field-name-field-short-synopsis')]//text()")[0],
		#LongSynopsis               = element.xpath(".//div[contains(@class,'field-name-field-short-synopsis')]")[0].text,
		posterFrameUri             = element.xpath(".//div[contains(@class,'field-name-field-image')]//img/@src")[0],
		#channel                    = element.xpath('./d:AdditionalInfo/d:Channel',namespaces={'d' : ITV_XML_NS})[0].text,
		#channelLogoUrl             = element.xpath('./d:AdditionalInfo/d:ChannelLogoUrl',namespaces={'d' : ITV_XML_NS})[0].text,
		#dentonId                   = element.xpath('./d:Denton/d:DentonId',namespaces={'d' : ITV_XML_NS})[0].text,
		#customerRating             = element.xpath('./d:Denton/d:Rating',namespaces={'d' : ITV_XML_NS})[0].text   
	)

