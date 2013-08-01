#################################################
#                                               #
# ITV Player Plex Plugin                        #
#                                               #
# Version: 	0.5                                 # 
# Created: 	08th Sept 2010                      #
# Last Updated: 01th Aug 2013                   #
#                                               #
#################################################

import MediaItems
import urllib
import re
import datetime

from xml.dom import minidom

#################################################
#
#
# Parameters
#
#
#################################################

VIDEO_PREFIX            = "/video/itvplayer"
NAME                    = L('Title')
ART                     = 'art-2013.jpg'
ICON                    = 'icon-2013.png'


ITV_URL                 = "http://www.itv.com"
ITV_POPULAR_URL         = "https://www.itv.com/itvplayer/categories/browse/popular/catch-up"
ITV_GENRE_POPULAR_URL   = "https://www.itv.com/itvplayer/categories/%s/popular/catch-up"
ITV_AZ_URL              = "https://www.itv.com/itvplayer/a-z/%s"
ITV_DATE_URL            = "https://www.itv.com/itvplayer/by-day/%s"
ITV_SEARCH_URL          = "https://www.itv.com/itvplayer/search/term/%s/catch-up"

ITV_PROGRAMME_XPATH     = "//div[@id='categories-content']/div[@class='item-list']/ul/li"
ITV_EPISODE_XPATH       = "//div[@class='view-content']/div[@class='views-row']"
ITV_SEARCH_XPATH        = "//div[@class='search-results-wrapper']/div[@class='search-wrapper']"


VIDEO_TITLE             = L('VideoTitle')
POPULAR_TITLE           = "Most Popular Programmes"
MOST_WATCHED_TITLE      = "Most Watched Shows"
TV_CHANNELS_TITLE       = "TV Channels"
TV_GENRES_TITLE         = "Genres"
TV_DATE_TITLE           = "Browse by Date"
A_Z_TITLE               = "A to Z"
SEARCH_TITLE            = "Search Programmes"
SEARCH_SUBTITLE         = "Search for your Programme"
SEARCH_SUMMARY          = "This lets you search for ITV Programmes"

ITV1_LOGO               = "http://thumbs.tvgenius.net/512x512/bds-itv.jpg"
ITV2_LOGO               = "http://thumbs.tvgenius.net/512x512/bds-itv2.jpg"
ITV3_LOGO               = "http://thumbs.tvgenius.net/512x512/bds-itv3.jpg"
ITV4_LOGO               = "http://thumbs.tvgenius.net/512x512/bds-itv4.jpg"
CITV_LOGO               = "http://thumbs.tvgenius.net/512x512/bds-citv.jpg"

#################################################

def Start():
	
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')
	Plugin.AddViewGroup('MediaPreview', viewMode='MediaPreview', mediaType='items')
	
	DirectoryObject.thumb = R(ICON)
	
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:17.0) Gecko/20100101 Firefox/17.0'

#################################################

@handler('/video/itv', NAME, thumb=ICON, art=ART)
def VideoMainMenu():

	oc = ObjectContainer(no_cache=True)
		
	oc.add(
		DirectoryObject(
			key=Callback(RenderProgramList, url=ITV_POPULAR_URL, parent_name=oc.title1, section_name=POPULAR_TITLE),
			title=POPULAR_TITLE,
			summary="Browse the most popular programmes available on catchup across all the ITV channels.",
			thumb=R(ICON),
		)
	)
	
	oc.add(
		DirectoryObject(
			key=Callback(AddGenres, parent_name=oc.title1),
			title=TV_GENRES_TITLE,
			summary="Browse for programmes available on catchup by genre.",
			thumb=R(ICON),
		)
	)


	oc.add(
		DirectoryObject(
			key=Callback(AddTVChannels, parent_name=oc.title1),
			title=TV_CHANNELS_TITLE,
			summary="Browse for programmes available on catchup by channel.",
			thumb=R(ICON),
		)
	)

	oc.add(
		DirectoryObject(
			key=Callback(AddDateList, parent_name=oc.title1),
			title=TV_DATE_TITLE,
			summary="Browse the last 30 days of programmes.",
			thumb=R(ICON),
		)
	)

	oc.add(
		InputDirectoryObject(
			key=Callback(RenderSearchResults, parent_name=oc.title1),
			title=SEARCH_TITLE,
			summary="Search for TV programmes",
			thumb=R(ICON),
			prompt="Enter search term"
		)
	)
		
	return oc


#################################################
def AddGenres(parent_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=TV_GENRES_TITLE)
	
	genres = [
		['Children','children'],
		['Comedy','comedy'],
		['Drama & Soaps','drama-soaps'],
		['Entertainment','entertainment'],
		['Factual','factual'],
		['Films','films'],
		['Lifestyle','lifestyle'],
		['Music','music'],
		['News & Weather','news-weather'],
		['Sport','sport'],
	]
	
	for genre in genres:
	
		oc.add(
			DirectoryObject(
				key=Callback(RenderProgramList, url=ITV_GENRE_POPULAR_URL % genre[1], sort_by_name=True, parent_name=oc.title2, section_name=genre[0]),
				title=genre[0],
			)
		)

	return oc		
	
#################################################
def AddTVChannels(parent_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=TV_CHANNELS_TITLE)
	
	channels = [
		['ITV','itv',ITV1_LOGO],
		['ITV 2','itv2',ITV2_LOGO],
		['ITV 3','itv3',ITV3_LOGO],
		['ITV 4','itv4',ITV4_LOGO],
		['CITV','citv',CITV_LOGO],						
	]
	
	for channel in channels:
	
		oc.add(
			DirectoryObject(
				key=Callback(RenderProgramList, url=ITV_GENRE_POPULAR_URL % channel[1], sort_by_name=True, parent_name=oc.title2, section_name=channel[0]),
				title=channel[0],
				thumb=channel[2],
			)
		)

	return oc		
	
#################################################
def AddDateList(parent_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=TV_DATE_TITLE)
	
	date = Datetime.Now()
	oc.add(
		DirectoryObject(
			key=Callback(RenderEpisodesForDay, url=ITV_DATE_URL % date.strftime("%d-%b-%Y"), parent_name=oc.title2, section_name="Today"),
			title="Today",
		)
	)
	
	date += Datetime.Delta(days=-1)
	oc.add(
		DirectoryObject(
			key=Callback(RenderEpisodesForDay, url=ITV_DATE_URL % date.strftime("%d-%b-%Y"), parent_name=oc.title2, section_name="Yesterday"),
			title="Yesterday",
		)
	)
	
	for number in range (2, 31):
		date += Datetime.Delta(days=-1)
		oc.add(
			DirectoryObject(
				key=Callback(RenderEpisodesForDay, url=ITV_DATE_URL % date.strftime("%d-%b-%Y"), parent_name=oc.title2, section_name=date.strftime("%a, %d %b %Y")),
				title=date.strftime("%a, %d %b %Y"),
			)
		)
		
	return oc

	
#################################################

def RenderProgramList(url=None, sort_by_name=False, parent_name=None, section_name=None):

	oc = ObjectContainer(no_cache=True, view_group="InfoList", title1=parent_name, title2=section_name)
	
	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
	programmes = content.xpath(ITV_PROGRAMME_XPATH)
	progs = []
	
	if len(programmes) < 1:
		return MessageContainer(
			"No Programmes Found",
			"No Programmes have been found matching your search\nPlease try again."
		)

	for programme in programmes:
		progs.append(ConstructProgramme(programme))
		
	if sort_by_name:
		progs = sorted(progs, key=lambda prog:prog.title)
	
	for prog in progs:
			
		title = prog.title
		
		if (prog.additionalInfo.episodeCount is not None):
			title += ' [' + str(prog.additionalInfo.episodeCount) + ']'
		
		oc.add(
			DirectoryObject(
				key = Callback(RenderEpisodeList, url=prog.pageUri, parent_name=oc.title2, section_name=title),
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

def RenderEpisodesForDay(url, parent_name=None, section_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=section_name)
	eps = []
	
	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)
	
	for channel in content.xpath("//div[contains(@class,'view-display-id-by_day')]"):
	
		channelName = re.search("global-(\\w*)-large", channel.xpath(".//span[contains(@class,'chan-button')]/@class")[0]).groups()[0]
		episodes = channel.xpath(".//li[contains(@class,'min-container')]")
	
		for episode in episodes:
			ep = ConstructEpisode(pageUri=url, element=episode)
			ep.channel = channelName
			eps.append(ep)
		
	for ep in sorted(eps, key=lambda ep: ep.lastBroadcast, reverse=True):
		
		oc.add(
			VideoClipObject(
				url = ep.id,
				title = ep.lastBroadcast.strftime("%H:%M") + " - " + ep.channel + " - " + ep.title,
				thumb = ep.posterFrameUri,
				summary = ep.summary(),
				duration = ep.durationMilliseconds()
			)
		)
		
	return oc
	
	
#################################################

def RenderSearchResults(query=None, parent_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name)
		
	content = HTML.ElementFromURL(ITV_SEARCH_URL % String.Quote(query), errors='ignore', cacheTime=1800)
	
	programmes = content.xpath(ITV_SEARCH_XPATH)

	if len(programmes) < 1:
		return MessageContainer(
			"No Programmes Found",
			"No Programmes have been found matching your search\nPlease try again."
		)

	for programme in programmes:
	
		# See if the search result is for a programme or an episode.
		matchType = programme.xpath(".//div[@data-matchtype]/@data-matchtype")[0]
		
		prog = ConstructProgrammeSearch(programme)
		
		if (matchType == 'programme'):
		
			title = prog.title
			if (prog.additionalInfo.episodeCount is not None):
				title += ' [' + str(prog.additionalInfo.episodeCount) + ' matched]'
			
			oc.add(
				DirectoryObject(
					key = Callback(RenderEpisodeList, url = prog.pageUri),
					title = title,
					thumb = prog.imageUri,
					summary = prog.shortSynopsis,
				)
			)
			
		else:
					
			for episode in programme.xpath(".//div[contains(@class,'episodenid-')]"):
			
				ep = ConstructEpisodeSearch(episode)
				
				oc.add(
					VideoClipObject(
						url = ep.id,
						title = prog.title + " - " + ep.title,
						summary = ep.summary(),
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

def RenderEpisodeList(url=None, parent_name=None, section_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=section_name)
	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)

	episodes = content.xpath(ITV_EPISODE_XPATH)

	if len(episodes) <= 1:
	
		episodes = content.xpath("//div[@class='hero']")
		
		if len(episodes) < 1:
			return MessageContainer(
				"No Episodes Found",
				"No Episodes have been found matching your search\nPlease try again."
			)
	
	for episode in episodes:
	
		ep = ConstructEpisode(pageUri=url, element=episode)
		
		oc.add(
			VideoClipObject(
				url = ep.id,
				title = ep.titleDisplay(),
				thumb = ep.posterFrameUri,
				summary = ep.summary(),
				duration = ep.durationMilliseconds()
			)
		)
		
	return oc

#################################################
def ConstructProgramme(element):
	
	imageUri = ''
	if len(element.xpath('.//img/@src')) > 0:
		imageUri = element.xpath('.//img/@src')[0]
		imageUri = imageUri.replace('player_image_thumb_standard','posterframe')
		
	additionInfoEpisodeCount = None
	if len(element.xpath(".//span[@class='episode-free']")) > 0:
		additionInfoEpisodeCount = element.xpath(".//span[@class='episode-free']")[0].text
	
	return MediaItems.Programme(
		title                      = element.xpath(".//div[@class='programme-title cell-title']/a")[0].text,
		pageUri                    = ITV_URL + element.xpath(".//div[@class='programme-title cell-title']/a/@href")[0],
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
	
#################################################
def ConstructProgrammeSearch(element):
	
	imageUri = ''
	if len(element.xpath(".//div[@class='search-result-image']//img/@src")) > 0:
		imageUri = element.xpath(".//div[@class='search-result-image']//img/@src")[0]
		imageUri = imageUri.replace('player_image_thumb_standard','posterframe')
		
	additionInfoEpisodeCount = None
	if len(element.xpath(".//span[@class='search-max']")) > 0:
		additionInfoEpisodeCount = element.xpath(".//span[@class='search-max']")[0].text
	
	return MediaItems.Programme(
		title                      = element.xpath(".//h4[@class='programme-title']/a")[0].text,
		pageUri                    = element.xpath(".//h4[@class='programme-title']/a/@href")[0],
		imageUri                   = imageUri,
		shortSynopsis              = " ".join(element.xpath(".//div[@class='programme-description']//text()")).strip(),
		additionInfoEpisodeCount   = additionInfoEpisodeCount,
		latestEpisodeDate          = '',
		latestEpisodeTime          = '',
	)
	
#################################################
def ConstructEpisode(element, pageUri):
	
	id = pageUri
	if len(element.xpath(".//div[contains(@class, 'node-episode')]/a[1]/@href")) > 0:
		id = ITV_URL + element.xpath(".//div[contains(@class, 'node-episode')]/a[1]/@href")[0]
	elif len(element.xpath("./a")) > 0:
		id = ITV_URL + element.xpath("./a[1]/@href")[0]
		
	title = 'Unknown'
	if len(element.xpath("//h2[@class='title episode-title']")) > 0:
		title = element.xpath("//h2[@class='title episode-title']")[0].text
	elif len(element.xpath(".//div[@class='programme-title']")) > 0:
		title = " ".join(element.xpath(".//div[@class='programme-title']//text()")).strip()
	
	seasonNumber = ''
	if len(element.xpath(".//div[contains(@class, 'field-name-field-season-number')]//text()")) > 0:
		seasonNumber = element.xpath(".//div[contains(@class, 'field-name-field-season-number')]//text()")[0]
	
	episodeNumber = ''
	if len(element.xpath(".//div[contains(@class, 'field-name-field-episode-number')]//text()")) > 0:
		episodeNumber = element.xpath(".//div[contains(@class, 'field-name-field-episode-number')]//text()")[0]
		
	daysRemaining = None
	if len(element.xpath(".//div[@class='offer-duration']")) > 0:
		daysRemaining = re.search("(\\d*)",element.xpath(".//div[@class='offer-duration']")[0].text.strip()).groups()[0]
	#elif len() > 0:
	#	re.search("(\\d*)",element.xpath(".//div[@class='offer-duration']")[0].text.strip()).groups()[0]
		
	shortSynopsis = ''
	if len(element.xpath(".//div[contains(@class,'field-name-field-short-synopsis')]//text()")) > 0:
		shortSynopsis = element.xpath(".//div[contains(@class,'field-name-field-short-synopsis')]//text()")[0]
		
	duration = None
	if len(element.xpath(".//div[contains(@class, 'field-name-field-duration')]//text()")) > 0:
		res = re.search(
			"(?:(?:(\\d+)(?:\s*hours?\s*))|(?:(\\d+)(?:\s*minutes?))){1,2}",
			" ".join(element.xpath(".//div[contains(@class, 'field-name-field-duration')]//text()")).strip()
		)
		if res:
			duration = (int(res.groups()[0]) if res.groups()[0] else 0) * 60
			duration += (int(res.groups()[1]) if res.groups()[1] else 0)
			
	lastBroadcast = datetime.datetime.strptime(
		element.xpath(".//div[contains(@class, 'field-name-field-broadcastdate')]//span/@content")[0][:-6],
		'%Y-%m-%dT%H:%M:%S'
	)
	        
	posterFrameUri = None
	if len(element.xpath(".//div[contains(@class,'field-name-field-image')]//img/@src")) > 0:
		posterFrameUri = element.xpath(".//div[contains(@class,'field-name-field-image')]//img/@src")[0]
	elif len(element.xpath(".//param[@name='poster']")) > 0:
		posterFrameUri = element.xpath(".//param[@name='poster']/@value")[0]
		
	if posterFrameUri:
		posterFrameUri = posterFrameUri.replace('player_image_thumb_standard','posterframe')
	
	return MediaItems.Episode(
		id                         = id,
		title                      = title,
		seasonNumber               = seasonNumber,
		episodeNumber              = episodeNumber,
		duration                   = duration,
		lastBroadcast              = lastBroadcast,
		daysRemaining              = daysRemaining,
		shortSynopsis              = shortSynopsis,
		posterFrameUri             = posterFrameUri,
		#channel                    = element.xpath('./d:AdditionalInfo/d:Channel',namespaces={'d' : ITV_XML_NS})[0].text,
		#channelLogoUrl             = element.xpath('./d:AdditionalInfo/d:ChannelLogoUrl',namespaces={'d' : ITV_XML_NS})[0].text,
	)
	
def ConstructEpisodeSearch(element):

	daysRemaining = None
	res = re.search("(\\d+)", " ".join(element.xpath(".//div[@class='remaining-time']//text()")).strip())
	if res:
		daysRemaining = res.groups()[0]
		
	return MediaItems.Episode(
		id                         = ITV_URL + element.xpath(".//a/@href")[0],
		title                      = " ".join(element.xpath(".//div[@class='episode-title']//text()")).strip(),
		shortSynopsis              = " ".join(element.xpath(".//div[@class='description']//text()")).strip(),
		daysRemaining              = daysRemaining
	)

