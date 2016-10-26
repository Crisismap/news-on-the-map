# -*- coding: utf-8 -*-
import time;
import sys
import httplib, urllib
import json
import array;
import base64;
import string;

import xml.dom.minidom;


def getOriginalStringFromTreeHash(wordHash,wordId):
    
    wordList = [];
    try:    
        if(len(wordHash[wordId][0]) > 0):
            wordList = [[wordHash[wordId][0][1],wordHash[wordId][0][2]]];
        
        for childId in wordHash[wordId][1]:
            wordList += getOriginalStringFromTreeHash(wordHash,childId);
    except:
        print "ERROR";
    return wordList;

def printPositionWordList(wordList):
    try:
         # Sort word list by word position
        wordList.sort(key=lambda x: int(x[0]));
        
        strOut = "";
        for wordObj in wordList:
            strOut += wordObj[1] + " ";
        return strOut;
    except:
        print "ERROR";


def parseByteArray(byteArray):
    outStr = '';
    for i  in range(0,len(byteArray)):
        
        if(byteArray[i] <= 0x7F):
            if(byteArray[i] == 0x25):
                outStr += "%25";
            else:
                outStr += String.fromCharCode(byteArray[i]);
        else: 
            outStr += "%" + str(byteArray[i]).upper()
    return outStr

def toByteArray(inString):
    byteArray = [];
    byteArray.append(0xEF);
    byteArray.append(0xBB);
    byteArray.append(0xBF);
    
    #byteArray = byteArray + map(ord,inString);
    #return byteArray;
    codedString = map(ord,inString);
    for i in range(0,len(inString)):
        if (codedString[i] <= 0x7F):
            byteArray.append(codedString[i]);
        else:
            h = urllib.quote(inString[i].encode('utf-8'))[1:].split('%');
            for j in range(0,len(h)):
                byteArray.append(int(h[j],16));
    return byteArray;


class abbyy(object):
    def __init__(self):
        self.conn = None;
        self.currentTaskId = None;

    def connect(self):
        #ABBYY Rest API was changed
        #self.conn = httplib.HTTPConnection("semanticservice.abbyy.com")
        #self.conn.request("GET", "/parserservice.svc/rest/MarkupLanguages")
        self.conn = httplib.HTTPConnection("parserservicebackup.abbyy.com")        
        self.conn.request("GET", "/api/server/markupLanguages", "", {"Authorization": "Basic ___"}) #___  <-> BASE64 (user:pass)
        response = self.conn.getresponse()        
        #semanticservice.abbyy.com/parserservice.svc/rest        
        if(response.status != 200):
            raise Exception("Could not connect to abbyy service: "+response.reason);
        data = response.read();
                
        
    def sendSourceText(self,txtSource):
        if(self.conn == None):
            raise Exception("Connection is has not been established yet!");        
        #ABBYY Rest API was changed
        #params = '{"taskParameters": {"Source":{"Extension":".txt","Contents":' + str(toByteArray(txtSource)) + '},"UserCredentials":{"Login":"sx","Password":"mQ3Po5Bj","IsCustomUser":true},"SourceLanguage":"","MarkupLanguage":"neutral","XmlParameters":["All"],"Topics":[],"Ontologies":["All"],"ProcessTimeout":1000000}}';
        params = '{"Source":{"Extension":".txt","Content":"' + base64.b64encode(txtSource) + '"},"SourceLanguage":"","MarkupLanguage":"neutral","XmlParameters":["All"],"Topics":[],"Ontologies":["All"],"ProcessingTimeout":1000000}';
        headers = {"Authorization": "Basic ___","Content-type": "application/json; charset=utf-8","Accept": "*/*"} #___  <-> BASE64 (user:pass)
        #print params
        #print headers
        #ABBYY Rest API was changed
        #self.conn.request("POST", "/parserservice.svc/rest/Tasks/StartTask",params,headers)
        self.conn.request("POST", "/api/tasks",params,headers)
        response = self.conn.getresponse()
        #ABBYY Rest API was changed
        #if(response.status != 200):
        if(response.status != 201):
            raise Exception("Could not create a new task: "+response.reason);
        
        #jsonResponse = json.JSONDecoder().decode(response.read())
        #self.currentTaskId = jsonResponse['taskId'];
        self.currentTaskId = string.replace(response.read(), '"', '')
        
    def isReady(self):
        if(self.conn == None):
            raise Exception("Connection is has not been established yet!");
 
        # Check progress
        #ABBYY Rest API was changed
        #self.conn.request("GET", "/parserservice.svc/rest/Tasks/" + self.currentTaskId + "/State")
        self.conn.request("GET", "/api/tasks/" + self.currentTaskId, '', {"Authorization": "Basic ___","Content-type": "application/json; charset=utf-8","Accept": "*/*"}) #___  <-> BASE64 (user:pass)
        response = self.conn.getresponse()
        if(response.status != 200):
            raise Exception("State check failed: "+response.reason);

        jsonResponse = json.JSONDecoder().decode(response.read())
        status = jsonResponse['State'];
        percent = jsonResponse['CompletionPercent'];
        result = jsonResponse['Result'];
        error = jsonResponse['Error'];
        isFullyProcessed = jsonResponse['IsFullyProcessed'];
        #ABBYY Rest API was changed
        #if(status != 3 and status != 5 and status != 2):
        #    if(status == 0):
        #        print jsonResponse['GetTaskStateResult']['Message'];
        #    raise Exception("ERROR: Apparently an error has accured. Status returned by ABBYY: "+status)
        #return status != 3 and status != 2
        print 'Debug: ' + str(status) + ' ' + str(percent) + ' ' + str(error) + ' ' + str(isFullyProcessed)
        st = status.lower();
        if (st == 'notprocessed' or st == 'processingfailed'):
            raise Exception("ERROR: Apparently an error has accured. Status returned by ABBYY: "+status)
        if (st == 'processingsuccessful'):
            return base64.b64decode(result['Content'])
        else: # (st != 'inqueue' && st != 'processing')
            return None
    
    def getXMLResults(self):
        if(self.conn == None):
            raise Exception("Connection is has not been established yet!");
        
        self.conn.request("GET", "/parserservice.svc/rest/Tasks/" + self.currentTaskId + "/Result")
        response = self.conn.getresponse()
        if(response.status != 200):
            raise Exception("Failed to obtain results: "+response.reason);

        jsonResponse = json.JSONDecoder().decode(response.read())
        
        if(jsonResponse['GetTaskResultResult']['Code'] != 0):
            raise Exception("Erroroneous results")
            
        return array.array('B', jsonResponse['result']['Contents']).tostring()
    
    def extractGeoOntologyObjects(self,xmlInput):
		import codecs
		locationStrings = [];

		doc = xml.dom.minidom.parseString(xmlInput)
		ontoObjects = doc.getElementsByTagName('OntoObject');
		#with codecs.open('C:/sx/Operative/NewsRss/Test/' + str(len(xmlInput)) + '.xml', 'w', encoding = 'utf8') as f:
		#	f.write(xmlInput)
		#print(ontoObjects)

		blacklisted_classes = ["Road","TownSquare","PublicTransportStation"]
		geo_object_classes = ["GeoObject"]

		for obj in ontoObjects:
			wordHash = {};
			superClass = obj.getElementsByTagName('SuperClass')[0].firstChild.data;
			if(superClass in geo_object_classes):
				phrase = obj.getElementsByTagName('Title')[0].firstChild.data;
				subClass = obj.getElementsByTagName('Class')[0].firstChild.data;
				
				if(subClass not in blacklisted_classes):
					print subClass + " : " + phrase;
					locationStrings.append(phrase)
		return locationStrings;

    def extractLocationStrings(self,xmlInput):
        locationStrings = [];

        doc = xml.dom.minidom.parseString(xmlInput)
        sentenceNodes = doc.getElementsByTagName('Sentence');
        
        for sent in sentenceNodes:
            wordHash = {};
            
            words = sent.getElementsByTagName('Word');
            for word in words:
                # If this is substituted word, skip it
                subsAttr = word.getAttributeNode('substituted');
                
                fSubstitute = False;
                
                if(subsAttr != None and subsAttr.nodeValue == "true"):
                    fSubstitute = True;
                
                parentId = -1;
                if(len(word.getElementsByTagName('ParentID')) > 0):
                    parentId = word.getElementsByTagName('ParentID')[0].firstChild.data
                try:
                    id = word.getElementsByTagName('ID')[0].firstChild.data;
                    
                    if(fSubstitute == False):
                        position = word.getElementsByTagName('Position')[0].firstChild.data;
                        
                        if(len(word.getElementsByTagName('NF')) > 0):
                            wordTxt = word.getElementsByTagName('NF')[0].firstChild.data;
                        else:
                            wordTxt = word.getElementsByTagName('Original')[0].firstChild.data;
                        lexicalClasses = [];
                        if(len(word.getElementsByTagName('NearestSensibleParent')) > 0):
                            lexicalClasses = word.getElementsByTagName('NearestSensibleParent')[0].firstChild.data.split(':');
                        
                except:
                    raise Exception("Parsing Error");
                
                
                if id not in wordHash.keys():
                    wordHash[id] = [[],[]];
                    
                if(fSubstitute == False):
                    wordHash[id][0] = [parentId,position,wordTxt,lexicalClasses]; #word object
                
                if(parentId != -1):
                    if parentId not in wordHash.keys():
                        wordHash[parentId] = [[],[]];
                    wordHash[parentId][1].append(id);  #append child to parent node
                
            # Now step through all words, and identify those of interest, printing all their children ordered by position
            for wordId,wordNode in wordHash.iteritems():
                #classesOfInterest = ['PLACE','UNITS_OF_SPACE','VILLAGE','COUNTRY_AS_ADMINISTRATIVE_UNIT','GEOGRAPHICAL_OBJECT','ADMINISTRATIVE_REGION','DISTRICT','CITY_TOWN']
                classesOfInterest = ['VILLAGE','COUNTRY_AS_ADMINISTRATIVE_UNIT','GEOGRAPHICAL_OBJECT','ADMINISTRATIVE_REGION','DISTRICT','CITY_TOWN']
                
                for classStr in classesOfInterest:
                    try:
                        if(len(wordNode[0]) > 0 and classStr in wordNode[0][3]):
                            locationStrings.append(printPositionWordList(getOriginalStringFromTreeHash(wordHash,wordId)));
                            break;
                    except:
                        raise Exception("Parsing Error")
                
        return locationStrings;
    
    def disconnect(self):
        if(self.conn == None):
            raise Exception("Connection is has not been established yet!");
        
        self.conn.close();
        
    def getCandidateNounPhrases(self,text):
        try:
            self.connect();
            self.sendSourceText(text);
            
            #ABBYY Rest API was changed
            #while(self.isReady() == False):
            #    time.sleep(1);
            #xmlOut = self.getXMLResults();
			
            while (True):
                xmlOut = self.isReady();
                if (xmlOut != None):
                    break;
                time.sleep(1);
            
            self.disconnect();
            
            #return self.extractLocationStrings(xmlOut);

            #print(xmlOut);
            return self.extractGeoOntologyObjects(xmlOut);
        except:
            print "Error: ",sys.exc_info()[0],sys.exc_info()[1]
            if(self.conn != None):
                self.disconnect();
            return []
        

