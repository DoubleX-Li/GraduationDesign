# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    type = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    good_rate_show = scrapy.Field()
    poor_rate_show = scrapy.Field()
    average_score = scrapy.Field()
    good_count = scrapy.Field()
    general_rate = scrapy.Field()
    general_count = scrapy.Field()
    poor_rate = scrapy.Field()
    after_count = scrapy.Field()
    good_rate_style = scrapy.Field()
    poor_count = scrapy.Field()
    poor_rate_style = scrapy.Field()
    general_rate_style = scrapy.Field()
    comment_count = scrapy.Field()
    product_id = scrapy.Field()
    good_rate = scrapy.Field()
    general_rate_show = scrapy.Field()
    url = scrapy.Field()
    item_ids = scrapy.Field()
    save_time = scrapy.Field()

class JdComment(scrapy.Item):
    type = scrapy.Field()
    id = scrapy.Field()
    item_id = scrapy.Field()
    content = scrapy.Field()
    creation_time = scrapy.Field()
    reply_count = scrapy.Field()
    score = scrapy.Field()
    useful_vote_count = scrapy.Field()
    useless_vote_count = scrapy.Field()
    user_level_id = scrapy.Field()
    user_province = scrapy.Field()
    nickname = scrapy.Field()
    product_color = scrapy.Field()
    product_size = scrapy.Field()
    user_level_name = scrapy.Field()
    user_client = scrapy.Field()
    user_client_show = scrapy.Field()
    is_mobile = scrapy.Field()
    days = scrapy.Field()
    reference_time = scrapy.Field()
    after_days = scrapy.Field()
    images_count = scrapy.Field()
    ip = scrapy.Field()
    after_content = scrapy.Field()
    save_time = scrapy.Field()
