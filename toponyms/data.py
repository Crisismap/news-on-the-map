#-*- coding: UTF-8 -*-
import pymorphy2
import numpy as np
import os,csv
import re
import lasagne
np.set_printoptions(threshold='nan')

morph = pymorphy2.MorphAnalyzer()

def grammar_token(token):
    if len(morph.parse(token)) > 0:
        t = ''
        for gram in morph.parse(token)[0].tag.grammemes:
            t += ('_'+str(gram))
    else:
        t = token
    return t

def normal_form (token):
    if len(morph.parse(token)) > 0:
        return morph.parse(token)[0].normal_form
    else:
        return token


def rus_vector(word, model):
    n_cap = int(word.isupper() or (word.isalpha() and not word.isupper() and not word.islower()))
    #n_cap = 0
    if normal_form(word)  in model.vocab and grammar_token(word) in model.vocab:
        #print 'qq'
        return np.hstack((model[normal_form(word)],model[grammar_token(word)], [n_cap,]))
    elif grammar_token(word) in model.vocab:
        #print 'kk'
        return np.hstack((model['unk'], model[grammar_token(word)], [n_cap,]))
    else:
        #print 'll'
        return np.hstack((model['unk'], np.zeros((model.vector_size, )), [n_cap,]))

def eng_vector(word, model):
    n_cap = int(word.isupper() or (word.isalpha() and not word.isupper() and not word.islower()))
    if word.lower()  in model.vocab :
        return np.concatenate((model[word.lower()], [n_cap,]))
    else:
        return np.concatenate((model['unk'], [n_cap,]))


def neurons(words, winsize, model, lang = 'rus'):
    l = len(words)
    #words = [u'<fullstop>'] * winsize + words[: -1] + [u'<fullstop>'] * winsize
    words = [u'<fullstop>'] * winsize + words[:-1] + [u'<fullstop>'] * winsize
    if lang == 'rus':
        ns = np.empty((l - 1, (2*winsize + 1), (model.vector_size * 2 + 1)))
        for i in xrange(winsize, len(words)-winsize):
            ns[i - 1, :, :] = np.vstack((rus_vector(words[i - winsize], model),
                                     rus_vector(words[i], model), rus_vector(words[i + winsize], model)))

    else:
        ns = np.empty((l - 1, (2*winsize + 1), (model.vector_size + 1)))
        for i in xrange(winsize, len(words)-winsize):
            ns[i - 1, :, :] = np.vstack((eng_vector(words[i - winsize], model),
                                     eng_vector(words[i], model), eng_vector(words[i + winsize], model)))


    return ns

def mklsts (CORPUS, files, winsize,  word2vec, lang = 'rus'):
    WORDS, CLS = [], []
    if lang == 'rus':
        Ns = np.empty((0,winsize * 2 + 1, word2vec.vector_size * 2 + 1))
    else:
        Ns = np.empty((0,winsize * 2 + 1, word2vec.vector_size + 1))
    for file in files:
        with open (os.path.join(CORPUS, file), 'r') as f:
            words,cls = [], []
            reader = csv.reader(f, delimiter = '\t')
            for row in reader:
                words.append(row[0].decode('utf-8'))
                cls.append(int(row[1]))
            n = neurons(words, winsize, word2vec, lang = lang)
            WORDS.extend(words)
        CLS.extend(cls[:-1])
        Ns = np.concatenate((Ns, n))
#    target = np.zeros((len(CLS), 3))
#    for i in xrange(len(CLS)):
#        target[i][CLS[i]] = 1
    return Ns,  WORDS, np.asarray(CLS, dtype = 'int32')

def get_tokens(text):
    text = re.sub(ur'&quot;', ur'"', text)
    text = re.sub(ur'([\.,:;!\?\=\-—/&])', ur' \1 ', text)
    text = re.sub(ur'([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-zA-Z\+])(["»„\)])', ur'\1 \2', text)
    text = re.sub(ur'([\(“"«])([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-z-A-Z\+])', ur'\1 \2', text)
    text = re.sub(ur'[ ]+', ' ', text)
    words = text.split()
    return words


def Pr (result, response):
    try:
        return  len(result.intersection(response))/float(len(result))
    except:
        print 'no true results'
        return 0

def Re (result, response):
    try:
        return len(response.intersection(result))/float(len(response))
    except:
        print 'no true responses'
        return 0

def f1(result, response):
    try:
        return 2 * Pr(result, response) * Re(result, response) / float(Pr (result, response) + Re(result, response) )
    except:
        print 'invalid f1'
        return 0


def build_mlp(shape, input_var=None):
    network = lasagne.layers.InputLayer(shape=shape[0],
                                     input_var=input_var)
    #l_in_drop = lasagne.layers.DropoutLayer(l_in, p=0.2)
    for hid in shape[1:]:
        network = lasagne.layers.DenseLayer(
            network, num_units=hid,
            nonlinearity=lasagne.nonlinearities.sigmoid,
            W=lasagne.init.GlorotUniform())
    #l_hid1_drop = lasagne.layers.DropoutLayer(l_hid1, p=0.5)
    network = lasagne.layers.DenseLayer(
        network, num_units=3,
        nonlinearity=lasagne.nonlinearities.softmax)
    return network

def iterate_minibatches(inputs, targets, batchsize, shuffle=False):
    print len(inputs), len(targets)
    assert len(inputs) == len(targets)
    if shuffle:
        indices = np.arange(len(inputs))
        np.random.shuffle(indices)
    for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batchsize]
        else:
            excerpt = slice(start_idx, start_idx + batchsize)
        yield inputs[excerpt], targets[excerpt]