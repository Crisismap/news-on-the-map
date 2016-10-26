#key-value collection. key = news type, value = tuple training set
#training set is a file located in ./data directory and language (currently supported values: 'ru', 'en')
classificators = { 
  'fires' : ('scored_corpus.csv', 'ru'),
  'fires_eng' : ('scored_corpus_fires_eng.csv', 'en'),
  'antiplaton' : ('antiplaton.csv', 'ru'),
  'syria_eng' : ('Syria_WAR_ENG.csv', 'en'),
  'syria' : ('Syria_WAR_RUS.csv', 'ru')
}

import mincl
import pickle
import time
import sys
from sx_storage import sxDBStorage
from os.path import isfile
from os.path import splitext

def classify(type, file, lang):
  name, ext = splitext(file)
  pickle_fname = name + '.pck'
  if isfile(pickle_fname): #if model exists, load it
    print "Loading model..."
    model = pickle.load(open(pickle_fname, 'rb'))
    print "Model is loaded."
  else: #else learn and dump
    print "Learning model..."
    model = mincl.learn(file, lang)
    print "Model is loaded. Dumping model..."
    pickle.dump(model, open(pickle_fname, 'wb'))
    print "Model is dumped."
  dbsx = sxDBStorage()
  dbsx.ConnectMaps()
  news = dbsx.LoadUnclassifiedNews(type)
  for fn in news:
    #print fn["title"]
    #time.sleep(5)
    predict = mincl.predict((fn["title"], fn["body"]), model)[0]
    print predict
    dbsx.UpdateNewsClass(fn["id"], predict)
    #return
  return

def classify_all():
  for key in classificators:
    try:
      classify(key, 'c:/sx/Operative/NewsRss/data/' + classificators[key][0], classificators[key][1])
    except:
      print "Error classifiing " + key + ": " + str(sys.exc_info()[1])
  return
  
if __name__ == '__main__':
  classify_all()