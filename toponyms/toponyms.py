#-*- coding: UTF-8 -*-

import numpy as np
import csv, data
import theano
from gensim.models import word2vec
import os
import theano.tensor as T
import annots

import lasagne
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

class toponyms(object):
  def __init__(self):
    #return
    print "Hello from toponyms.__init__"
    #word2vec models
    self.eng_word2vec_model = word2vec.Word2Vec.load_word2vec_format('c:/Scanex/Operative/Data/TEMP/news/data/wiki-100.model',
                                                                binary=False)
    self.rus_word2vec_model = word2vec.Word2Vec.load_word2vec_format('c:/Scanex/Operative/Data/TEMP/news/data/100-hs-sg-joint.model',
                                                                binary=False)
    # trained models
    self.eng_model = 'c:/Scanex/Operative/Data/TEMP/news/data/model-eng.npz'
    self.rus_model = 'c:/Scanex/Operative/Data/TEMP/news/data/model-rus.npz'
    self.input_var = T.dtensor3('inputs')

    # building nets for russian and english
    self.rus_network = data.build_mlp(((None,3,201), 300), self.input_var)
    self.eng_network = data.build_mlp(((None, 3, 101),150), self.input_var)
    with np.load(self.eng_model) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    lasagne.layers.set_all_param_values(self.eng_network, param_values)
    with np.load(self.rus_model) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    lasagne.layers.set_all_param_values(self.rus_network, param_values)
    

  def test(self):
    print "Hello from toponyms.test"
    
  def iseng(self, text):
    lat = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    cyr = u'цукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0'
    return sum(1 for l in text if l in lat ) > sum(1 for l in text if l in cyr)
    
  def getCandidatePhrases(self, text):
    words = data.get_tokens(text) # split to tokens
    if self.iseng(text): # if test is in English, we use English Language model
      ns = data.neurons(words, 1, self.eng_word2vec_model, lang = 'eng')

      prediction = lasagne.layers.get_output(self.eng_network, deterministic=True)
      predict_fn = theano.function([self.input_var], T.argmax(prediction, axis=1))
      pred = list(predict_fn(ns))
      predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
                                                                       # each one has a type (Location) and offsets (in terms of tokens)
      predicted = annots.setlabels(words,predannotations)  # list of  toponyms selected
    else: # if test is in Russian, we use Кгыышфт Language model
      ns = data.neurons(words, 1, self.rus_word2vec_model, lang = 'rus')

      prediction = lasagne.layers.get_output(self.rus_network, deterministic=True)
      predict_fn = theano.function([self.input_var], T.argmax(prediction, axis=1))
      pred = list(predict_fn(ns))
      predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
                                                                       # each one has a type (Location) and offsets (in terms of tokens)
      predicted = annots.setlabels(words,predannotations)  # list of  toponyms selected
    return predicted

'''
def iseng(text):
    lat = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    cyr = u'цукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0'
    return sum(1 for l in text if l in lat ) > sum(1 for l in text if l in cyr)



def main():
    #word2vec models
    eng_word2vec_model = word2vec.Word2Vec.load_word2vec_format('c:/Scanex/Operative/Data/TEMP/news/data/wiki-100.model',
                                                                binary=False)
    rus_word2vec_model = word2vec.Word2Vec.load_word2vec_format('c:/Scanex/Operative/Data/TEMP/news/data/100-hs-sg-joint.model',
                                                                binary=False)
    # trained models
    eng_model = 'c:/Scanex/Operative/Data/TEMP/news/data/model-eng.npz'
    rus_model = 'c:/Scanex/Operative/Data/TEMP/news/data/model-rus.npz'
    input_var = T.dtensor3('inputs')

    # building nets for russian and english
    rus_network = data.build_mlp(((None,3,201), 300), input_var)
    eng_network = data.build_mlp(((None, 3, 101),150), input_var)
    with np.load(eng_model) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    lasagne.layers.set_all_param_values(eng_network, param_values)
    with np.load(rus_model) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    lasagne.layers.set_all_param_values(rus_network, param_values)

    dt = [] # news text (title + snippet)
    labels = [] # toponyms labelled with Compreno
    #we read the file and fill the lists
    with open ('c:/Scanex/Operative/Data/TEMP/news/data/Crisismap - news.csv','r') as file:
        reader = csv.reader(file, delimiter = ';')
        for row in reader:
            dt.append(row[9].decode('utf-8') + '. ' + row[10].decode('utf-8'))
            labels.append(row[11])

    for text, toponyms in zip(dt, labels):
        words = data.get_tokens(text) # split to tokens
        if iseng(text): # if test is in English, we use English Language model
            ns = data.neurons(words, 1, eng_word2vec_model, lang = 'eng')

            prediction = lasagne.layers.get_output(eng_network, deterministic=True)
            predict_fn = theano.function([input_var], T.argmax(prediction, axis=1))
            pred = list(predict_fn(ns))
            predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
                                                                             # each one has a type (Location) and offsets (in terms of tokens)
            predicted = annots.setlabels(words,predannotations)  # list of  toponyms selected
        else: # if test is in Russian, we use Кгыышфт Language model
            ns = data.neurons(words, 1, rus_word2vec_model, lang = 'rus')


            prediction = lasagne.layers.get_output(rus_network, deterministic=True)
            predict_fn = theano.function([input_var], T.argmax(prediction, axis=1))
            pred = list(predict_fn(ns))
            predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
                                                                             # each one has a type (Location) and offsets (in terms of tokens)
            predicted = annots.setlabels(words,predannotations)  # list of  toponyms selected

        # three columns: news text - toponyms selected with compreno - toponyms selected with our model
        with open ('c:/Scanex/Operative/Data/TEMP/news/data/toponyms.csv', 'a+') as file:
            writer = csv.writer(file, delimiter = '\t')
            writer.writerow([text.encode('utf-8'), str(toponyms), ','.join(predicted).encode('utf-8')])
'''

if __name__ == '__main__':
  t = toponyms()
  t.test
  #main()
