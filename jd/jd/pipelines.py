# -*- coding: utf-8 -*-

from jd import session
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from jd.models import JdItem, JdComment


class JdPipeline(object):
    def process_item(self, item, spider):
        if 'item' == item.get('type'):
            temp = session.query(JdItem).filter(JdItem.id==item.get('id')).first()
            if temp:
                # print(temp)
                pass
            else:
                jd_item = JdItem(
                    item.get('id'),
                    item.get('name'),
                    item.get('good_rate_show'),
                    item.get('poor_rate_show'),
                    item.get('average_score'),
                    item.get('good_count'),
                    item.get('general_rate'),
                    item.get('general_count'),
                    item.get('poor_rate'),
                    item.get('after_count'),
                    item.get('good_rate_style'),
                    item.get('poor_count'),
                    item.get('poor_rate_style'),
                    item.get('general_rate_style'),
                    item.get('comment_count'),
                    item.get('product_id'),
                    item.get('good_rate'),
                    item.get('general_rate_show'),
                    item.get('url'),
                    item.get('item_ids'),
                    item.get('save_time')
                )
                print('创建JdItem对象')
                print(jd_item)
                session.add(jd_item)
                try:
                    session.commit()
                except:
                    session.rollback()


        elif 'comment' == item.get('type'):
            temp = session.query(JdComment).filter(JdComment.id == item.get('id')).first()
            if temp:
                # print(temp)
                pass
            else:
                jd_comment = JdComment(
                    item.get('id'),
                    item.get('item_id'),
                    item.get('content'),
                    item.get('creation_time'),
                    item.get('reply_count'),
                    item.get('score'),
                    item.get('useful_vote_count'),
                    item.get('useless_vote_count'),
                    item.get('user_level_id'),
                    item.get('user_province'),
                    item.get('nickname'),
                    item.get('product_color'),
                    item.get('product_size'),
                    item.get('user_level_name'),
                    item.get('user_client'),
                    item.get('user_client_show'),
                    item.get('is_mobile'),
                    item.get('days'),
                    item.get('reference_time'),
                    item.get('after_days'),
                    item.get('images_count'),
                    item.get('ip'),
                    item.get('after_content'),
                    item.get('save_time')
                )
                print('创建JdComent对象')
                print(jd_comment)
                session.add(jd_comment)
                try:
                    session.commit()
                except:
                    session.rollback()
        return item
