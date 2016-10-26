# -*- coding: utf-8 -*-
import sys
import urllib2
import xml.dom.minidom

# List of banned coordinates
bannedCoordinates = dict({u'37.406971 56.013920':u'садовое товарищество Регион',u'45.466117 54.725145':u'СЕЛО КАМЧАТКА'});

def getYandexMapLocation(locationStr):
    try:
        APIKEY = "___"
        YANDEX_REVERSE_GEOCODING_URL = "http://geocode-maps.yandex.ru/1.x/"
        # Use Yandex Geocoder to reverse geocode the location specified
        xmlDoc = urllib2.urlopen(YANDEX_REVERSE_GEOCODING_URL + "?geocode=%s&documentContent=%s"%(locationStr,APIKEY));
        
        textResponse = xmlDoc.read();
        f = open("results.xml","w")        
        f.write(textResponse);
        f.close();
        
        doc = xml.dom.minidom.parseString(textResponse)
        nFound = doc.getElementsByTagName('found')[0];
        
        if(int(nFound.firstChild.data.encode('ascii')) == 0):
            return None;
        else:
            featureMember = doc.getElementsByTagName('featureMember')[0];
            latLon = featureMember.getElementsByTagName('pos')[0];
            lowerCorner = featureMember.getElementsByTagName('lowerCorner')[0];
            upperCorner = featureMember.getElementsByTagName('upperCorner')[0];
            CountryNameCode = featureMember.getElementsByTagName('CountryNameCode')[0];
            kind = featureMember.getElementsByTagName('kind')[0].firstChild.data;
            
            #print "Location: " + unicode(locationStr) +  " " + latLon.firstChild.data
            if(kind != 'locality' and kind != 'country' and kind != 'province' and kind != 'area'):
                print "GeographyType: " + kind + " " + locationStr;
                return None;
            
            #if(CountryNameCode.firstChild.data.encode('ascii') not in ['RU','UA','KZ','BY','BG']):
            #    print  CountryNameCode.firstChild.data.encode('ascii');
            #    return None
            #print latLon.firstChild.data.split(' ');
            #print "Location: " + unicode(locationStr) +  " " + latLon.firstChild.data
            
            # Make sure the coordinates are not banned
            strCoords = latLon.firstChild.data;
            if(strCoords in bannedCoordinates.keys()):
                print "Banned coords: " + bannedCoordinates(strCoords)
                return None;
            else:
                lc = lowerCorner.firstChild.data;
                uc = upperCorner.firstChild.data;
                return [tuple(strCoords.split(' ')),tuple(lc.split(' ')),tuple(uc.split(' '))];
                
    except:
        print "Error parsing XML output from Yandex: " + str(sys.exc_info()[1])
        return None;