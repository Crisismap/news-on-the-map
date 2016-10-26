import re
import time
from collections import Counter
from collections import defaultdict
from itertools import chain
from optparse import OptionParser


import sys
version = 2 if sys.version[0] == '2' else 3
if version == 2: from codecs import open

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm


def is_ok(word, first, stopwords = [u'в', u"с", u"от", u"но", u"из", u"под", u"о", u"для",  u"к", u"по", u"за", u"на", u"не", u"бы", u"и", u"прот",  \
	u"эт", u"котор", u"что", u"как", u"тем", u"он", \
	u"сентябр", u"будут", u"времен"]):
                def is_ascii(s): return all(ord(c) < 128 for c in s)
                non_alphanumerics = re.compile('[\W_]+')
                def is_capitalized(word):return len(word)>1 and word[0].isupper() and all(x.islower() for x in word[1:])
                return not word.isdigit() and not is_ascii(word) and not word in stopwords and (not is_capitalized(word) or word == first)


def complex(s):
    verbal = re.compile(u'не\s+((могут|удается|получается)\s+)?\w+')
    m = re.search(verbal, s)
    if m:
        group = m.group(0)
        complex = re.sub('\s+', '', group)
        return s.replace(group, complex)
    else: return s


def sentence2words(sentence):
    word_boundary = re.compile('[\-\s \) \( ,;"»]+', re.VERBOSE | re.UNICODE)
    non_alphanumerics = re.compile('[\W_]+', re.UNICODE)
    def get_first(it):
        for elem in it:
            if elem.strip():
                return elem
            if not sentence: return None
    try:
        words = (complex(non_alphanumerics.sub('', word)) for word in re.split(word_boundary, sentence))
        words = (word for word in words if word)
        first_word = get_first(words)
        #words = (stemmer.stem(word) for word in words if is_ok(word, first_word))
        words = (word for word in words if is_ok(word, first_word))
    except Exception as err: print (err) #('ha')
    return words

def txt2words(txt):
	sentence_splitter = re.compile('[\.?!]+')
	sentences = [list(sentence2words(sentence)) for sentence in re.split(sentence_splitter, txt) if sentence]
	return chain.from_iterable(sentences)


def file2data(fname):
	data = []; news = []
	scores = []
	with open(fname, encoding = 'utf8') as fh:
		for row in fh:
			spl = row.strip().split('\t')
			txt0 = u'\t'.join([spl[1], spl[1], spl[2]]); txt1 = u'\t'.join([spl[1], spl[2]])
			data.append(list(txt2words(txt0))); news.append(txt1)
			scores.append(int(spl[0]))
	return np.array([u' '.join(elem) for elem in data]), np.array(scores), np.array(news)


def learn():
    data, labels, news = file2data('data/scored_corpus.csv')
    splitter = str.split if version == 3 else unicode.split
    vectorizer = TfidfVectorizer(analyzer = splitter)
    func = svm.SVC(kernel='linear')
    clf = Pipeline( [('vect', vectorizer), ('clf', func)])
    clf.fit(data, labels)
    return clf

def predict(news, clf):
    txt = u'\t'.join([news[0], news[0], news[1]])
    return clf.predict([txt])


if __name__ == '__main__':
    model = learn()

    n0 = (u'Сотрудники лесоохраны проинспектировали новосибирские леса с воздуха.', u'В апреле парашютисты спасали леса Кыштовского и Северного районов.')
    n1 = (u'В Ярославской области снова горят торфяники', u'Угрозы для населенных пунктов нет Пожар обнаружен в десять часов утра 14 июня в Воскресенском лесничестве Некоузского района. На месте работают местные пожарные подразделения и сотрудники спецучреждения &quot;Лесная охрана&quot;. К четырем часам дня удалось локализовать пожар на площади три гектара.')

    print (predict(n0, model))
    print (predict(n1, model))





