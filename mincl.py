import string
import csv
import time
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from nltk import word_tokenize

import sys
version = 2 if sys.version[0] == '2' else 3
if version == 2: from codecs import open

stopwords = [u'в', u"с", u"от", u"но", u"из", u"под", u"о", u"для",  u"к", u"по", u"за", u"на", u"не", u"бы", u"и", u"прот",  \
	u"эт", u"котор", u"что", u"как", u"тем", u"он", u"сентябр", u"будут", u"времен", u"об", u"без", u"нет", u"во"]

def timing(func):
    def wrapper(*args, **kwargs):
        begin = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        ellapsed = end - begin
        print ('{0} min. {1} sec. in function {2}'.format(int(ellapsed//60), round(ellapsed%60, 2), func.__name__))
        return result
    return wrapper

def tokenize(text):
    def is_ok(item, stemmer):
        return True if item.lower() == item and all((elem.isalpha() and not elem in string.ascii_letters and not stemmer.stem(item) in stopwords) for elem in item) else False
    from nltk.stem.snowball import RussianStemmer
    stemmer = RussianStemmer(ignore_stopwords=True)
    tokens = word_tokenize(text)
    return [item for item in tokens if is_ok(item, stemmer)]

def tokenize_en(text):
    def is_ok(item):
        return True if item.lower() == item and all(elem.isalpha() and elem in string.ascii_letters for elem in item) else False
    from nltk.stem.snowball import EnglishStemmer
    stemmer = EnglishStemmer(ignore_stopwords=True)
    tokens = word_tokenize(text)
    result = [stemmer.stem(item) for item in tokens if is_ok(item)]
    return result

@timing
def file2data(fname):
    data = []
    labels = []
    with open(fname, encoding = 'utf8') as fh:
        for row in unicode_csv_reader(fh):#(fh, delimiter  = '\t'):
            try:
                if len(row) == 3:
                    score, header, body = row
                elif len(row) == 2: pass
                txt = u'\t'.join([header, header, body])
                labels.append(int(score))
                data.append(txt)
            except ValueError: pass
    return data, np.array(labels)


def clf_factory(stopwords = stopwords, lang = 'ru'):
    if lang == 'en':
        vect = TfidfVectorizer(stop_words = 'english', lowercase = False, tokenizer = tokenize_en)
    else:
        vect = TfidfVectorizer(stop_words = stopwords, lowercase = False, tokenizer = tokenize)
    func = svm.SVC(kernel='linear')
    return Pipeline( [('vect', vect), ('clf', func)])


@timing
def learn(fname, lang = 'ru'):
    data, labels = file2data(fname)
    clf = clf_factory(lang = lang)
    print ("Hello")
    clf.fit(data, labels)
    print ("Bye")
    return clf

def predict(news, clf):
    txt = u'\t'.join([news[0], news[0], news[1]])
    return clf.predict([txt])

    
def unicode_csv_reader(unicode_csv_data):    
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), delimiter  = '\t') # csv.py doesn't do Unicode; encode temporarily as UTF-8
    for row in csv_reader: # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

        
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
    
    
if __name__ == '__main__':
    lang = 'ru'

    filenames = dict(en = 'c:/sx/Operative/NewsRss/data/scored_corpus_fires_eng.csv', ru = 'c:/sx/Operative/NewsRss/data/scored_corpus.csv')
    model = learn(fname  = filenames[lang], lang = lang)

    test_news = dict(ru  = u"""Росавиация: запрет Киевом транзита может означать отсутствие гарантий безопасности полетов\tВ среду Госавиаслужба Украины уведомила
    Росавиацию о введении с 26 ноября запрета на транзитное использование своего воздушного пространства для всех российских авиакомпаний.
    ПМОСКВА, 25 ноября. /ТАСС/. Последние действия Киева, вероятно, указывают на то, что украинская сторона вновь не гарантирует безопасность
    полетов, заявили ТАСС в пресс-службе Росавиации.""",
    en = u"""End destructive practice of logging forests after wildfires - Sacramento Bee,"When it comes to wildfire , the U.S. Forest Service
    has it all wrong. In its just-released plan to chop down trees in nearly 17,000 acres hit by last year's King fire in the Eldorado National Forest –
    including logging in 28 occupied spotted owl ...\"""")

    print(predict(test_news[lang], model))
