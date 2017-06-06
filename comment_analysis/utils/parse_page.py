from lxml import etree
import re
from datetime import datetime
import json
from .models import JdItem, JdComment
import requests
from utils import sql_session
session = requests.session()

def parse_search_page():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Host': 'search.jd.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }

    search_url = 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA'
    session.headers = headers
    response = session.get(search_url)
    page = response.content.decode('utf-8')
    html = etree.HTML(page)

    items = html.xpath('//li[@class="gl-item"]')
    products = []
    for item in items:
        product_name = ''.join(item.xpath('.//div[@class="p-name p-name-type-2"]/a/em/text()'))
        pattern1 = '（.*）'
        product_name = re.sub(pattern1, '', product_name)
        product_name = product_name.replace('移动联通电信4G', '全网通')
        product_img = item.xpath('.//div[@class="p-img"]/a/img/@src')
        if len(product_img) == 0:
            product_img = item.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img')
        try:
            product_img = product_img[0]
        except:
            pass

        product_link = item.xpath('.//div[@class="p-img"]/a/@href')
        try:
            product_link = product_link[0]
        except:
            pass
        id = re.match(r'(.*)/(\d+)\.html', product_link)
        if id:
            product = {
                'name': ' '.join([part for part in product_name.split(' ')[:3] if 'GB' not in part]),
                'img': product_img,
                'id': '/product/{0}'.format(id.group(2))
            }
            products.append(product)
        else:
            pass
    print(products)
    return products

def parse_detail_page(product_id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Referer': 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=shou%27ji&pvid=6a9f244790eb47dea2801c394f708dca',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    comment_list = []
    def get_comment_url(product_id):
        detail_url = 'https://item.jd.com/{0}.html'.format(product_id)
        session.headers=headers
        response = session.get(detail_url)
        page = response.content.decode('gbk', 'ignore')
        html = etree.HTML(page)
        name = html.xpath('//head/title/text()')
        pattern = re.compile('commentVersion:\'(\d+)\'', re.S)
        comment_version = re.search(pattern, page).group(1)
        ids = html.xpath('//div[@class="dd"]/div/@data-sku')
        item_ids = ','.join(ids)
        url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv' \
              '{comment_version}&productId={product_id}&score=0&sortType={sort_type}&page=0&pageSize=10' \
              '&isShadowSku=0'. \
            format(product_id=product_id, comment_version=comment_version, sort_type='6')
        return (name, url, item_ids)

    def get_one_page(url):
        session.headers['Host'] = 'club.jd.com'
        session.headers['Referer'] = 'https://item.jd.com/{0}.html'.format(product_id)
        resonse = session.get(url)
        page = resonse.content.decode('gb2312', 'ignore')
        return page

    def get_a_comment(url):
        page = get_one_page(url)
        pattern = re.compile('\((.*?)\);', re.S)
        item = re.search(pattern, page)
        if item != None and item.group(1) != None:
            try:
                data = json.loads(item.group(1))
                parse_comment(data)
            except:
                pass

    def get_all_comments(name, url, item_ids):
        page = get_one_page(url)
        pattern = re.compile('\((.*?)\);', re.S)
        item = re.search(pattern, page)
        if item != None and item.group(1) != None:
            try:
                data = json.loads(item.group(1))
                pcs = data.get('productCommentSummary')
                temp = sql_session.query(JdItem).filter(JdItem.id==product_id).first()
                if temp:
                    print(temp)
                else:
                    jd_item = JdItem(
                        product_id,
                        name,
                        pcs.get('goodRateShow'),
                        pcs.get('poorRateShow'),
                        pcs.get('averageScore'),
                        pcs.get('goodCount'),
                        pcs.get('generalRate'),
                        pcs.get('generalCount'),
                        pcs.get('poorRate'),
                        pcs.get('afterCount'),
                        pcs.get('goodRateStyle'),
                        pcs.get('poorCount'),
                        pcs.get('poorRateStyle'),
                        pcs.get('generalRateStyle'),
                        pcs.get('commentCount'),
                        pcs.get('productId'),
                        pcs.get('goodRate'),
                        pcs.get('generalRateShow'),
                        url,
                        item_ids,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    print(jd_item)
                    sql_session.add(jd_item)
                    try:
                        sql_session.commit()
                    except:
                        sql_session.rollback()

                page_count = data.get('maxPage')
                count = min(20, page_count)
                for i in range(1, count):
                    former_page = re.search(r'(.*)(page=\d+)(.*)', url)
                    former_page = former_page.group(2)
                    new_url = url.replace(former_page, 'page={0}'.format(i))
                    get_a_comment(new_url)
            except:
                pass

    def parse_comment(data):
        comments = data.get('comments', [])
        if comments:
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

                content = content.replace('\'', '').replace('\n', ' ')
                after_content = after_content.replace('\'', '')

                temp = sql_session.query(JdComment).filter(JdComment.id == id).first()
                if temp:
                    print(temp)
                    comment_list.append(temp.content)
                else:
                    jd_comment = JdComment(
                        id,
                        product_id,
                        content,
                        creation_time,
                        reply_count,
                        score,
                        useful_vote_count,
                        useless_vote_count,
                        user_level_id,
                        user_province,
                        nickname,
                        product_color,
                        product_size,
                        user_level_name,
                        user_client,
                        user_client_show,
                        is_mobile,
                        days,
                        reference_time,
                        after_days,
                        images_count,
                        ip,
                        after_content,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )

                    print(jd_comment)
                    sql_session.add(jd_comment)
                    try:
                        sql_session.commit()
                    except:
                        sql_session.rollback()
                    comment_list.append(jd_comment.content)

    name, url, item_ids = get_comment_url(product_id)
    print('商品名称: {0}'.format(name))
    print('商品链接: {0}'.format(url))
    get_all_comments(name, url, item_ids)
    return comment_list


if __name__ == '__main__':
    parse_search_page()
