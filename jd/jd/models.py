from sqlalchemy import Column, Integer, String, Text, Float, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JdItem(Base):
    __tablename__ = 'jd_items'

    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    good_rate_show = Column(Integer)
    poor_rate_show = Column(Integer)
    average_score = Column(Integer)
    good_count = Column(Integer)
    general_rate = Column(Float)
    general_count = Column(Integer)
    poor_rate = Column(Float)
    after_count = Column(Integer)
    good_rate_style = Column(Integer)
    poor_count = Column(Integer)
    poor_rate_style = Column(Integer)
    general_rate_style = Column(Integer)
    comment_count = Column(Integer)
    product_id = Column(Integer)
    good_rate = Column(Float)
    general_rate_show = Column(Integer)
    url = Column(String(255))
    item_ids = Column(String(255))
    save_time = Column(String(255))

    def __init__(self, id, name, good_rate_show, poor_rate_show, average_score,
                 good_count, general_rate, general_count, poor_rate, after_count,
                 good_rate_style, poor_count, poor_rate_style,
                 general_rate_style, comment_count, product_id, good_rate,
                 general_rate_show, url, item_ids, save_time):
        self.id = id
        self.name = name
        self.good_rate_show = good_rate_show
        self.poor_rate_show = poor_rate_show
        self.average_score = average_score
        self.good_count = good_count
        self.general_rate = general_rate
        self.general_count = general_count
        self.poor_rate = poor_rate
        self.after_count = after_count
        self.good_rate_style = good_rate_style
        self.poor_count = poor_count
        self.poor_rate_style = poor_rate_style
        self.general_rate_style = general_rate_style
        self.comment_count = comment_count
        self.product_id = product_id
        self.good_rate = good_rate
        self.general_rate_show = general_rate_show
        self.url = url
        self.item_ids = item_ids
        self.save_time = save_time

    def __repr__(self):
        return '<JdItem: {0}>'.format(self.name)


class JdComment(Base):
    __tablename__ = 'jd_comments'

    id = Column(BigInteger, primary_key=True)
    item_id = Column(String(255))
    content = Column(Text)
    creation_time = Column(String(255))
    reply_count = Column(Integer)
    score = Column(Integer)
    useful_vote_count = Column(Integer)
    useless_vote_count = Column(Integer)
    user_level_id = Column(String(255))
    user_province = Column(String(255))
    nickname = Column(String(255))
    product_color = Column(String(255))
    product_size = Column(String(255))
    user_level_name = Column(String(255))
    user_client = Column(Integer)
    user_client_show = Column(String(255))
    is_mobile = Column(Boolean)
    days = Column(Integer)
    reference_time = Column(String(255))
    after_days = Column(Integer)
    images_count = Column(Integer)
    ip = Column(String(255))
    after_content = Column(String(255))
    save_time = Column(String(255))

    def __init__(self, id, item_id, content, creation_time, reply_count, score,
                 useful_vote_count, useless_vote_count, user_level_id,
                 use_province,nickname,product_color,product_size,
                 user_level_name,user_client,user_client_show,is_mobile,
                 days,reference_time,after_days,images_count,ip,
                 after_content,save_time):
        self.id=id
        self.item_id=item_id
        self.content=content
        self.creation_time=creation_time
        self.reply_count=reply_count
        self.score=score
        self.useful_vote_count=useful_vote_count
        self.useless_vote_count=useless_vote_count
        self.user_level_id=user_level_id
        self.user_province=use_province
        self.nickname=nickname
        self.product_color=product_color
        self.product_size=product_size
        self.user_level_name=user_level_name
        self.user_client=user_client
        self.user_client_show=user_client_show
        self.is_mobile=is_mobile
        self.days=days
        self.reference_time=reference_time
        self.after_days=after_days
        self.images_count=images_count
        self.ip=ip
        self.after_content=after_content
        self.save_time=save_time

    def __repr__(self):
        return '<JdComment: {0}>'.format(self.content)