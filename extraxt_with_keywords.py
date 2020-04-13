# -*- coding: utf-8 -*-
"""
解析wiki,通过关键词抽取相关语料
"""

from gensim.corpora.wikicorpus import extract_pages, filter_wiki
import bz2file
import re
from opencc import OpenCC
from tqdm import tqdm
import codecs
import pandas as pd

openCC = OpenCC('t2s')
keywords_pattern = re.compile(r'', re.I)
keywords_list = []
keyword_match_num = 3


def wiki_replace_reg(d):
    s = d[1]
    s = re.sub(':*{\|[\s\S]*?\|}', '', s)
    s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
    s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
    s = filter_wiki(s)
    s = re.sub('\* *\n|\'{2,}', '', s)
    s = re.sub('\n+', '\n', s)
    s = re.sub('\n[:;]|\n +', '\n', s)
    s = re.sub('\n==', '\n\n==', s)
    s = u'【' + d[0] + u'】\n' + s
    s_converted = openCC.convert(s)

    m = keywords_pattern.search(s_converted)
    if m is None:
        return None
    else:
        print(m.group())
        return s_converted


def keywords_search_valid(s_converted):
    global keyword_match_num
    num = 0
    for keyword in keywords_list:
        search_rst = re.search(keyword, s_converted)
        if search_rst is None:
            continue
        else:
            num = num + 1
            if num > keyword_match_num:
                return True
    return False


def wiki_replace_list(d):
    s = d[1]
    s = re.sub(':*{\|[\s\S]*?\|}', '', s)
    s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
    s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
    s = filter_wiki(s)
    s = re.sub('\* *\n|\'{2,}', '', s)
    s = re.sub('\n+', '\n', s)
    s = re.sub('\n[:;]|\n +', '\n', s)
    s = re.sub('\n==', '\n\n==', s)
    s_converted = openCC.convert(s)

    m = keywords_search_valid(s_converted)
    if m is False:
        return None
    else:
        print(s_converted)
        return s_converted


def wiki_process(input_file, save_path):
    wiki = extract_pages(bz2file.open(input_file))
    i = 0
    f = codecs.open(save_path, 'w', encoding='utf-8')
    w = tqdm(wiki, desc=u'已获取0篇文章')

    for d in w:
        if not re.findall('^[a-zA-Z]+:', d[0]) and d[0] and not re.findall(u'^#', d[1]):
            # s = wiki_replace_reg(d)
            s = wiki_replace_list(d)
            if s is None:
                continue
            f.write(s + '\n\n\n')
            i += 1
            if i % 10 == 0:
                w.set_description(u'已获取%s篇文章' % i)
    f.close()


def read_keywords_pattern(keywords_file):
    global keywords_pattern
    f = open(keywords_file, "r")
    lines = "|".join(['.*(' + line.rstrip() + ')' for line in f.readlines()])
    keywords_match = "(" + lines + "){3,}"
    keywords_pattern = re.compile(r'' + keywords_match + r'', re.I)
    print(type(keywords_pattern))
    print("pattern compiled")
    f.close()


def read_keywords_list(keywords_file):
    global keywords_list
    f = open(keywords_file, "r")
    keywords_list = [line.strip('\n\r') for line in f.readlines()]
    print(keywords_list)

    # lines = "|".join(['.*('+line.strip("\n\r")+')' for line in f.readlines()])
    # keywords_match = "("+lines+"){3,}"
    # keywords_pattern = re.compile(r''+keywords_match + r'', re.I)
    # print(type(keywords_pattern))
    # print("pattern compiled")
    f.close()


if __name__ == '__main__':
    input_file = "./raw_data/zhwiki-20200401-pages-articles-multistream.xml.bz2"
    keywords_file = './keywords/keywords.txt'
    save_path = 'output_data/zhwiki-20200401-pages-articles-keywords.txt'
    # read_keywords_pattern(keywords_file)
    read_keywords_list(keywords_file)
    wiki_process(input_file, save_path)