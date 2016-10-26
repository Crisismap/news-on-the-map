#from toponyms.toponyms import toponyms
from sx_storage import sxDBStorage;
from location_extraction_abbyy import LocationExtractionAbbyy;
import sys;
import odbc;

if __name__ == '__main__':
  db = odbc.odbc("Driver={SQL Server Native Client 10.0};Server=___;Failover_Partner=___;Database=___;Uid=___;Pwd=___");
  cur = db.cursor();
  print "go"
  cur.execute("SELECT TOP 1 id,guid,pubDate,title,type,link,description FROM NewsRSS_Bak WHERE isLocalized = 0 ORDER BY id DESC");
  #cur.execute("SELECT TOP 1 id,guid FROM rss_guids_repair ORDER BY id DESC");
  news = cur.fetchall();
  #print news
  for article in news:
    print article[1]#.encode('ascii', 'ignore')
    break
  cur.close();

'''
class test(object):

  def __init__(self):
    #self.toponyms = toponyms()
    return

  def go(self):
    text = 'First big wildfire of season contained NW of Madras - KTVZ. A 638-acre wildfire about 20 miles northwest of Madras was fully contained on Tuesday. It all started Sunday evening when a campfire escaped and quickly grew into a large-scale fire. Several crews were dispatched Sunday night, including firefighters...'
    res = self.toponyms.getCandidatePhrases(text)
    print res
  
if __name__ == '__main__':
  le = LocationExtractionAbbyy();
  dbsx = sxDBStorage()
  dbsx.ConnectMaps()
  news = dbsx.LoadUnlocalizedNewsFromDB()
  for article in news:
    print 'article id: ', article["id"]
    articleTxt = article["title"] + ". " + article["description"];
    [locations, debugOutput, allPhrases] = le.GetCandidateLocations(articleTxt, True, True);
    print [locations, debugOutput, allPhrases]
  #t = test()
  #t.go()
  #t = toponyms()
  #t.test
'''