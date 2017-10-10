# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import scrapy

import dns.resolver
from urllib import parse
import threading

class DnsOnlyMiddleware(object):
	# Perform dns only, no further http connections

	DNS_SERVER_FILE = 'dns_server'
	INTERESTED_TYPE_STR = '/dns'
	dns_servers = []

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=scrapy.signals.spider_opened)
		return s

	def extract_domain(self, url):
		return parse.urlparse(url).netloc

	def resolve_dns(self, domain, ns, result):
		resolver = dns.resolver.Resolver(configure=False)
		try:
			resolver.nameservers = []
			resolver.nameservers.append(ns)
			answer = resolver.query(domain, 'A')
			for addr in answer.rrset.items:
				result.add(addr)
		except:
			pass

	def process_request(self, request, spider):
		if self.INTERESTED_TYPE_STR in request.meta[spider.TASK_TYPE]:
			# Do dns request instead
			result = set()
			workers = []
			domain = self.extract_domain(request.url)
			for server in self.dns_servers:
				t = threading.Thread(target=self.resolve_dns, args=(domain,server,result))
				t.setDaemon(True)
				workers.append(t)
				t.start()
			for t in workers:
				t.join()
			request.meta[spider.DOMAIN_IP_LIST] = result
			spider.logger.info('{}: got {} IPs.'.format(domain, len(result)))
			return scrapy.http.Response(domain, status=200, request=request)

	def spider_opened(self, spider):
		with open(self.DNS_SERVER_FILE) as f:
			self.dns_servers = [line.strip() for line in f if line.strip()]
		spider.logger.info('DnsOnlyMiddleware loaded {} dns servers.'.format(len(self.dns_servers)))
