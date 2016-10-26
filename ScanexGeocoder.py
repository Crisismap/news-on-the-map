# -*- coding: utf-8 -*-
import sys
import json
import urllib
import urllib2

def getLocation(locationStr):
  try:
    sx_GEOCODING_URL = u"http://geocode.kosmosnimki.ru/GeoSearch.ashx?UseOSM=1&IsStrongSearch=1&SearchString="
    #etostrokakotorayadolzhnavernutpustoyrezultat
    doc = urllib2.urlopen(sx_GEOCODING_URL + urllib.quote(locationStr.encode("utf-8"))).read()
    res = json.JSONDecoder().decode(doc)
    if (len(res) == 0):
      return None
    r = res[0]
    return [(str(r["CntrLon"]), str(r["CntrLat"])),(str(r["MinLon"]), str(r["MinLat"])),(str(r["MaxLon"]), str(r["MaxLat"]))];
  except:
    print "Error parsing JSON output from sx: " + str(sys.exc_info()[1])
    return None;

if __name__ == '__main__':    
    print getLocation(u"москва")
    print getLocation(u"московская область")
