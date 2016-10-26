from collections import namedtuple, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial import distance
from sx_storage import sxDBStorage
import datetime as dt

Pair = namedtuple("Pair", ['center', 'distance'])

def init_cluster(ds, min_dist = 0.5):
	num_of_news = ds.shape[0]
	d = defaultdict(set)
	for i in range(0, num_of_news):
		for j in range(i+1, num_of_news):
			if i!=j:
				distance = ds[i, j]
				if distance < min_dist:
						d[i].add(Pair(j, distance))
						d[j].add(Pair(i, distance))
	return d


def clusterize(items2neighbours, ds):
	item2all = defaultdict(set)
	for elem, pairs in items2neighbours.items():
		neighbours = [el.center for el in pairs] + [elem]
		neighbours_of_neighbours = [neighbour_of_neighbour.center for neighbour in neighbours for neighbour_of_neighbour in items2neighbours[neighbour]]
		#new_arrived = set(neighbours_of_neighbours) - set(neighbours)
		#if new_arrived:
			#print (elem, new_arrived, neighbours)
		item2all[elem] = frozenset(set(neighbours) | set(neighbours_of_neighbours))
	clusters = set(item2all.values())
	cluster2center = {}
	for cluster in clusters:
		if len(cluster)>2:
			best = None
			for elem in cluster:
				sum_of_distances = sum(ds[elem, j] for j in cluster)
				if best is None or sum_of_distances< best[1]:
					best = (elem, sum_of_distances)
			cluster2center[cluster] = best[0]
		else: cluster2center[cluster] = min(cluster)
	item2center = {}
	for k, v in cluster2center.items():
		for elem in k:
			item2center[elem] = v
	for i in range(ds.shape[0]):
		item2center[i] = item2center.setdefault(i, None)
	return item2center

def clusterizer(iterable, key1 = "Title", key2= "Description"):
	vect = TfidfVectorizer()
	X = np.array([ " ".join([elem[key1] + elem[key2]]) for elem in iterable])
	t = vect.fit_transform(X)
	ds = distance.squareform(distance.pdist(t.toarray()))
	items2neighbours = init_cluster(ds, 1.2)
	clusters = clusterize(items2neighbours, ds)
	return clusters

if __name__ == '__main__':
	db = sxDBStorage()
	db.ConnectMaps()
	date_start = dt.datetime.utcnow() + dt.timedelta(hours=-24)
	data = db.LoadLastNews(date_start.strftime("%Y-%m-%d %H:%M:%S"))
	count = len(data)
	clustered_data = clusterizer(data, "title", "body")
	clusters = []
	for i in range(0, count):
		if clustered_data[i] == None: clusters.append((str(data[i]["id"]), str("NULL"))) #print data[i]["id"], "NULL"
		else: clusters.append((str(data[i]["id"]), str(data[clustered_data[i]]["id"])))#print data[i]["id"], data[clustered_data[i]]["id"]
	#print clusters
	sql = db.UpdateNewsClusters(clusters)
	print sql, count
