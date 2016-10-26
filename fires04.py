import re
import csv
from collections import namedtuple

#По данным на утро 14 июля, в регионе зарегистрировано 22 очага на общей площади около 282 га
#-за лесных пожаров действует режим ЧС
#из-за лесных пожаров действовал режим чрезвычайной ситуации
fire = re.compile('(?<!из-за лесных )(пожар(ы|а|ов)?|очаг(а|ов)?)(?!(\w| на пшеничном поле|\sв\sквартире))')
fire1 = re.compile('(пожар(ы|а|ов)?|очаг(а|ов)?)(?!(\w| на пшеничном поле|\sв\sквартире))')
takes_place0 = re.compile('(?<!не )(произош[ёе]?л[аио]?|начал[аио]?ся?|бушу[ею]т|действу[ею]т|зарегистрировали|зафиксировали|начал[ои]? действовать|не могут ликвидировать|не ликвидирован|угрожа[ею]т|возник(?!\w)|участились)')

takes_place1 = re.compile('(?<! не )зарегистрирова(но|ны|н)')
#сейчас проблема только с "не было зафиксировано"
takes_place2 = re.compile('(?<!не )зафиксирова(но|ны|н)')

liqu = re.compile('(?<!не )ликвидирова(ли|но|ны|н)|потушили|потушен(о|ы)?|останови(ли|но|ны|н)|локализова(ли|но|ны|н)|тушили')
succeed_liqu = re.compile('(?<!не )удалось (ликвидировать|потушить|остановить|локализовать)')
burns = re.compile('гор[яи]?т|спалили')
burns_str = 'огонь продолжает пожирать' #'огонь продолжает пожирать лес'
#"пожарной опасности", "противопожарный режим", "лесопожарной обстановки"
more_abstract = re.compile('жара|жары|температура воздуха|пожароопасност[ьи]|пожароопасный|пожарной|противопожарный|лесопожарной')
#burned = {'горел', 'сгорели'}
nonactual_modifiers = re.compile('(за\sпрошедшую\sнеделю|на\sпрошлой\sнеделе|в минувшие выходные|с начала 2014 года|c\sначала\sпожароопасного\sпериода\s2014\sгода)')

#"С 15 апреля в крае из-за лесных пожаров действовал режим чрезвычайной ситуации."
#из-за таких примеров нужно всё-таки делать честное согласование

class WrongFire(Exception): pass

def classify(sentence):
    sentence = sentence.lower()
    if re.search('пожар\sв\sквартире', sentence): raise WrongFire
    elif re.search(burns, sentence) or re.search(burns_str, sentence): return 1
    elif re.search(fire, sentence) and (re.search(takes_place0, sentence) or re.search(takes_place1, sentence) or re.search(takes_place2, sentence)) and not re.search(nonactual_modifiers, sentence): return 1
    elif re.search(fire, sentence) and re.search(liqu, sentence): return 2
    elif re.search(fire, sentence) and re.search(succeed_liqu, sentence): return 2
    elif re.search(fire1, sentence) or re.search(more_abstract, sentence): return 3
    else: return 4

def tell(string):
    ss = re.split('[\.;]', string);
    scores = sorted([classify(s) for s in ss]); #print(scores)
    first = scores[0]
    #second = scores[1] if len(scores) > 1 else None
    #result = (first, second) if second and second ==2 else first
    #return result
    return first


def is_english(string):
    english_words = ['the', 'in', 'no', 'of', 'a', 'to', 'for', 'he', 'as', 'on', 'by']
    words = set(string.split())
    #print(words)
    score = sum([1 for word in english_words if word in words])
    if score > 3: return True
    else: return False

n = "LeBaron: Historic wildfires' catastrophic lessons - Santa Rosa Press Democrat  But in between  wildfires  — with no evacuation orders, no TV reporters standing in front of the flames, no front page headlines counting the thousands of acres burned — we might be tempted to forget just how quickly fires move and how much damage they ... "


def to_int(value, index): return int(value.strip().rstrip('?').split(',')[index])

News = namedtuple('News', 'title body')

def mk_txts(fname = 'News_classified_v28.07.csv'):
    with open(fname, encoding = 'utf-8') as scored:
        txts = []
        splitted_lines = [line.split('\t') for line in scored]
        txts = [News(sl[7], sl[8]) for sl in splitted_lines]
        scores = [min(to_int(sl[4], 0), to_int(sl[4], -1)) for sl in splitted_lines]
        return txts, scores

def process(n):
        title  = tell(n[0])
        body = tell(n[1])
        predict = title if (body == 4 or title in [2, 1]) else body
        return predict
        #print(predict, n[0], n[1])

def main():
    import time
    some_news = [('Очередной лесной пожар произошел в Архангельской области,"По предварительным данным, причиной пожара стала сухая гроза. За период с 10 по 13 июля в регионе возникло семь лесных пожаров, пять из них были ликвидированы на малых площадях. Всего с начала пожароопасного сезона в области зафиксировано 50 «лесных» возгораний общей площадью порядка 300 гектаров."', 1), \
('На Ямале не осталось действующих природных пожаров,"На Ямале не осталось действующих природных пожаров. Однако в целях безопасности действует ограничение на посещение лесов. По данным региональной диспетчерской службы &quot;Леса Ямала&quot;, сегодня, 14 июля, на территории Ямало-Ненецкого автономного округа нет ни одного действующего лесного пожара', 3), \
('Эта новость вообще про бандикутов', 4), \
('Бушует пожар.', 1), \
('Режим пожарной опасности действует в области', 3),\
("Стоит жара", 3), \
('Пожар удалось остановить', 2)]
#('Пожар не удалось локализовать', 1)

    begin = time.time()
    for n in some_news:
        if tell(n[0]) != n[1]: print (n, tell(n[0]))
        print(tell(n), ':', n)
        assert tell(n[0]) == n[1]


    txts, scores = mk_txts()

    ind = 0
    for i, t in enumerate(txts):
        if is_english(' '. join([t.title, t.body])): continue
        try:
            title  = tell(t.title)
            body = tell(t.body)
            predict = title if (body == 4 or title in [2, 1]) else body
        except WrongFire: predict = 4
        cl = scores[i]
        if predict != cl:
            print(predict, cl, t)
            ind +=1
    print(ind)


    import feed
    for n in feed.news:
        process(n)


    duration = time.time() - begin
    dif = '{0} minutes {1} seconds'.format(duration//60, round(duration%60, 2))
    print(dif, duration)

if __name__ == '__main__':
    main()

