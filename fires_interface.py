import fire_classifier
import min_cl

def main():
    from sx_storage import sxDBStorage;
    dbsx = sxDBStorage();
    dbsx.ConnectMaps();
    fireNews = dbsx.LoadUnclassifiedFireNews();
    #print(fireNews)
    model = min_cl.learn()
    for fn in fireNews:
        predict = min_cl.predict((fn["title"], fn["body"]), model)[0]
        print predict
        #news = fire_classifier.News(fn["title"], fn["body"])
        #predict = fire_classifier.classify_tuple(news)
        #print predict		
        dbsx.UpdateFireNewsClass(fn["id"], predict)

if __name__ == '__main__':
    main()
