# -*- coding: utf-8 -*-
import odbc
import os

class sxDBStorage(object):
	def ConnectFires(self):	
		self.db = odbc.odbc("Driver={SQL Server Native Client 10.0};Server=___;Database=___;Uid=___;Pwd=___");
	def ConnectMaps(self):
		self.db = odbc.odbc("Driver={SQL Server Native Client 10.0};Server=___;Failover_Partner=___;Database=___;Uid=___;Pwd=___");
	def Close(self):
		self.db.close();
	
	def LoadNewsLocationsFromDB(self):
		cur = self.db.cursor();
		cur.execute("SELECT id,guid,debug_output FROM NewsRSS");
		news = cur.fetchall();
		cur.close();
		
		allArticles = []; 
		for article in news:
			allArticles.append({"rss_id" : article[0],"guid":article[1],"debug_output":article[2]});	
		return allArticles
    
	def GetLatestNewsArticle(self):
		cur = self.db.cursor();
		cur.execute("SELECT TOP 1 id,pubDate,guid,title,type,link,description FROM NewsRSS ORDER BY id DESC");
		news = cur.fetchall();
		cur.close();
		
		allArticles = []; 
		for article in news:
			allArticles.append({"id" : article[0],"pubDate":article[1],"guid":article[2],"title":article[3],"type":article[4],"link":article[5],"description":article[6]});	
		return allArticles[0]

	def LoadUnclassifiedNews(self, type):
		cur = self.db.cursor();
		cur.execute("SELECT /*TOP 50*/ news_location_id,Title,Description FROM NewsLocations where class is null and type = '" + type + "'");
		news = cur.fetchall();
		cur.close();
		allArticles = [];
		for article in news:
			allArticles.append({"id" : article[0],"title":article[1],"body":article[2]});	
		return allArticles;

	def UpdateNewsClass(self, id, newsClass):
		cur = self.db.cursor();
		cur.execute("UPDATE NewsLocations SET [class] = " + str(newsClass) + " WHERE news_location_id = " + str(id));
		cur.close();

	def LoadUnclassifiedFireNews(self):
		cur = self.db.cursor();
		cur.execute("SELECT id,Title,Description FROM FireNewsLocations where class is null");
		news = cur.fetchall();
		cur.close();
		allArticles = [];
		for article in news:
			allArticles.append({"id" : article[0],"title":article[1],"body":article[2]});	
		return allArticles;
		
	def UpdateFireNewsClass(self, id, fireClass):
		cur = self.db.cursor();
		sql = "UPDATE FireNewsLocations SET [class] = " + str(fireClass) + " WHERE id = " + str(id)
		#print(sql)
		cur.execute(sql);
		cur.close();
		
		
	def LoadUnlocalizedNewsFromDB(self):
		cur = self.db.cursor();
		cur.execute("SELECT /*TOP 1*/ id,pubDate,guid,title,type,link,description FROM NewsRSS WHERE isLocalized = 0 ORDER BY id DESC");
		news = cur.fetchall();
		cur.close();
		
		allArticles = []; 
		for article in news:
			#print article#[0]
			#print article[2].encode('cp1251', 'ignore')
			#return []
			allArticles.append({"id" : article[0],"pubDate":article[1],"guid":article[2],"title":article[3],"type":article[4],"link":article[5],"description":article[6]});	
		return allArticles

	def LoadLastNews(self, since_date):
		cur = self.db.cursor();
		#cur.execute("SELECT news_location_id,Title,Description FROM NewsLocations where pub_date > convert(datetime, '" + since_date + "', 20) ORDER BY news_location_id DESC")
		cur.execute("SELECT news_location_id,Title,Description FROM NewsLocations where pub_date > convert(datetime, '" + since_date + "', 20)")
		news = cur.fetchall()
		cur.close()
		allArticles = []
		for article in news:
			allArticles.append({"id" : article[0],"title":article[1],"body":article[2]})
		return allArticles

	def UpdateNewsClusters(self, data):
		cur = self.db.cursor()
		#chucks = 0
		chunk_size = 0
		sql = "DECLARE @clusters AS TABLE([num] INT, [id] INT, [c_id] INT);" + os.linesep
		i = 0
		for row in data:
			if (chunk_size == 0):
				sql += "INSERT INTO @clusters([num], [id], [c_id]) VALUES" + os.linesep
			elif (chunk_size > 0):
				sql += ","
			sql += "(" + str(i) + "," + str(row[0]) + "," + str(row[1]) + ")"
			chunk_size += 1
			i += 1
			if (chunk_size == 1000):
				chunk_size = 0
				sql += ";" + os.linesep
			#print sql
		sql += ";" + os.linesep
		sql += "UPDATE dest SET [cluster_id] = src.[c_id] FROM [dbo].[NewsLocations] dest INNER JOIN @clusters src ON dest.[news_location_id] = src.[id]"
		#sql += "MERGE [dbo].[NewsLocations] AS dest  USING (SELECT [id], [c_id] FROM @clusters) AS src ON (dest.[news_location_id] = src.[id])" + os.linesep
		#sql += "WHEN MATCHED THEN UPDATE SET [cluster_id] = src.[c_id]" + os.linesep
		#sql += "WHEN NOT MATCHED BY TARGET THEN INSERT"
		return sql

	def StoreArticleLocationssxTest(self,article,locations,debugOutput,allPhrases):
		for coords in locations:
			cur = self.db.cursor();
			sqlCommand = u"INSERT INTO NewsLocationssxTest (rss_id,URL,Title,Description,guid,lat,long,pub_date,type,phrases) VALUES ("+str(article["id"])+",'"+article["link"]+"','"+article["title"].replace("'", "''")+"','"+article["description"].replace("'", "''")+"','"+article["guid"]+"',"+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["type"]+"','"+allPhrases.replace("'", "''")+"')";
			cur.execute(sqlCommand);
			cur.close();

	def StoreArticleLocations(self,article,locations,debugOutput,allPhrases):
		cur = self.db.cursor();
		sqlCommand = u"UPDATE NewsRSS SET isLocalized = 1,debug_output = '" + debugOutput + "',phrases='" + allPhrases.replace("'", "''") + "' WHERE guid = '"+article["guid"] + "'"
		#print sqlCommand.encode('ascii', 'ignore');
		cur.execute(sqlCommand);
		cur.close();
		
		for coords in locations:
			cur = self.db.cursor();
			sqlCommand = u"INSERT INTO NewsLocations (rss_id,URL,Title,Description,guid,lat,long,pub_date,type,phrases) VALUES ("+str(article["id"])+",'"+article["link"]+"','"+article["title"].replace("'", "''")+"','"+article["description"].replace("'", "''")+"','"+article["guid"]+"',"+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["type"]+"','"+allPhrases.replace("'", "''")+"')";
			#print sqlCommand.encode('ascii', 'ignore');
			cur.execute(sqlCommand);
			cur.close();
			
			#cur = self.db.cursor();
			#cur.execute("SELECT news_location_id FROM NewsLocations WHERE guid = '"+article["guid"] + "' AND lat = '" + coords[1] + "' AND long = '" + coords[0] +"'");
			#newLocationId = cur.fetchall()[0][0];
			#print newLocationId;
			#cur.close();
			
			
			#sqlCommand = "INSERT INTO NewsLayer (news_location_id,lat,long,pub_date,title,URL) VALUES ("+str(newLocationId)+","+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["title"]+"','"+article["link"]+"')";
			#print sqlCommand
			#cur = self.db.cursor();
			#cur.execute(sqlCommand);
			#cur.close();
			
if __name__ == '__main__':
  db = sxDBStorage()
  db.ConnectMaps()
  print db.LoadLastNews('2016-08-05')