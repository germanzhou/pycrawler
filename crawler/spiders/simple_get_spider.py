import scrapy
import os
import time

from crawler.items import CrawlerItem

class SimpleGetSpider(scrapy.Spider):
	timestamp = time.time()
	global_output = 'report{}.txt'.format(timestamp)
	
	TASK_DIR = 'task/'
	# meta keys
	TASK_TYPE = 'task_type'
	DOMAIN_IP_LIST = 'domain_ip_list'

	name = "simple_get_spider"

	def force_add_schema(self, url):
		if not (url.startswith('http://') or url.startswith('https://')):
			return 'http://' + url
		return url

	def start_task(self, task_dir):
		for root, dirs, fns in os.walk(task_dir):
			for fn in fns:
				with open(os.path.join(root, fn)) as seeds:
					for seed in seeds:
						if seed.strip():
							yield scrapy.Request(self.force_add_schema(seed.strip()), 
								meta={'task_type': root},
								callback=self.parse)
			for d in dirs:
				self.start_task(d)

	def start_requests(self):
		return self.start_task(self.TASK_DIR)
							
	def parse(self, response):
		item = CrawlerItem()
		item['raw_url'] = response.url
		item['raw_rsp'] = response
		yield item