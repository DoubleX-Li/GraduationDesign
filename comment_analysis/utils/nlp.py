import os
import pickle

import sys
from pyltp import Parser
from pyltp import Postagger
import jieba
from snownlp import SnowNLP
from collections import Counter

LTP_DATA_DIR = 'D:\ltp_data'  # ltp模型目录的路径
aspect_path = os.path.join(os.path.join(sys.path[0], 'assets'), 'aspect')


def segmentor(text):
    seg_list = jieba.cut(text)
    words = [seg for seg in seg_list]
    print('\t'.join(['{0}:{1}'.format(index + 1, word) for index, word in enumerate(words)]))
    return words


def postagger(words):
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`

    postagger = Postagger()  # 初始化实例
    postagger.load(pos_model_path)  # 加载模型

    postags = postagger.postag(words)  # 词性标注

    print('\t'.join(['{0}:{1}'.format(index + 1, postag) for index, postag in enumerate(postags)]))

    postagger.release()  # 释放模型

    return postags


def parser(words, postags):
    par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

    parser = Parser()  # 初始化实例
    parser.load(par_model_path)  # 加载模型

    arcs = parser.parse(words, postags)  # 句法分析

    print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    parser.release()  # 释放模型
    return arcs


def foo(noun_adj_list):
    aspect_dict = dict()
    for pair in noun_adj_list:
        s = SnowNLP(pair[1])
        if not pair[0] in aspect_dict.keys():
            aspect_dict[pair[0]] = {
                'count': 1,
                'adj': [pair[1]],
                'total_sentiment': s.sentiments
            }
        elif pair[0] in aspect_dict.keys():

            aspect_dict[pair[0]]['count'] += 1
            aspect_dict[pair[0]]['adj'].append(pair[1])
            aspect_dict[pair[0]]['total_sentiment'] += s.sentiments

    print(aspect_dict)
    return aspect_dict


def bar(product_id, aspect_dict):
    aspect_list = []
    for k, v in aspect_dict.items():
        total_sentiment = v.get('total_sentiment')
        total_sentiment /= len(v.get('adj'))

        if 0 <= int(total_sentiment * 100) < 30:
            total_sentiment = 'danger'
        elif 30 <= int(total_sentiment * 100) < 70:
            total_sentiment = 'warning'
        elif 70 <= int(total_sentiment * 100) <= 100:
            total_sentiment = 'success'
        else:
            total_sentiment = 'primary'

        v['total_sentiment'] = total_sentiment
        aspect_list.append((k, v))

    sorted_aspect_list = sorted(aspect_list, key=lambda x: x[1].get('count'), reverse=True)

    # for item in sorted_aspect_list:
    #     print('{0} -> {1} -> {2}'.format(item[0], item[1].get('count'), set(item[1].get('adj'))))
    # print(item[0] + ' -> ' + str(item[1].get('count')) + ' -> ' + str(set(item[1].get('adj'))))
    # print(sorted_aspect_list)
    temp_other = None
    items = []
    for item in sorted_aspect_list:
        adjs_dict = Counter()

        for adj in item[1].get('adj'):
            adjs_dict[adj] += 1

        adjs = [{'text': k, 'count': v} for k, v in adjs_dict.items() if '' != k.strip()]
        sorted_adjs = sorted(adjs, key=lambda x: x.get('count'), reverse=True)
        print(sorted_adjs)

        if item[0].strip() != '' and item[1].get('count') >= 3 and '其他' != item[0]:
            temp_dict = {
                'text': item[0],
                'adjs': sorted_adjs,
                'sentiment': item[1].get('total_sentiment')
            }
            items.append(temp_dict)
        elif item[0] == '其他':
            temp_other = {
                'text': item[0],
                'adjs': sorted_adjs,
                'sentiment': item[1].get('total_sentiment')
            }

    if temp_other:
        items.append(temp_other)

    with open(os.path.join(aspect_path, '{0}.data'.format(product_id)), 'wb') as f:
        pickle.dump(items, f)
    return items


def main(product_id, comments):
    noun_adj_list = []
    total = len(comments[:100])
    if os.path.exists(os.path.join(aspect_path, '{0}.data'.format(product_id))):
        print('read aspect.data from exsist!')
        with open(os.path.join(aspect_path, '{0}.data'.format(product_id)), 'rb') as f:
            items = pickle.load(f)
    else:
        for index, comment in enumerate(comments[:100]):
            print('{0} of {1}'.format(index + 1, total))
            words = segmentor(comment)
            postags = postagger(words)
            arcs = parser(words, postags)

            sentence_adj = []
            for index, arc in enumerate(arcs):
                if arc.relation == 'SBV' and postags[index] == 'n' and postags[arc.head - 1] not in ['n', 'v', 'd']:
                    sentence_adj.append(words[arc.head - 1])
                    print(words[index] + ' -> ' + words[arc.head - 1])
                    noun_adj_list.append((words[index], words[arc.head - 1]))

            for index, word in enumerate(words):
                if postags[index] == 'a' and word not in sentence_adj:
                    sentence_adj.append(word)
                    print('其他 -> ' + word)
                    noun_adj_list.append(('其他', word))

            print()
        items = bar(product_id, foo(noun_adj_list))
    return items
