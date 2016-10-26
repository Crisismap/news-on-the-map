# -*- coding: utf-8 -*-
import feedparser
import ssl
import odbc;
import re;
import time;
from sx_storage import sxDBStorage;
from bs4 import BeautifulSoup

print "start"
if hasattr(ssl, '_create_unverified_context'):
	ssl._create_default_https_context = ssl._create_unverified_context
## Add RSS URLs to this dictionary, and specify the label/type for the news that we recieve from that source.
news_sources = dict({
					#землетрясения					
					#'http://earthquake.usgs.gov/earthquakes/feed/atom/2.5/day':'earthquake',
					'https://news.google.com/news/feeds?q=earthquake&output=rss':'earthquake_eng',
					'https://news.google.com/news/feeds?q=%D0%B7%D0%B5%D0%BC%D0%BB%D0%B5%D1%82%D1%80%D1%8F%D1%81%D0%B5%D0%BD%D0%B8%D0%B5&output=rss':'earthquake',
					#пожары
					'http://news.google.com/news?q=%D0%BB%D0%B5%D1%81%D0%BD%D0%BE%D0%B9+%D0%BF%D0%BE%D0%B6%D0%B0%D1%80&output=rss':'fires',
					'https://news.google.com/news/feeds?q=%D1%82%D0%BE%D1%80%D1%84%D1%8F%D0%BD%D0%BE%D0%B9+%D0%BF%D0%BE%D0%B6%D0%B0%D1%80&output=rss':'fires',
					'https://news.google.com/news/section?q=%D0%B8%D0%B7%D0%B2%D0%B5%D1%80%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5+%D0%B2%D1%83%D0%BB%D0%BA%D0%B0%D0%BD&output=rss':'fires',
					'http://aviales.ru/news.rss?lenta=1':'fires',
					'http://news.yandex.ru/fire.rss':'fires',
					'http://www.forestforum.ru/rss.xml':'fires',
					'https://news.google.com/news/feeds?q=wildfire&output=rss':'fires_eng',
					'http://inciweb.nwcg.gov/feeds/rss/articles/':'fires_eng',
					#украина
					'http://news.google.com/news/feeds?q=%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B5%20%D0%B1%D0%B5%D0%B6%D0%B5%D0%BD%D1%86%D1%8B&output=rss':'ukraine',
					'https://news.google.com/news/feeds?q=%D0%B1%D0%BE%D0%B5%D0%B2%D1%8B%D0%B5+%D0%B4%D0%B5%D0%B9%D1%81%D1%82%D0%B2%D0%B8%D1%8F+%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0&output=rss':'ukraine',
					'https://news.google.com/news/feeds?q=%D0%B2%D0%BE%D0%B9%D0%BD%D0%B0+%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0&output=rss':'ukraine',
					'https://news.google.com/news/feeds?q=ukraine+war&output=rss':'ukraine_eng',
					'https://news.yandex.ua/east.rss':'ukraine',
					'http://liveuamap.com/rss':'ukraine_eng',
					#война+сирия
					'https://news.google.com/news/feeds?q=%D0%B2%D0%BE%D0%B9%D0%BD%D0%B0+%D1%81%D0%B8%D1%80%D0%B8%D1%8F&output=rss':'syria',
					'http://syria.liveuamap.com/rss':'syria_eng',
					#авиаудары+игил
					'https://news.google.com/news/feeds?q=%D0%B0%D0%B2%D0%B8%D0%B0%D1%83%D0%B4%D0%B0%D1%80%D1%8B+%D0%B8%D0%B3%D0%B8%D0%BB&output=rss':'syria',
					#'http://feeds.newsru.com/il/www/section/mideast':'syria',
					'https://news.google.com/news/feeds?q=syria+airstikes&output=rss':'syria_eng',
					'https://news.google.com/news/feeds?q=syria+war&output=rss':'syria_eng',
					#беженцы
					'https://news.google.com/news/feeds?q=%D1%81%D0%B8%D1%80%D0%B8%D1%8F+%D0%B1%D0%B5%D0%B6%D0%B5%D0%BD%D1%86%D1%8B':'refugees',
					'https://news.google.com/news/feeds?q=%D0%BB%D0%B0%D0%B3%D0%B5%D1%80%D1%8F+%D0%B1%D0%B5%D0%B6%D0%B5%D0%BD%D1%86%D1%8B':'refugees',
					'https://news.google.com/news/feeds?q=refugees+syria':'refugees_eng',
					#израиль
					'http://feeds.newsru.com/il/www/section/israel':'israel',
					#,'http://static.utro.ua/rss/publications-proisshestviya.ru.rss.xml':'ukraine'
					#,'http://www.forestforum.ru/rss.xml':'fires'
					#наводнения
					'https://news.google.com/news/section?q=%D0%BD%D0%B0%D0%B2%D0%BE%D0%B4%D0%BD%D0%B5%D0%BD%D0%B8%D1%8F&output=rss':'floods',
					'https://news.google.com/news/section?q=flashfloods&output=rss':'floods_eng',
					#окружающая среда
					#'http://checkins.ru/rss-export/?q=%D0%BD%D0%B5%D0%B7%D0%B0%D0%BA%D0%BE%D0%BD%D0%BD%D0%B0%D1%8F+%D1%81%D0%B2%D0%B0%D0%BB%D0%BA%D0%B0':'ecology_vk',
					'https://script.googleusercontent.com/macros/echo?user_content_key=cOTfw1B8fNmNhw5rRAEMR7gny7zBbDDbgmq9yjf256I0SH-XN1ErA662avHEFfzP4fnNVdMWwQcaUS5aaboDGpk0W0xeTvyCOJmA1Yb3SEsKFZqtv3DaNYcMrmhZHmUMWojr9NvTBuBLhyHCd5hHa3djn4kcaeuceAVPTcb_IKOQizEdNNom8Sk6pZs7_CDNMUWiDq7n5DCWZiujjnbT-IrTlwrp2DSWLgANXR6ofjDf5WHNTOrgsuIqrCF7L_yANRKX8R5kuZXt9ZwMYLv7EOTOKNhF1Uj7ryjVFeKdSSI94WSHqvuye14cN6jzX3jWLEHyQ_tWh3iKxlDi_IOksIa7aw92jXDdLi2yFradcP86mDkagt_OdYgJ1ExvHO4uhynZsQjJq04&lib=MkTrT-GFjciLZr9a0QLCCFly6XnJGsUf7':'ecology_twitter',
					'https://script.googleusercontent.com/macros/echo?user_content_key=_Ap0JiMwidCDeY65UpjC1JWwOAgd5NLxSk-hA4znOnVFE2n8EJzMCk1V1jdWVHJ0yUGGoxyrQj1rz3_rs1YbEluVBxrCnZ3wOJmA1Yb3SEsKFZqtv3DaNYcMrmhZHmUMWojr9NvTBuBLhyHCd5hHa3djn4kcaeuceAVPTcb_IKOQizEdNNom8Sk6pZs7_CDNMUWiDq7n5DCWZiujjnbT-IrTlwrp2DSWLgANXR6ofjDf5WHNTOrgsl4cN6jzX3jWwxaiLsu5XEj0MrsVzq54gUMraeaYJFFKVYWgJbE-3N0FHTfcywuwgWLW2Q7xUmErExozreiOTjbuzy6WZJfnFEOFmRhYzyjKWO-YTWkR6gSh8Oj789czJ8GD6mYBOprp&lib=MkTrT-GFjciLZr9a0QLCCFly6XnJGsUf7':'ecology_twitter',
					'https://news.yandex.ru/ecology.rss':'ecology',
					'feeds.reuters.com/reuters/environment':'ecology_eng',
					'https://news.google.com/news/section?q=%D0%B7%D0%B0%D0%B3%D1%80%D1%8F%D0%B7%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5+%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%85%D0%B0&output=rss':'ecology',
					'https://news.google.com/news/section?q=%D0%BD%D0%B5%D0%B7%D0%B0%D0%BA%D0%BE%D0%BD%D0%BD%D0%B0%D1%8F+%D1%81%D0%B2%D0%B0%D0%BB%D0%BA%D0%B0&output=rss':'ecology',
					'https://script.googleusercontent.com/macros/echo?user_content_key=m6tk5dBDTsx5CUYHpHzKjS-GG4sZTTqmlYpLs174ECmpZi8gyB70GF_GmKO6AT0ASwbHiJOhTH8Q47_CNmtGHt5jWKjJF5H7OJmA1Yb3SEsKFZqtv3DaNYcMrmhZHmUMWojr9NvTBuBLhyHCd5hHa3djn4kcaeuceAVPTcb_IKOQizEdNNom8Sk6pZs7_CDNMUWiDq7n5DCWZiujjnbT-IrTlwrp2DSWLgANXR6ofjDf5WHNTOrgsudrZcxZzA24N6hwApyDVcMAPWBcdI_E2UMraeaYJFFKNiV4qZl1oW8CU6cvb-wj4e0BQ2CJeOqTEMNlqVLIbS8G8d9eiTjLOMGD6mYBOprp&lib=MkTrT-GFjciLZr9a0QLCCFly6XnJGsUf7':'ecology_twitter'
					#'https://news.yandex.ru/incident.rss':'accidents'
					#'https://news.google.com/news/feeds?q=%D0%B4%D0%BE%D0%BD%D0%BE%D1%80%D1%81%D0%BA%D0%B0%D1%8F+%D0%BA%D1%80%D0%BE%D0%B2%D1%8C&output=rss':'blood'
					#'https://news.google.com/news/feeds?q=%D0%BF%D1%80%D0%BE%D1%82%D0%B5%D1%81%D1%82%D1%8B+%D0%B4%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B1%D0%BE%D0%B9%D1%89%D0%B8%D0%BA%D0%B8&output=rss':'antiplaton',
					#'https://news.google.com/news/feeds?q=%D0%BF%D0%BB%D0%B0%D1%82%D0%BE%D0%BD+%D0%B4%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B1%D0%BE%D0%B9%D1%89%D0%B8%D0%BA%D0%B8&output=rss':'antiplaton',
					#'https://news.google.com/news/feeds?q=%D0%B0%D0%BD%D1%82%D0%B8%D0%BF%D0%BB%D0%B0%D1%82%D0%BE%D0%BD&output=rss':'antiplaton',
					#'https://script.googleusercontent.com/macros/echo?user_content_key=TZsyA5Fq2q6HGLuDWq23ixHb8GfsSZj1_JsqVpggKTsVY7Cuzu-12LGxQfuqCj3KFI2QQt-XcV8Zm62l0aqJS1a1OoCyjxEXm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnNrJjcn5tMnJozsIHLgb4WDmzEc3V7pY_qbmxUTSbtzxx0nSp4K8Rg-TeO0TF_iSt4Tt-flz1lUkWh6nmMXDfIYlXmOAssj6TcGD6mYBOprp&lib=Msp86L4y290o5xM5axajKI1y6XnJGsUf7':'antiplaton_tw'
					#'https://news.google.com/news/feeds?q=%D0%B2%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%BB%D0%B0%D0%B3%D0%B5%D1%80%D1%8F%20%D0%B1%D0%B5%D0%B6%D0%B5%D0%BD%D1%86%D0%B5%D0%B2&output=rss':'ukraine'
					#'http://blogs.yandex.ru/search.rss?text=%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B5+%D0%B1%D0%B5%D0%B6%D0%B5%D0%BD%D1%86%D1%8B':'ukraine'
					#,'http://news.google.com/news?gl=us&pz=1&ned=us&hl=en&q=%D0%B7%D0%B5%D0%BC%D0%BB%D0%B5%D1%82%D1%80%D1%8F%D1%81%D0%B5%D0%BD%D0%B8%D0%B5&output=rss':'earthquakes'
					#,'http://news.google.com/news?hl=en&gl=us&q=%D0%BD%D0%B0%D0%B2%D0%BE%D0%B4%D0%BD%D0%B5%D0%BD%D0%B8%D1%8F&um=1&ie=UTF-8&output=rss':'floods'
					});

def custom_strip_tags(value):
	soup = BeautifulSoup(value);
	allFontTags = soup.find_all("font",{"size":"-1"});
	if(len(allFontTags) > 0):
		content = soup.find_all("font",{"size":"-1"})[1];
	else:
		content = value;	
	result = re.sub(r'<[^>]*?>', ' ', unicode(content))
	
	return unicode(result)

#try:
dbsx = sxDBStorage();

dbsx.ConnectMaps();
print "connect"
for url in news_sources.keys():
	#if news_sources[url] != "fires_eng":
	#	continue
	try:
		fires_lenta = feedparser.parse(url);
		
		conn = odbc.odbc("Driver={SQL Server Native Client 10.0};Server=___;Failover_PartnerPartner=___;Database=___;Uid=___;Pwd=___");
		cur = conn.cursor();
		
		for entry in fires_lenta.entries:
			str_date = time.strftime('%d/%m/%Y %H:%M:%S',entry.updated_parsed);
			print str_date
			type = news_sources[url];
			
			if hasattr(entry,'georss_point'):
				coords = entry.georss_point.split(' ');
				entry.geo_long = coords[0];
				entry.geo_lat = coords[1];
				print "1"
			if hasattr(entry,'geo_long'):
				print "2"
				sqlCmd = "IF (SELECT COUNT(*) FROM NewsRSS WHERE guid = '"+entry.guid+ "') = 0 INSERT INTO NewsRSS Values ('"+entry.guid+"','"+entry.title.replace("'", "''")+"','"+entry.link+"','"+custom_strip_tags(entry.description).replace("'", "''")+"','"+str_date+"','"+type+"',1,'',NULL,NULL)";
				cur.execute(sqlCmd);
				
				article = dbsx.GetLatestNewsArticle();
				
				dbsx.StoreArticleLocations(article,[(entry.geo_long, entry.geo_lat)],'');
			else:
				#print "3"
				if not hasattr(entry, 'guid'):
					entry.guid = entry.link
				print entry.guid
				#print entry.title
				#print entry.link
				#print entry.description.encode('ascii', 'ignore')
				sqlCmd = "IF (SELECT COUNT(*) FROM NewsRSS WHERE guid = '"+entry.guid+ "') = 0 INSERT INTO NewsRSS Values ('"+entry.guid+"','"+entry.title.replace("'", "''")+"','"+entry.link+"','"+custom_strip_tags(entry.description).replace("'", "''")+"','"+str_date+"','"+type+"',0,'',NULL,NULL)";
				#print sqlCmd.encode('ascii', 'ignore');
				cur.execute(sqlCmd);	
			#print sqlCmd;
			#cur.execute(sqlCmd);
			dbsx.Close();
	except Exception, e:
		print "Error processing RSS Feed: ", str(e);

#except:
#	print "Error processing RSS Feed.";
