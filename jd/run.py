from scrapy import cmdline

id = '4510588'
cmd = 'scrapy crawl jd -a product_id={0} -a url=https://item.jd.com/{0}.html'.format(id)
cmdline.execute(cmd.split())
