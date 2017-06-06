import copy
import time
from collections import Counter
import os

import sys
from flask import Flask, render_template, jsonify

from utils import sql_session
from utils.models import JdComment, JdItem
from utils.parse_page import parse_search_page, parse_detail_page
from utils.nlp import main

app = Flask(__name__)


# real exsist page
@app.route('/')
def index():
    return 'Index!'


@app.route('/general')
def general():
    return render_template('general.html')


@app.route('/pro')
def pro():
    return render_template('pro.html')


@app.route('/product/<int:product_id>')
def product(product_id):
    return render_template('product_detail.html', product_id=product_id)


# for ajax
@app.route('/general_ajax', methods=['GET'])
def general_ajax():
    products = parse_search_page()
    return jsonify(products)


@app.route('/pro_ajax')
def pro_ajax():
    ids = []
    products = []
    current_path = sys.path[0]
    assets_path = os.path.join(current_path, 'assets')
    aspect_path = os.path.join(assets_path, 'aspect')
    for file in os.listdir(aspect_path):
        ids.append(file.split('.')[0])
        id = file.split('.')[0]
        item = sql_session.query(JdItem.name).filter(JdItem.id == id).first()
        if item:
            name = item[0]
            print(name)
            product = {
                'name': name.split('】')[0] + '】',#''.join([part for part in name.split(' ')[0:4] if 'GB' not in part]),
                # 'img': product_img,
                'id': '/product/{0}'.format(id)
            }
            products.append(product)
    print(products)
    return jsonify(products)


@app.route('/detail/<int:product_id>', methods=['GET'])
def detail(product_id):
    comments = [comment.content for comment in
                sql_session.query(JdComment).filter(JdComment.item_id == product_id).limit(100).all()]
    if len(comments) < 100:
        comments = parse_detail_page(product_id)
    analyse_result = main(product_id, comments)
    print(analyse_result)
    comments_list = [{'comment': comment} for comment in comments]
    result = {
        'tables': comments_list,
        'items': analyse_result
    }
    return jsonify(result)

@app.route('/get_item/<int:product_id>')
def get_item(product_id):
    pie_pic_model = {
        'title': {
            'text': '',
            'x': 'center'
        },
        'tooltip': {
            'trigger': 'item',
            'formatter': "{a} <br/>{b} : {c} ({d}%)"
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'data': []
        },
        'series': [
            {
                'name': '',
                'type': 'pie',
                'radius': '55%',
                'center': ['50%', '60%'],
                'data': [],
                'itemStyle': {
                    'emphasis': {
                        'shadowBlur': 10,
                        'shadowOffsetX': 0,
                        'shadowColor': 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }

    jd_item = sql_session.query(JdItem).filter(JdItem.id == product_id).first()
    comments = sql_session.query(JdComment).filter(JdComment.item_id == product_id).all()

    # 统计颜色信息
    colors = [comment.product_color for comment in comments]
    color_counter = Counter()
    for color in colors:
        color_counter[color] += 1
    color_count = {k: v for k, v in color_counter.items()}

    # 统计配置信息
    sizes = [comment.product_size for comment in comments]
    size_counter = Counter()
    for size in sizes:
        size_counter[size] += 1
    size_count = {k: v for k, v in size_counter.items()}

    # 统计评论设备信息
    devices = [comment.user_client_show for comment in comments]
    device_counter = Counter()
    for device in devices:
        device_counter[device] += 1
    device_count = {k: v for k, v in device_counter.items()}

    # 统计评论时段信息
    hours = [comment.reference_time.split(' ')[1].split(':')[1] for comment in comments]
    hour_counter = Counter()
    for hour in hours:
        hour_counter[hour] += 1
    hour_count = {k: v for k, v in hour_counter.items()}

    if jd_item:
        comment_level_option = copy.deepcopy(pie_pic_model)
        comment_level_option['title']['text'] = '不同等级评价比例'
        comment_level_option['legend']['data'] = ['好评', '中评', '差评']
        comment_level_option['series'][0]['data'] = [
            {'value': jd_item.good_count, 'name': '好评'},
            {'value': jd_item.general_count, 'name': '中评'},
            {'value': jd_item.poor_count, 'name': '差评'}
        ]

        colors_option = copy.deepcopy(pie_pic_model)
        colors_option['title']['text'] = '不同颜色比例'
        colors_option['legend']['data'] = [color_name for color_name in color_count.keys()]
        colors_option['series'][0]['data'] = [{'value': v, 'name': k} for k, v in color_count.items()]

        sizes_option = copy.deepcopy(pie_pic_model)
        sizes_option['title']['text'] = '不同配置比例'
        sizes_option['legend']['data'] = [size_name for size_name in size_count.keys()]
        sizes_option['series'][0]['data'] = [{'value': v, 'name': k} for k, v in size_count.items()]

        devices_option = copy.deepcopy(pie_pic_model)
        devices_option['title']['text'] = '不同渠道比例'
        devices_option['legend']['data'] = [device_name for device_name in device_count.keys()]
        devices_option['series'][0]['data'] = [{'value': v, 'name': k} for k, v in device_count.items()]

        my_data = {
            'comment_level_option': comment_level_option,
            'colors_option': colors_option,
            'sizes_option': sizes_option,
            'devices_option': devices_option,
            'hours_option': {

            },

            'rate': jd_item.average_score,
            'name': jd_item.name,
            'url': 'https://item.jd.com/{0}.html'.format(jd_item.id)
        }

        print(my_data)
        return jsonify(my_data)
    else:
        return jsonify()


if __name__ == '__main__':
    app.run(debug=True)
