import re
import csv
from collections import namedtuple
import codecs
#from fire_helper01 import check

#============dictionary =======================================================

negs = [u'не', u'не был', u'не было', u'не были', u'не была']

#По данным на утро 14 июля, в регионе зарегистрировано 22 очага на общей площади около 282 га
#-за лесных пожаров действует режим ЧС
#из-за лесных пожаров действовал режим чрезвычайной ситуации

fire = re.compile(u'(?<!из-за лесных )(пожар(ы|а|ов)?|очаг(а|ов)?|пламя|возгораний)[\s\.,;!](?!(на пшеничном поле|\sв\sквартире))')
#fire = re.compile(u'пожар[\.\s\Z]') #, re.UNICODE
fire1 = re.compile(u'(пожар(ы|а|ов)?|очаг(а|ов)?)[\.\s,;!](?!(на пшеничном поле|\sв\sквартире))')
began = re.compile(u'(произош[ёе]?л[аио]?|начал[аио]?ся?|вспыхнул[ио]?|начал[ои]? действовать|угрожа[ею]т|возник(ло)?)[\s\.,;!]')
emergency = re.compile(u'(пожароопасност[ьи]|пожароопасн([оы]й|ая|ую|ы[еx])|пожарная опасность|чрезвычайный класс пожарной опасности)')
#|
threat = re.compile(u'смог .*может прийти|увеличение возникновения очагов пожаров|росту? (числа )?(лесных )?пожаров|экстренное предупреждение|(введен|объявлен) режим чс|(экстремальная|аномальная) жара|площадь лесных пожаров .* (выросла|увеличилась) в 2.5 раза|быстрому распространению огня')
#тушили?
#otmenili = re.compile(u'отменен')
takes_place0 = re.compile(u'(бушу[ею]т|полыха[ею]т|действу[ею]т|зарегистрировали|зафиксировали|не могут ликвидировать|не ликвидирован|участились|туш[аи]т)[\s\.,;!]')
takes_place1 = re.compile(u'зарегистрирова(но|ны|н)|зафиксирова(но|ны|н)')

#эта новость в результате должна быть двойкой, потому что "был ликвидирован"
#Два лесных пожара  в воскресенье в Нижегородской области; Два лесных пожара тушили в минувшее воскресенье в
#Нижегородской области, сообщает региональное ГУ МЧС. Первое возгорание произошло в Павловском районе в 13:50. В 20:35 пожар был ликвидирован.
#это значит, что "тушили" говорит о пожаре, если нет "ликвидирован"
#проблема в том, что они находятся в разных предложениях, т.е. так легко эту логику не реализовать сейчас.
#"В Амурской области тушили лесной пожар в заповеднике" - эту новость вроде нужно отнести к 1
put_out = re.compile(u' тушили')
#сейчас проблема только с "не было зафиксировано"

liqu = re.compile(u'ликвидирова(ли|но|ны|н)|потушили|потушен(о|ы)?|останови(ли|но|ны|н)|локализова(ли|но|ны|н)')
succeed_liqu = re.compile(u'удалось (ликвидировать|потушить|остановить|локализовать)')
stop = re.compile(u'не допущено распространение|предотвратили')
better = re.compile(u'жара .*ослабеет|отменен режим чс|режим чс отменен|жара .*начнет ослабевать|жара пойдет на спад')
burns = re.compile(u'гор[яи]?т|спалили|площадь лесных пожаров .* (выросла|увеличилась)')
burns_str = u'огонь продолжает пожирать' #'огонь продолжает пожирать лес'
#"пожарной опасности", "противопожарный режим", "лесопожарной обстановки"
#пожарн([оы]й|ая|ую|ы[еx]) - не нужно, а то пожарные, которые просто помогают спасателям, тоже работают на 3
more_abstract = re.compile(u'жар[аы]|температур[аы] воздуха|пожарн(ой|ая)|противопожарн([оы]й|ая|ую|ы[еx])|лесопожарн([оы]й|ая|ую|ы[еx])|пожохран[аы]')
#burned = {'горел', 'сгорели'}
nonactual_modifiers = re.compile(u'(прошедшую неделю|прошлой неделе|в минувшие выходные|с\sначала 2014 года|с\sначала\sпожароопасного|\d+ года)', re.IGNORECASE)

#"С 15 апреля в крае из-за лесных пожаров действовал режим чрезвычайной ситуации."
#из-за таких примеров нужно всё-таки делать честное согласование

#===============grammar=========================================================================

def find_regexp(string, regex):
    s = re.search(regex, string)
    if s:
        found = s.group(0)
        coordinate = string.find(found)
        return (coordinate, coordinate + len(found))
    else: return (-1, -1)

def checkRight(substring, regex):
    coordinate = find_regexp(substring, regex)
    result = True if coordinate[1] == len(substring) and re.match('[\s\.,;!]', substring[coordinate[0]-1]) else False
    return result


def check(string, verb, negs):
    coord = find_regexp(string, verb)
    m = [checkRight(string[:coord[0]-1], neg) for neg in negs]
    if coord != (-1, -1) and not sum(m):
        return True
    else: return False

#==============internals of classification============================================================

class WrongFire(Exception): pass


def classify_sentence(sentence):
    sentence = sentence.lower()
    if re.search(u'в квартире', sentence): raise WrongFire
    elif re.search(fire1, sentence) and re.search(began, sentence) and not re.search(nonactual_modifiers, sentence): return 0
    elif re.search(emergency, sentence) and re.search(u'объявлен|ожидается', sentence)  and not re.search(nonactual_modifiers, sentence): return 0
    elif re.search(threat, sentence) and not re.search(nonactual_modifiers, sentence): return 0
    elif re.search(burns, sentence) or re.search(burns_str, sentence): return 1
    elif re.search(fire, sentence) and (re.search(takes_place0, sentence) or check(sentence, takes_place1, negs)) and not re.search(nonactual_modifiers, sentence): return 1
    elif re.search(fire, sentence) and re.search(liqu, sentence) or re.search(succeed_liqu, sentence) or re.search(stop, sentence): return 2
    elif re.search(better, sentence): return 2
    elif re.search(put_out, sentence): return 1
    #elif re.se
    elif re.search(fire1, sentence) or re.search(more_abstract, sentence): return 3
    elif re.search(emergency,sentence): return 3
    else: return 4

def classify_subtext(string):
    ss = re.split('[\.;]', string)
    scores = sorted([classify_sentence(s + '.') for s in ss])
    first = 2 if 2 in scores else scores[0]
    return first

#def classify_subtext(string):
    #p = re.compile(u'пожар')
    #if re.search(p, string)>-1: return 1

    #if string.find(u'пожар')>-1: return 1

#====================interface========================================================================
News = namedtuple('News', 'title body')

def classify_tuple(news_tuple):
        try:
            title  = classify_subtext(news_tuple.title)
            body = classify_subtext(news_tuple.body)
            predict = title if (body == 4 or title in [2, 1, 0]) else body
            #if body == 2: predict = body
        except WrongFire: predict = 4
        return predict

#======================testing==============================================================================

def test():
    some_news = [(u'Очередной лесной пожар произошел в Архангельской области,"По предварительным данным, причиной пожара стала сухая гроза. За период с 10 по 13 июля в регионе возникло семь лесных пожаров, пять из них были ликвидированы на малых площадях. Всего с начала пожароопасного сезона в области зафиксировано 50 «лесных» возгораний общей площадью порядка 300 гектаров."', 1), \
(u'На Ямале не осталось действующих природных пожаров,"На Ямале не осталось действующих природных пожаров. Однако в целях безопасности действует ограничение на посещение лесов. По данным региональной диспетчерской службы &quot;Леса Ямала&quot;, сегодня, 14 июля, на территории Ямало-Ненецкого автономного округа нет ни одного действующего лесного пожара', 3), \
(u'Эта новость вообще про бандикутов', 4), \
(u'Крупный лесной пожар бушует на Сахалине.', 1), \
(u'Режим пожарной опасности действует в области', 3),\
(u"Стоит жара", 3), \
(u'Пожар удалось остановить', 2)]
    for n in some_news:
        grade = classify_subtext(n[0])
        #if grade != n[1]: print grade, n[1], n[0]
        assert classify_subtext(n[0]) == n[1]



ScoredNews = namedtuple('ScoredNews', 'score title body')

def process(fname = 'new.txt'):
    def read_scored(fname):
        with codecs.open(fname) as fh:
            return [ScoredNews(*l.strip().split('\t')) for l in fh]
    i =0
    with codecs.open('log_' + fname, 'w', encoding = 'utf8') as lfile:
        for n in read_scored(fname):
            try:
                score = int(n[0])
                news = News(n[1].decode('utf-8'), n[2].decode('utf-8'))
                predict = classify_tuple(news)
                if predict != score:
                    log = u'automatically classified as {p}, manually as {cl}, {t}\n'.format(p =  predict, cl = score, t = '; '.join([n for n in news]))
                    #print log
                    lfile.write(log)
                    i+=1
            except Exception: print n[0]
    print i


#=======================score corpus========================================================================

def score_corpus():
    def read_file(fname):
        with codecs.open(fname, 'r', encoding = 'utf-8') as fh:
            return [l.split('\t') for l in fh]
    fname = 'merged00.csv'
    #fname ='p.csv'
    for n in read_file(fname)[40:60]:
        id = int(n[0])
        news = News(n[1], n[2])
        predict = classify_tuple(news)
        log = '\t'.join([str(id), str(predict), n[1], n[2]]) + '\n'
        print(log)

#===============================================================================================

def main():
    from sx_storage import sxDBStorage;
    dbsx = sxDBStorage();
    dbsx.ConnectMaps();
    fireNews = dbsx.LoadUnclassifiedFireNews();
    for fn in fireNews:
        news = News(fn["title"], fn["body"])
        predict = classify_tuple(news)
        dbsx.UpdateFireNewsClass(fn["id"], predict)
        #print(news, predict)
    
    return;
	
    import time
	
    begin = time.time()

    #test()
    #score_corpus()
    process()

    duration = time.time() - begin
    dif = '{0} minutes {1} seconds'.format(duration//60, round(duration%60, 2))
    print(dif)

if __name__ == '__main__':
    main()

