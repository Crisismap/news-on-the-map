import re
import csv
from collections import namedtuple
import codecs

sep = '[\s\.,;!:\b]'

def j(l):
    return '|'.join(l)

def jsep(l):
    return '(' + '|'.join(l) + ')' + sep

#============dictionary =======================================================

wrong_fire =  [u'в квартире', u'в .*доме', u'в гараже', u'в строении', u'в автомобиле', u'в ресторане', u'в .*сарайчиках',\
u'возгорани.*(автомобил|квартир)', u'загорани.*автомобил', u'автомобиль горит', \
u'в .*поезде', u'вагон', u'.*вокзале', u'нефтепроводе', u'пожара? нефтепровода', u'возгоранием .*нефтепровода', \
u'с?горел.*(дом|автомобил|квартир|барак|сарай|землянк)', u'(дом|автомобил|квартир|барак|сарай|землянк).*с?горел', u'учения мчс', \
u'судне', u'на корабле', u'загорелся .*поезд', u'на .*рынке', u'в наркодиспансер', u'техногенных пожаров', u'в коллекторе теплотрассы']
#, \
wrong_fire = re.compile(jsep(wrong_fire))

training_fire = [u'условный лесной пожар', u'условное возгорание', u'согласно легенде']
training_fire = re.compile(jsep(training_fire))

not_so_serious = [u'локальный лесной пожар']
#not_so_serious = re.compile(jsep(not_so_serious))

nonactual_modifiers = [u'прошедшую неделю', u'прошлой неделе', u'в минувшие выходные', \
u'с начала 2014 года', u'с начала (пожароопасного |\d+)?(года|сезона|периода)', u'2010 года', \
u'в течение .*пожароопасного сезона', u'в 201\d году', u'первый лесной пожар', u'последний лесной пожар', u'в этом году',
u'в октябре']
not_so_actual_modifiers = [u'за минувшие сутки', u'в минувшие сутки']
nonactual_modifiers = re.compile(jsep(nonactual_modifiers + not_so_serious), re.UNICODE | re.IGNORECASE)

#
fire = [u'пожар(ы|а|ов)?', u'очаг(а|ов)? горения']
fire_additional = [u'пламя', u'возгораний', u'огонь']
fire = re.compile(u'(?<!из-за лесных )' + jsep(fire + fire_additional))

#0
began = [u'начал[аио]?ся?', u'вспыхнул[ио]?', u'начал[ои]? действовать', u'угрожа[ею]т', u'возник(ло|и)?', u'случился',
u'обнаружены?', u'быстро распространил(ись|ся)']
began = re.compile(jsep(began))

#u'загорел[оаи]сь',
fire_began = [u'молния подожгла лес', u'огонь продолжает пожирать', u'загорелись .*леса']
fire_began = re.compile(jsep(fire_began))

#, u'особый противопожарный режим' - то ли нужен, то ли нет
emergency = [u'(высок|чрезвычайн)(ая|ой) пожароопасност[ьи]', u'пожароопасн([оы]й|ая|ую|ы[еx])', \
    u'чрезвычайный класс пожарной опасности', u'(введен\s|объявлен|ввели).*режим (чс|чрезвычайной ситуации)', \
    u'режим (чс|чрезвычайной ситуации).*(введен\s|объявлен|ввели)']
    #u'(введен\s|объявлен).*режим чс'
    #u'пожарная опасность', u'чрезвычайная пожарная опасность'
    #u'особый противопожарный режим', u'режим чс'
    #
emergency = re.compile(jsep(emergency))

threat = [u'смог .*может прийти', u'увеличение возникновения очагов пожаров', u'росту? (числа )?(лесных )?пожаров', u'экстренное предупреждение', \
        u'(экстремальная|аномальная) жара', u'площадь лесных пожаров .* (выросла|увеличилась) в .*раза', \
        u'быстрому распространению огня', u'сообщают о запахе гари', u'(появился|вернулся) запах гари', \
        u'может появиться запах гари', u'выявлен новый очаг пожара', u'угроза для жизни и здоровья', \
        u'загрязнение воздуха .*превысило норму',  u'превышена пдк продуктов горения', u'дымом от торфяников заволокло', \
        u'грядет смог', u'штормовое предупреждение', u'пожар.*уничтожил', u'уничтожил.*пожар', \
        u'(возросло|увеличилась|выросла|растет).*(число|количество|площадь) (лесн(ых|ого) )?пожар(а|ов)',
        u'(число|количество|площадь) (лесн(ых|ого) )?пожар(а|ов).*(возросло|увеличилась|выросла|растет)',
        u'распространился на .*площадь', u'площадь лесного пожара .*достигла', u'пожар .*подобрался к',
        u'(эвакуируют|эвакуированы) .*из-за лесного пожара']
threat = re.compile(jsep(threat))
#u'площадь лесных пожаров .* (выросла|увеличилась)',

#1
takes_place0 = [u'бушу[ею]т', u'полыха[ею]т', u'действу[ею]т', u'зарегистрировали', u'зафиксировали',\
    u'участились', u'охватил', u'продолжается', u'продолжает действовать', \
    u'\sне ликвидирован',  u'\sне могут ликвидировать', u'остаются не\s?потушенными', u'\sне могут потушить', u'не стихает',\
    u'не прекращается', u'не удается потушить',\
    u'туш[аи]т', u'осталось потушить', u'обещает потушить .*пожары',u'продолжают тушить', u'пытаются потушить',\
    u'надеются ускорить ликвидацию', u'проводится комплекс мероприятий по ликвидации возгораний',\
    u'тушить пожар .*стало', u'продолжается ликвидация', u'распорядился .*погасить', u'отправились тушить']
takes_place0 = re.compile(jsep(takes_place0))

takes_place1 = [u'зарегистрирова(но|ны|н)', u'зафиксирова(но|ны|н)', u'произош[ёе]?л[аио]?']
takes_place1 = re.compile(jsep(takes_place1), re.UNICODE)

burns = [u'гор[яи]?т', u'спалили', u'продолжают гореть', \
    u'ликвидируют .*очаг возгорания', u'продолжают тлеть', u'дым от горящих торфяников стал заметен', u'продолжают тушить торфяники',\
     u'охвачены.*(пожарами|огнем)', u'поступило сообщение о загорании', ]
burns = re.compile(jsep(burns), re.UNICODE)

#2
liqu = [u'ликвидирова(ли|но|ны|н)', u'потушили', u'потушен(о|ы)?', u'останови(ли|но|ны|н)', u'локализова(ли|но|ны|н)', \
    u'удалось (ликвидировать|потушить|остановить|локализовать|сократить площадь)', u'не допущено распространение', u'предотвратили', \
    u'площадь (лесных |природных )?пожаров .*(уменьшилась|сокращается|сократилась)',
    u'(уменьшилась|сокращается|сократилась) .*площадь (лесных |природных )?пожаров',
    u'стабилизируется', u'работы по тушению .*подходят к концу', \
    u'остановили распространение', u'пошел на убыль', u'ситуация с пожаром .*контролируется']
liqu = re.compile(jsep(liqu))

better = [u'жара .*ослабеет', u'(отменен|снят) режим (чс|чрезвычайной ситуации)', u'режим (чс|чрезвычайной ситуации) .*(отменен|сняли)', \
    u'жара .*начнет ослабевать', u'жара пойдет на спад']
better = re.compile(jsep(better))

#3
#"пожарной опасности", "противопожарный режим", "лесопожарной обстановки"
#пожарн([оы]й|ая|ую|ы[еx]) - не нужно, а то пожарные, которые просто помогают спасателям, тоже работают на 3
#сейчас не используем "тушили", "обводняют"
put_out = [u'залить водой .*торфяники', u'удалось спасти от (лесного )?пожара', u'справиться с огнем удалось']
put_out = re.compile(jsep(put_out))

more_abstract = [u'жар[аы]', u'температур[аы] воздуха', u'пожарн(ой|ая)', u'противопожарн([оы]й|ая|ую|ы[еx])', u'лесопожарн([оы]й|ая|ую|ы[еx])', \
    u'пожохран[аы]', u'берегите лес', u'из-за задымления', u'запах[ае]? гари', u'(жечь|жгут|спалил|спалить|сжег) .*леса?', u'леса .*жгут', u'выгорело']
more_abstract = re.compile(j(more_abstract))

#"С 15 апреля в крае из-за лесных пожаров действовал режим чрезвычайной ситуации."
#из-за таких примеров нужно всё-таки делать честное согласование

#==============internals of classification============================================================

def check_tuple(source, t):
    results = []
    for elem in t:
        m = re.search(elem, source)
        if m: results.append(m.group(0))
        else: return False
    return results

def ch(source, negative, *positive):
    results = []
    if negative:
        m = re.search(negative, source)
        if m: return []
    for p in positive:
        if isinstance(p, tuple):
            res = check_tuple(source, p)
            if res: return res
        else:
            m = re.search(p, source)
            if m: return [m.group(0)]
    return results

#на данный момент бессмысленная обертка
def check(source, negative, *positive):
    result = ch(source, negative, *positive)
    return result

def chech_neg(sentence, result):
    negs = u' не (был[оаи]? )?'
    ns = []
    for r in result:
        s = negs + r
        neg = ch(sentence, '', s)
        if neg:
                ns.extend(neg)
    return ns

class WrongFire(Exception): pass
class Training(Exception):pass
class English(Exception): pass

def is_cyrillic(symbol): return ord(symbol)>128
def cyr(word): return any([is_cyrillic(s) for s in word])


def classify_sentence(sentence):
    sentence = sentence.lower().replace('  ', ' ')

    if re.search(wrong_fire, sentence): raise WrongFire

    if re.search(training_fire, sentence): raise Training

    result = check(sentence, nonactual_modifiers, (fire, began), (emergency, u'объявлен|введен|ожидается|ввели|сохранится'), threat, fire_began)
    if result:
        if not chech_neg(sentence, result): return (0, result)
        #return (0, result)

    result = check(sentence, nonactual_modifiers, (fire, takes_place0), (fire, takes_place1), burns)
    if result:
        if not chech_neg(sentence, result): return (1, result)

    result = check(sentence, nonactual_modifiers, better, (fire, liqu), put_out)
    if result: return (2, result)

    result = check(sentence, '', fire, more_abstract, emergency)
    if result: return (3, result)

    else: return (4, '')

def classify_subtext(string):
    if not cyr(string): raise English
    ss = re.split('[\.;]', string)
    scores = sorted([classify_sentence(s + ' .')[0] for s in ss])
    first = 2 if 2 in scores else scores[0]
    return first

#====================interface========================================================================
News = namedtuple('News', 'title body')

def classify_tuple(news_tuple, log = False):
        try:
            title  = classify_subtext(news_tuple.title)
            body = classify_subtext(news_tuple.body)
            predict = title if (title<body or title ==2) else body
            #if body ==2: predict = 2 #в принципе результаты ничего, но формально ухудшение
            if log: print title, body
        except English: predict = 5
        except WrongFire: predict = 4
        except Training: predict = 3
        return predict


#=================testing =============================================
Result = namedtuple('Line', 'int news predict')
#обертка для отладки:
def class_tuple(string):
    news = News(string.split('|')[0], string.split('|')[1])
    return classify_tuple(news, log = True)

def read_file(fname):
        with codecs.open(fname) as fh:
            return [l.strip().split('\t') for l in fh]

def transf(listOfTuples, begin=0, end = None):
        if end is None: end = len(listOfTuples)
        result = []
        for elem in listOfTuples[begin:end]:
            if len(elem) ==3:
                integer = int(elem[0])
                news = News(elem[1].decode('utf-8') + u' ', elem[2].decode('utf-8') + u' ')
                predict = classify_tuple(news)
                result.append(Result(integer, news, predict))
        return result

def process(fname = 'markup.txt'):
    misclassified = []
    for n in transf(read_file(fname)):
        if n.int != n.predict:
            misclassified.append(n)


    logs = set([u'automatically classified as {predict}, manually as {int}, {txt}'.format(predict =  m.predict, int = m.int, txt = j(m.news)).strip() for m in misclassified])
    with codecs.open('log_' + fname) as lfile:
        lines = set([line.decode('utf-8').strip() for line in lfile])

    remained = logs.intersection(lines)
    new = logs.difference(lines)
    old = lines.difference(logs)

    print "New:"
    for n in new:
        print n

    print "Old:"
    for o in old:
        if o: print o

    print len(misclassified)

    with codecs.open('log_' + fname, 'w', encoding = 'utf8') as lfile:
        for m in misclassified:
            log = u'automatically classified as {predict}, manually as {int}, {txt}\n'.format(predict =  m.predict, int = m.int, txt = j(m.news))
            lfile.write(log)

#=======================score corpus========================================================================

Res = namedtuple('Res', 'number score txt')

def corpus_diff(fname = 'corpus.csv'):
    try:
        with open('log_'+ fname) as old:
            old_results = [Res(line.strip.split('\t')) for line in old]
    except IOError: pass
    for n in transf(read_file(fname)):
            log = '\t'.join([str(n.int), str(n.predict), n.news.title, n.news.body]) + '\n'
            print(log)


def score_corpus(fname = 'corpus.csv', lower = 3000, higher = 4000):
    with codecs.open('scored_' + fname, 'w', encoding = 'utf8') as log:
        for n in transf(read_file(fname), lower, higher):
            log.write('\t'.join([str(n.predict), n.news.title, n.news.body]) + '\n')
            #log = '\t'.join([str(n.int), str(n.predict), n.news.title, n.news.body]) + '\n'


#===============================================================================================

def main():
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

