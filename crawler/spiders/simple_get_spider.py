import scrapy
import os

from crawler.items import CrawlerItem

class SimpleGetSpider(scrapy.Spider):
	TASK_DIR = 'task/'
	name = "simple_get_spider"

	def start_task(self, task_dir):
		for root, dirs, fns in os.walk(task_dir):
			for fn in fns:
				with open(os.path.join(root, fn)) as seeds:
					for seed in seeds:
						if seed.strip():
							yield scrapy.Request(seed.strip(), 
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