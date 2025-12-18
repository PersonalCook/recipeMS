import os
from elasticsearch import AsyncElasticsearch

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
client = AsyncElasticsearch(hosts=[ES_HOST])
