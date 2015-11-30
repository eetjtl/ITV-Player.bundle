#################################################
#                                               #
# ITV Player Plex Plugin                        #
#                                               #
# Version: 	0.6.0                               # 
# Created: 	08th Sept 2010                      #
# Last Updated: 22nd Nov 2015                   #
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
ITV_ALL_URL         = "http://www.itv.com/hub/shows"

ITV_PROGRAMME_XPATH     = "//ul[@id='az-list']/li/ul/li"


VIDEO_TITLE             = L('VideoTitle')
ALL_TITLE           = "All Programmes"

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

	oc = ObjectContainer()
		
	oc.add(
		DirectoryObject(
			key=Callback(RenderProgramList, url=ITV_ALL_URL, parent_name=oc.title1, section_name=ALL_TITLE),
			title=ALL_TITLE,
			summary="Browse all programmes.",
			thumb=R(ICON),
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

		if("/hub/" in prog.pageUri):
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

def RenderEpisodeList(url=None, parent_name=None, section_name=None):

	oc = ObjectContainer(no_cache=True, title1=parent_name, title2=section_name, view_group="InfoList")

	content = HTML.ElementFromURL(url, errors='ignore', cacheTime=1800)

	mytitle = content.xpath('//meta[@property="og:title"]/@content')[0]
	mysummary = content.xpath('//meta[@property="og:description"]/@content')[0]
	myimage = content.xpath('//meta[@property="og:image"]/@content')[0]

	oc.add(
		VideoClipObject(
			url = url,
			title = mytitle,
			summary = mysummary,
			thumb = myimage
		)
	)


	moreEpisodes = content.xpath('//a[@data-content-type="episode"]')

	# skip the first as it's the current episode that we already got info for above
	if len(moreEpisodes) > 1:
		for episode in moreEpisodes[1:]:
			epUrl = episode.xpath("@href")[0]
			epContent = HTML.ElementFromURL(epUrl, errors='ignore', cacheTime=1800)
			eptitle = epContent.xpath('//meta[@property="og:title"]/@content')[0]
			epsummary = epContent.xpath('//meta[@property="og:description"]/@content')[0]
			epimage = epContent.xpath('//meta[@property="og:image"]/@content')[0]
			oc.add(
				VideoClipObject(
					url = epUrl,
					title = eptitle,
					summary = epsummary,
					thumb = epimage
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
#	if len(element.xpath(".//p")) > 0:
#		additionInfoEpisodeCount = element.xpath(".//p")[0].text # TODO: strip ' episodes' from end of string
	
	return MediaItems.Programme(
		title                      = element.xpath(".//h3")[0].text.strip(),
		pageUri                    = element.xpath(".//a/@href")[0],
		imageUri                   = imageUri,
		shortSynopsis              = '',
		additionInfoEpisodeCount   = additionInfoEpisodeCount,
		latestEpisodeDate          = '',
		latestEpisodeTime          = '',
	)
	
