import datetime
import json
import re
import time
import random

import chardet
from scrapy import Spider, Request
from scrapy.http.cookies import CookieJar
from scrapy.utils.project import get_project_settings

from jd.items import JdItem, JdComment


class JDSpider(Spider):
    name = 'jd'

    def __init__(self, name=None, **kwargs):
        super(JDSpider, self).__init__(name, **kwargs)
        self.url = kwargs.get('url')
        self.guid = kwargs.get('guid', 'guid')
        pattern = re.compile('\d+', re.S)
        self.product_id = re.search(pattern, self.url).group()
        self.log('product_id: %s' % self.product_id)
        self.item_table = 'item_%s' % self.product_id

        # self.log_dir = 'log'
        self.is_record_page = False
        # self.sql = kwargs.get('sql')
        # print('find sql')
        # print(self.sql)

    def start_requests(self):
        yield Request(
            url=self.url,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch, br',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                # 'Connection': 'keep-alive',
                'Host': 'item.jd.com',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            },
            method='GET',
            meta={
                'dont_merge_cookies': True,
                'cookiejar': CookieJar(),
            },
            dont_filter=True,
            callback=self.get_comment_count
        )

    def get_comment_count(self, response):
        # self.save_page('%s.html' % self.product_id, response.body)

        name = response.xpath('//head/title/text()').extract_first()
        self.log('name:%s' % name)

        # utils.push_redis(self.guid, self.product_id,
        #                  '商品名称：%s 链接：<a href="%s" target="_blank">%s' % (name, self.url, self.url))

        ids = response.xpath('//div[@class="dd"]/div/@data-sku').extract()
        item_ids = ','.join(ids)
        self.log('item_ids:%s' % item_ids)

        pattern = re.compile('commentVersion:\'(\d+)\'', re.S)
        comment_version = re.search(pattern, response.body.decode('gbk', 'ignore')).group(1)

        # sort type 5:推荐排序 6:时间排序
        url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv' \
              '{comment_version}&productId={product_id}&score=0&sortType={sort_type}&page=0&pageSize=10' \
              '&isShadowSku=0'. \
            format(product_id=self.product_id, comment_version=comment_version, sort_type='6')

        yield Request(
            url=url,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch, br',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Connection': 'keep-alive',
                'Host': 'club.jd.com',
                'Referer': 'https://item.jd.com/{0}.html'.format(self.product_id),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            },
            method='GET',
            meta={
                'name': name,
                'comment_version': comment_version,
                'item_ids': item_ids,
            },
            dont_filter=True,
            callback=self.get_all_comment
        )

    def get_all_comment(self, response):
        # self.save_page('%s_all_comment.html' % self.product_id, response.body)

        # detect = chardet.detect(response.body)
        # encoding = detect.get('encoding', '')
        body = response.body.decode('gb2312', 'ignore')
        pattern = re.compile('\((.*?)\);', re.S)
        item = re.search(pattern, body)
        if item != None and item.group(1) != None:
            data = json.loads(item.group(1))

            pcs = data.get('productCommentSummary')
            new_jd_item = JdItem()
            new_jd_item['type'] = 'item'
            new_jd_item['id'] = self.product_id
            new_jd_item['name'] = response.meta.get('name')
            new_jd_item['good_rate_show'] = pcs.get('goodRateShow')
            new_jd_item['poor_rate_show'] = pcs.get('poorRateShow')
            new_jd_item['average_score'] = pcs.get('averageScore')
            new_jd_item['good_count'] = pcs.get('goodCount')
            new_jd_item['general_rate'] = pcs.get('generalRate')
            new_jd_item['general_count'] = pcs.get('generalCount')
            new_jd_item['poor_rate'] = pcs.get('poorRate')
            new_jd_item['after_count'] = pcs.get('afterCount')
            new_jd_item['good_rate_style'] = pcs.get('goodRateStyle')
            new_jd_item['poor_count'] = pcs.get('poorCount')
            new_jd_item['poor_rate_style'] = pcs.get('poorRateStyle')
            new_jd_item['general_rate_style'] = pcs.get('generalRateStyle')
            new_jd_item['comment_count'] = pcs.get('commentCount')
            new_jd_item['product_id'] = pcs.get('productId')
            new_jd_item['good_rate'] = pcs.get('goodRate')
            new_jd_item['general_rate_show'] = pcs.get('generalRateShow')
            new_jd_item['url'] = self.url
            new_jd_item['item_ids'] = response.meta.get('item_ids')
            new_jd_item['save_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            yield new_jd_item
            # self.product_msg = {
            #     'id': self.product_id,
            #     'name': response.meta.get('name'),
            #     'good_rate_show': pcs.get('goodRateShow'),
            #     'poor_rate_show': pcs.get('poorRateShow'),
            #     'average_score': pcs.get('averageScore'),
            #     'good_count': pcs.get('goodCount'),
            #     'general_rate': pcs.get('generalRate'),
            #     'general_count': pcs.get('generalCount'),
            #     'poor_rate': pcs.get('poorRate'),
            #     'after_count': pcs.get('afterCount'),
            #     'good_rate_style': pcs.get('goodRateStyle'),
            #     'poor_count': pcs.get('poorCount'),
            #     'poor_rate_style': pcs.get('poorRateStyle'),
            #     'general_rate_style': pcs.get('generalRateStyle'),
            #     'comment_count': pcs.get('commentCount'),
            #     'product_id': pcs.get('productId'),
            #     'good_rate': pcs.get('goodRate'),
            #     'general_rate_show': pcs.get('generalRateShow'),
            #     'url': self.url,
            #     'item_ids': response.meta.get('item_ids'),
            #     'save_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # }

            # info = '京东商城显示的评价信息，<strong style="color: red; font-size: 24px;">总的评价数:{comment_count}、好评数:{good_count}、' \
            #        '好评百分比:{good_rate}%、中评数:{general_count}、中评百分比:{general_rate}%、差评数:{poor_count}、差评百分比:{poor_rate}% ' \
            #        '</strong>' \
            #     .format(comment_count=pcs.get('commentCount'), good_count=pcs.get('goodCount'),
            #             general_count=pcs.get('generalCount'), poor_count=pcs.get('poorCount'),
            #             good_rate=pcs.get('goodRate', 0) * 100,
            #             general_rate=pcs.get('generalRate', 0) * 100,
            #             poor_rate=pcs.get('poorRate', 0) * 100)

            # utils.push_redis(self.guid, self.product_id, info)
            # 显示正在加载图片
            # utils.push_redis(self.guid, self.product_id,
            #                  '<li id="loader"><img src="/static/loader.gif"  height="90" width="90"></li>',
            #                  type='image', save_to_mysql=False)

            comment_version = response.meta.get('comment_version')
            comment_count = pcs.get('commentCount')
            page_count = int(int(comment_count) / 10)

            inner_crawl_page = get_project_settings().get('INNER_CRAWL_PAGE', 20)
            # if page_count > inner_crawl_page and False: #config.is_distributed:
            #     for i in range(inner_crawl_page, page_count):
            #         # 将数据插入 redis ，实现分布式抓取
            #         data = {
            #             'prodyct_id': self.product_id,
            #             'comment_version': comment_version,
            #             'sort_type': '6',
            #             'page': i
            #         }
            # self.red.rpush(self.product_id, json.dumps(data))

            # count = self.red.llen('spiders')
            # self.red.set('%s_page' % self.product_id, page_count - inner_crawl_page)
            # for i in range(count):
            #     guid = self.red.lindex('spiders', i)
            #     self.red.rpush(guid, self.product_id)

            # 正常抓取
            count = min(page_count, 100)
            # count = page_count
            for i in range(count):
                # if i % 1000 == 0 and i != 0:
                #     time.sleep(60)
                # elif i % 200 == 0 and i != 0:
                #     time.sleep(10)
                # elif i % 20 == 0:
                #     time.sleep(random.randint(2,3))
                # sort type 5:推荐排序 6:时间排序
                url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv' \
                      '{comment_version}&productId={product_id}&score=0&sortType={sort_type}&page={page}&' \
                      'pageSize=10&isShadowSku=0'. \
                    format(product_id=self.product_id, comment_version=comment_version, sort_type='6',
                           page=i)

                yield Request(
                    url=url,
                    headers={
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Host': 'club.jd.com',
                        'Referer': 'https://item.jd.com/{0}.html'.format(self.product_id),
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 '
                                      'Firefox/52.0',
                    },
                    method='GET',
                    meta={
                        'page': i,
                        'name': response.meta.get('name')
                    },
                    dont_filter=True,
                    callback=self.parse_comment
                )

    def parse_comment(self, response):
        # self.save_page('%s_%s.html' % (self.product_id, response.meta.get('page')), response.body)

        # detect = chardet.detect(response.body)
        # encoding = detect.get('encoding', '')
        body = response.body.decode('gb2312', 'ignore')

        pattern = re.compile('\((.*?)\);', re.S)
        item = re.search(pattern, body)
        if item != None and item.group(1) != None:
            data = json.loads(item.group(1))
            comments = data.get('comments', [])
            for comment in comments:

                id = comment.get('id')  # 评论的 id
                content = comment.get('content')  # 评论的内容
                creation_time = comment.get('creationTime', '')  # 评论创建的时间
                reply_count = comment.get('replyCount', '')  # 回复数量
                score = comment.get('score', '')  # 评星
                useful_vote_count = comment.get('usefulVoteCount', '')  # 其他用户觉得有用的数量
                useless_vote_count = comment.get('uselessVoteCount', '')  # 其他用户觉得无用的数量
                user_level_id = comment.get('userLevelId', '')  # 评论用户等级的 id
                user_province = comment.get('userProvince', '')  # 用户的省份
                nickname = comment.get('nickname', '')  # 评论用户的昵称
                product_color = comment.get('productColor', '')  # 商品的颜色
                product_size = comment.get('productSize', '')  # 商品的大小
                user_level_name = comment.get('userLevelName', '')  # 评论用户的等级
                user_client = comment.get('userClient', '')  # 用户评价平台
                user_client_show = comment.get('userClientShow', '')  # 用户评价平台
                is_mobile = comment.get('isMobile', '')  # 是否是在移动端完成的评价
                days = comment.get('days', '')  # 购买后评论的天数
                reference_time = comment.get('referenceTime', '')  # 购买的时间
                after_days = comment.get('afterDays', '')  # 购买后再次评论的天数
                images_count = len(comment.get('images', []))  # 评论总图片的数量
                after_user_comment = comment.get('afterUserComment', '')
                if after_user_comment != '' and after_user_comment != None:
                    ip = after_user_comment.get('ip', '')  # 再次评论的 ip 地址

                    h_after_user_comment = after_user_comment.get('hAfterUserComment', '')
                    after_content = h_after_user_comment.get('content', '')  # 再次评论的内容
                else:
                    ip = ''
                    after_content = ''

                content = content.replace('\'', '')
                after_content = after_content.replace('\'', '')

                new_comment = JdComment()
                new_comment['type'] = 'comment'
                new_comment['id'] = id
                new_comment['item_id'] = self.product_id
                new_comment['content'] = content
                new_comment['creation_time'] = creation_time
                new_comment['reply_count'] = reply_count
                new_comment['score'] = score
                new_comment['useful_vote_count'] = useful_vote_count
                new_comment['useless_vote_count'] = useless_vote_count
                new_comment['user_level_id'] = user_level_id
                new_comment['user_province'] = user_province
                new_comment['nickname'] = nickname
                new_comment['product_color'] = product_color
                new_comment['product_size'] = product_size
                new_comment['user_level_name'] = user_level_name
                new_comment['user_client'] = user_client
                new_comment['user_client_show'] = user_client_show
                new_comment['is_mobile'] = is_mobile
                new_comment['days'] = days
                new_comment['reference_time'] = reference_time
                new_comment['after_days'] = after_days
                new_comment['images_count'] = images_count
                new_comment['ip'] = ip
                new_comment['after_content'] = after_content
                new_comment['save_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                yield new_comment

                # msg = {
                #     'id': id,
                #     'content': content,
                #     'creation_time': creation_time,
                #     'reply_count': reply_count,
                #     'score': score,
                #     'useful_vote_count': useful_vote_count,
                #     'useless_vote_count': useless_vote_count,
                #     'user_level_id': user_level_id,
                #     'user_province': user_province,
                #     'nickname': nickname,
                #     'product_color': product_color,
                #     'product_size': product_size,
                #     'user_level_name': user_level_name,
                #     'user_client': user_client,
                #     'user_client_show': user_client_show,
                #     'is_mobile': is_mobile,
                #     'days': days,
                #     'reference_time': reference_time,
                #     'after_days': after_days,
                #     'images_count': images_count,
                #     'ip': ip,
                #     'after_content': after_content,
                #     'save_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # }
                # print(msg)
                # self.sql.insert_json(msg, self.item_table)

                # def save_page(self, filename, data):
                #     if self.is_record_page:
                #         with open('%s/%s' % (self.log_dir, filename), 'w') as f:
                #             f.write(data)
                #             f.close()

                # def close(spider, reason):
                #     if spider.product_msg != None:
                #         spider.sql.insert_json(spider.product_msg, 'item')  # TODO config.jd_item_table)
                #
                #     # # 如果是分布式抓取 清理 redis
                #     # if config.is_distributed:
                #     #     utils.red.delete('%s_page' % spider.product_id)
                #     #     utils.red.delete(spider.product_id)
                #     #     spider.log('clear redis product_id:%s' % spider.product_id)
                #     #
                #     #     # 等其他抓取进程一下
                #     #     time.sleep(5)
                #
                #     command = "SELECT COUNT(*) FROM {}".format('item_%s' % spider.product_id)
                #     spider.sql.execute(command, commit=False)
                #     (count,) = spider.sql.cursor.fetchone()
                #
                #     command = "SELECT COUNT(*) FROM {} WHERE score=5".format('item_%s' % spider.product_id)
                #     spider.sql.execute(command, commit=False)
                #     (good_count,) = spider.sql.cursor.fetchone()
                #
                #     command = "SELECT COUNT(*) FROM {} WHERE score>=3 and score <=4".format('item_%s' % spider.product_id)
                #     spider.sql.execute(command, commit=False)
                #     (general_count,) = spider.sql.cursor.fetchone()
                #
                #     command = "SELECT COUNT(*) FROM {} WHERE score<=2".format('item_%s' % spider.product_id)
                #     spider.sql.execute(command, commit=False)
                #     (poor_count,) = spider.sql.cursor.fetchone()
                #
                #     # utils.push_redis(spider.guid, spider.product_id,
                #     #                  info='抓取信息完成，实际抓取评价信息，<strong style="color: red; font-size: 24px;">总共抓取评价数:%s、好评数:%s、'
                #     #                       '中评数:%s、差评数:%s</strong>' % (count, good_count, general_count, poor_count))
                #     info = '抓取信息完成，实际抓取评价信息，总共抓取评价数:%s、好评数:%s、中评数:%s、差评数:%s' % (
                #         count, good_count, general_count, poor_count)
                #     print(info)
                #     # 事务提交数据
                #     spider.sql.commit()
