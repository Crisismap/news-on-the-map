#-*- coding: UTF-8 -*-
import numpy as np
import data

import csv
import random
from gensim.models import word2vec
import os
import theano
import theano.tensor as T
import time
import sys
from sklearn.metrics import f1_score
import annots
import lasagne

CORPUS = '/home/anna/Documents/News Classifier/CF-eng'  # english trainig corpus
winsize = 1
modelfile = '/home/anna/Documents/NER/news vector space model/english-wiki-vectors/wiki-100.model'
word2vec_model = word2vec.Word2Vec.load_word2vec_format(modelfile, binary=False)



def main(shape, model='mlp', num_epochs=500):
    # whole corpus
    files = os.listdir(CORPUS)
    random.shuffle(files)

    fs1 = files[:1200] #train
    fs2 = files[1201:1500] #evaluate
    fs3 = files[1501 : ] #test

    #train data + evaluation data
    X_train, words_train, y_train = data.mklsts(CORPUS, fs1, winsize, word2vec_model, lang = 'eng')
    X_val,  words_val, y_val = data.mklsts(CORPUS, fs2, winsize, word2vec_model, lang = 'eng')

    # we build the net
    input_var = T.dtensor3('inputs')
    target_var = T.ivector('targets')
    network = data.build_mlp(shape, input_var)

    prediction = lasagne.layers.get_output(network)
    loss = lasagne.objectives.categorical_crossentropy(prediction, target_var)

    loss = loss.mean() + 1e-4 * lasagne.regularization.regularize_network_params(
        network, lasagne.regularization.l2)

    params = lasagne.layers.get_all_params(network, trainable=True)
    updates = lasagne.updates.nesterov_momentum(loss, params, learning_rate=0.01, momentum=0.9)


    eval_prediction = lasagne.layers.get_output(network, deterministic=True)
    eval_loss = lasagne.objectives.categorical_crossentropy(eval_prediction,
                                                           target_var)
    eval_loss = eval_loss.mean()

    eval_acc = T.mean(T.eq(T.argmax(eval_prediction, axis=1), target_var),
                      dtype=theano.config.floatX)


    train_fn = theano.function([input_var, target_var], loss, updates=updates)
    val_fn = theano.function([input_var, target_var], [eval_loss, eval_acc])

    # and train it
    for epoch in range(num_epochs):
        # In each epoch, we do a full pass over the training data:
        train_err = 0
        train_batches = 0
        start_time = time.time()

        for batch in data.iterate_minibatches(X_train, y_train,  100, shuffle=True):
            inputs, targets = batch
            train_err += train_fn(inputs, targets)
            train_batches += 1

        # And a full pass over the validation data:
        val_err = 0
        val_acc = 0
        val_batches = 0
        for batch in data.iterate_minibatches(X_val, y_val, 100, shuffle=False):
            inputs, targets = batch
            err, acc = val_fn(inputs, targets)
            val_err += err
            val_acc += acc
            val_batches += 1

        # Then we print the results for this epoch:
        print "Epoch %d of %d took % 3f s" % (epoch + 1, num_epochs, time.time() - start_time)
        #print train_err, train_batches
        #print val_err, val_batches
        print"  training loss:\t\t%6f" % (train_err / train_batches)
        print"  validation loss:\t\t%6f" % (val_err / val_batches)
        print"  validation accuracy:\t\t%6f"% (val_acc / val_batches)


    #we delete train and evaluate data
    del X_train,  words_train, y_train, X_val, words_val, y_val

    #we save the network for future!
    np.savez('/home/anna/Documents/News Classifier/model-eng.npz', *lasagne.layers.get_all_param_values(network))

    #test data
    X_test,  words_test, y_test = data.mklsts(CORPUS, fs3, winsize, word2vec_model, lang = 'eng')

    #then we make a prediction on test data
    test_prediction = lasagne.layers.get_output(network, deterministic=True)
    predict_fn = theano.function([input_var], T.argmax(test_prediction, axis=1))
    pred = list(predict_fn(X_test))

    # create a set of Annotations, each one has a type (Location) and offsets (in terms of tokens)
    predannotations = annots.setAnnotations(pred,  {1: 'Location'}, exactness = 'lenient')
    clsannotations = annots.setAnnotations(y_test,  {1: 'Location'}, exactness = 'lenient')


    print 'Lenient Precision score = %s' % data.Pr(predannotations, clsannotations)
    print 'Lenient Recall = %s' % data.Re(predannotations, clsannotations)
    print 'Lenient F1 score = %s' % data.f1(predannotations, clsannotations)

    predannotations = annots.setAnnotations(pred,  {1: 'Location'})
    clsannotations = annots.setAnnotations(y_test,  {1: 'Location'})

    print 'Strict Precision score = %s' % data.Pr(predannotations, clsannotations)
    print 'Strict Recall score = %s' % data.Re(predannotations, clsannotations)
    print 'Strict F1 score = %s' % data.f1(predannotations, clsannotations)

    for file in fs3:
        X_test,  words_test, y_test = data.mklsts(CORPUS, [file], winsize, word2vec_model, lang = 'eng')

        pred = list(predict_fn(X_test))# for _ in X_test)
        predannotations = annots.setAnnotations(pred,  {1: 'Location'})# exactness = 'lenient')
        clsannotations = annots.setAnnotations(y_test,  {1: 'Location'})#, exactness = 'lenient')
        predlabels = annots.setlabels(words_test, predannotations)
        clslabels = annots.setlabels(words_test, clsannotations)

        # in each row: text , correct (compreno) label , our prediction
        with open('/home/anna/Documents/News Classifier/eng-toponyms.csv', 'a+') as file:
            writer = csv.writer(file, delimiter = '\t')
            writer.writerow([' '.join(words_test).encode('utf-8'), ', '.join(clslabels).encode('utf-8'), ', '.join(predlabels).encode('utf-8')])


if __name__ == '__main__':
    main(((None,winsize * 2 + 1,word2vec_model.vector_size + 1), 150), num_epochs = 500)

