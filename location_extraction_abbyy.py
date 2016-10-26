# -*- coding: utf-8 -*-
import urllib2
import ssl
from abbyy import abbyy
from YandexGeocoder import getYandexMapLocation
from sxGeocoder import getLocation
from GoogleGeocoder import getGoogleMapLocation
from toponyms.toponyms import toponyms

if hasattr(ssl, '_create_unverified_context'):
	ssl._create_default_https_context = ssl._create_unverified_context

# Dictionary of location coordinates.
locationDictionary = dict({u'ХАБАРОВСК КРАЙ':[(u'135.966288',u'51.191732'),(u'130.386205',u'46.638581'),(u'141.546372',u'55.333671')],
                           u'АМУР':          [(u"126.806329",u"51.305869"),(u"122.111123",u"48.851351"),(u"130.628822",u"53.563386")],
                           u'САХАЛИН':       [(u"142.979130",u"50.350880"),(u"141.210896",u"45.892699"),(u"144.747374",u"54.424655")],
                           u'ПРИАМУРЬЕ':     [(u"127.288284",u"53.152586"),(u"119.656153",u"48.851351"),(u"134.920416",u"57.060602")],
                           u'РЕГИОН СИБИРЬ': [(u"98.14",u"63.5"),(u"70.50",u"49.5"),(u"122.4",u"75.5")],
                           u"СИБИРЬ":        [(u"98.14",u"63.5"),(u"70.50",u"49.5"),(u"122.4",u"75.5")],
                           u"СИБИРСКИЙ ФЕДЕРАЛЬНЫЙ ОКРУГ":        [(u"98.14",u"63.5"),(u"70.50",u"49.5"),(u"122.4",u"75.5")],
                           u'ВОСТОК':        [(u"133.0",u"55.0"),(u"108.0",u"37.0"),(u"169.0",u"75.0")],
                           u"ДАЛЬНИЙ ВОСТОК":[(u"133.0",u"55.0"),(u"108.0",u"37.0"),(u"169.0",u"75.0")]});


class LocationExtractionAbbyy(object):
    def __init__(self):
        self.toponyms = toponyms()
        return;
    
    # Looks up the phrase specified in the dictionary, returning coordinates and bounds for the locality, or None if not found.
    def GetDictionaryLocation(self,phrase):    
        if(phrase in locationDictionary.keys()):
            return locationDictionary[unicode(phrase)];
        else:
            return None;
            
    def ExtractBestLocation(self,newsLocations):
        
        # start by counting all duplicates
        iLocation = 0;
        while(iLocation < len(newsLocations)):
            iOther = iLocation+1;
            #print ("Location: " + newsLocations[iLocation][0]).encode('cp866')
            while(iOther < len(newsLocations)):
                if(newsLocations[iLocation][1] == newsLocations[iOther][1]):
                    #print ("Duplicate: " + newsLocations[iOther][0]).encode('cp866')
                    #Increase counter by adding counters from current location and duplicate
                    newsLocations[iLocation][4] += newsLocations[iOther][4]
                    
                    #print "location count = "+str(newsLocations[iOther][4])+ " " + str(newsLocations[iLocation][4]);
                    
                    # Splice the array, removing the duplicate 
                    newsLocations = newsLocations[:iOther] + newsLocations[iOther+1:];
                     
                else:
                    iOther += 1;
            iLocation += 1;
        
        
        
        iLocation = 0;
        # Now let's drill down to the most precise location
        while(iLocation < len(newsLocations)):
            iOther = iLocation+1;
            
            while(iOther < len(newsLocations)):
                # check if the other location is enveloped by the current location
                if(float(newsLocations[iLocation][2][0]) < float(newsLocations[iOther][2][0]) and float(newsLocations[iLocation][2][1]) < float(newsLocations[iOther][2][1])
                   and float(newsLocations[iLocation][3][0]) > float(newsLocations[iOther][3][0]) and float(newsLocations[iLocation][3][1]) > float(newsLocations[iOther][3][1])):
                    
                    print newsLocations[iLocation][0] + " envelops " + newsLocations[iOther][0];
                    #Increase counter by adding counters from current location and enveloped location, and copy content from smaller location to larger one.
                    currentCnt = newsLocations[iLocation][4];
                    newsLocations[iLocation] = newsLocations[iOther];
                    newsLocations[iLocation][4] += currentCnt;                
                    
                    # Splice the array, removing the duplicate 
                    newsLocations = newsLocations[:iOther] + newsLocations[iOther+1:];
                    
                # Check if current location is enveloped by another location.
                elif(float(newsLocations[iOther][2][0]) < float(newsLocations[iLocation][2][0]) and float(newsLocations[iOther][2][1]) < float(newsLocations[iLocation][2][1])
                   and float(newsLocations[iOther][3][0]) > float(newsLocations[iLocation][3][0]) and float(newsLocations[iOther][3][1]) > float(newsLocations[iLocation][3][1])):
                    print (newsLocations[iLocation][0] + " ( " + str(float(newsLocations[iLocation][2][0])) + ","+str(float(newsLocations[iLocation][2][1]))   + " ) " + " ( " + str(float(newsLocations[iLocation][3][0])) + ","+str(float(newsLocations[iLocation][3][1]))   + " ) is enveloped by "+ newsLocations[iOther][0] + " " + newsLocations[iOther][0] + " ( " + str(float(newsLocations[iOther][2][0])) + ","+str(float(newsLocations[iOther][2][1]))   + " ) " + " ( " + str(float(newsLocations[iOther][3][0])) + ","+str(float(newsLocations[iOther][3][1]))   + ")").encode('cp866');    
                    
                    
                    #Increase counter by adding counters from current location and duplicate
                    newsLocations[iLocation][4] += newsLocations[iOther][4]
                    
                    # Splice the array, removing the duplicate 
                    newsLocations = newsLocations[:iOther] + newsLocations[iOther+1:]; 
                    
                else:
                    iOther += 1;
            iLocation += 1;
        
        # Now lets choose the location with highest count
        highestCount = 0;
        bestMatch = [];
        
        for iLocation in range(0,len(newsLocations)):
            if(newsLocations[iLocation][4] > highestCount):
                highestCount = newsLocations[iLocation][4];
                outputStr= "Best Match cntr = " + str(highestCount) + " Location: "+newsLocations[iLocation][0];
                #print outputStr.encode('cp866')
                bestMatch = [newsLocations[iLocation][1]];
        
        return bestMatch;
    
    # Extracts the most relevant locaion from the text
    def GetCandidateLocations(self,text,useGoogle,useCompreno) :
    	debugResults = "";
        newsLocations = [];
        
        if (useCompreno):
            abbyObj = abbyy();
            phrases = abbyObj.getCandidateNounPhrases(text);
        else:
            phrases = self.toponyms.getCandidatePhrases(text)
        
        allPhrases = "";
		
        for phrase in phrases:
            if (allPhrases != ""):
                allPhrases += ", ";
            allPhrases += phrase;
            phrase = phrase.upper()
            
            # First check if we have the location in our dictionary
            results = self.GetDictionaryLocation(phrase);
            if(results == None):
                # get coordinates from Yanxex or sx.
                if (useGoogle):
                    results = getGoogleMapLocation(phrase)#getYandexMapLocation(phrase); TRIING GOOGLE
                else: 
                    results = getLocation(phrase)
                    print results
            if(results != None):
                coords = results[0];
                
                newsLocations.append([phrase,coords,results[1],results[2],1]);
                print phrase + str(coords);
                debugResults += phrase + str(coords);
                
            #print phrase,coords
        
        debugResults = debugResults.replace("'",'\\"');
        
        #print "Checking best location. So far count =" + str(len(newsLocations));
        bestLocation = self.ExtractBestLocation(newsLocations);
        #newsLocations = list(set(newsLocations))
            #print debugResults.encode('cp866')
        print bestLocation
        if(len(bestLocation) > 0):
            print (bestLocation[0][0]).encode('cp866'),(bestLocation[0][1]).encode('cp866')
        return [bestLocation, debugResults, allPhrases];