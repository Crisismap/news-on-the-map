# -*- coding: utf-8 -*-
import sys
import json
import urllib
import urllib2

def getGoogleMapLocation(locationStr):
  try:
    GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json?key=___&address="
    #print GOOGLE_GEOCODING_URL + urllib.quote(locationStr)
    doc = urllib2.urlopen(GOOGLE_GEOCODING_URL + urllib.quote(locationStr.encode("utf-8"))).read() #etostrokakotorayadolzhnavernutpustoyrezultat
    res = json.JSONDecoder().decode(doc)
    geom = res["results"][0]["geometry"]
    loc = geom["location"]
    sw = geom["bounds"]["southwest"]
    ne = geom["bounds"]["northeast"]
    return [(str(loc["lng"]), str(loc["lat"])), (str(sw["lng"]), str(sw["lat"])), (str(ne["lng"]), str(ne["lat"]))]
  except:
    print "Error parsing JSON output from Google: " + str(sys.exc_info()[1])
    return None;

if __name__ == '__main__':
    print getGoogleMapLocation(u"Приморье")
    print getGoogleMapLocation(u"московская область")
