# -*- coding: utf-8 -*-
# This script figures out the most relevant location to the news articles.
 
from sx_storage import sxDBStorage;
#from location_extraction import LocationExtraction;
from location_extraction_abbyy import LocationExtractionAbbyy;
import sys;

reload(sys);
sys.setdefaultencoding('utf-8');

## Initialize utility classes
#le = LocationExtraction();
le = LocationExtractionAbbyy();
dbsx = sxDBStorage();

dbsx.ConnectMaps();

# Load news that had not yet been localized from the database.
news = dbsx.LoadUnlocalizedNewsFromDB();

# For each article, determine candidate locations
for article in news:
  try:
    print 'article id: ', article["id"]#, article["guid"].encode('utf-8', 'ignore');
    ## Append title and description
    articleTxt = article["title"] + ". " + article["description"];
    ## Extract location from the joint text
    [locations, debugOutput, allPhrases] = le.GetCandidateLocations(articleTxt, True, True);
    ## Record location and debug output to the database.
    dbsx.StoreArticleLocations(article,locations,debugOutput,allPhrases);
    ## Extract location from the joint text via sxGeocoder
    [locations, debugOutput, allPhrases] = le.GetCandidateLocations(articleTxt, True, False);
    ## Record location and debug output to the database.
    dbsx.StoreArticleLocationssxTest(article,locations,debugOutput,allPhrases);
  except Exception, e:
    print "Error processing news: ", str(e)#.encode('utf-8');

  
## Close database
dbsx.Close();