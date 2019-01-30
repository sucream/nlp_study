import re
import requests
import time

from urllib import parse  # 한글을 올바르게 전달하기 위해 인코딩
import asyncio

pt = re.compile(r'(?P<text>.+?)\((?P<pos>.+):.+\)')


# 주로(Noun: 4, 2) 같은 패턴을 text와 pos로 분리해서 사용하기 위한 정규식


def twitter_pos(sentence, concat=False, time_out=3, discard_stopwords=False, discard_verb=False):
    print('[', sentence, '] \n\n형태소 분석중...', end=' : ')
    sentence = parse.quote(sentence)  # 한글 인코딩
    # print(sentence) 어떻게 변경되는지 확인해보세요

    url = 'https://open-korean-text-api.herokuapp.com/normalize?text='

    try:
        sentence = requests.get(url=url + sentence, timeout=time_out).json()
    except requests.exceptions.Timeout as e:
        print('너무 오래 걸림')
        return None

    sentence = parse.quote(sentence['strings'])  # 한글 인코딩

    url = 'https://open-korean-text-api.herokuapp.com/tokenize?text='
    try:
        response = requests.get(url=url + sentence, timeout=time_out).json()  # 웹 요청한 결과를 json(dict)으로
    except requests.exceptions.Timeout as e:
        print('너무 오래 걸림')
        return None
    tokens = []
    for i in response['tokens']:
        m = pt.match(i)
        if m:
            if discard_verb:
                if 'Verb' in m.group('pos'):
                    continue
            if discard_stopwords:
                if m.group('pos') in ('Punctuation', 'Josa'):
                    continue
            if concat:
                tokens.append(m.group('text') + '/' + m.group('pos'))
            else:
                tokens.append((m.group('text'), m.group('pos')))

    print('OK\n')
    return tokens


def new_pos(sentences, concat=True, time_out=3, discard_stopwords=False, discard_verb=False):
    start_time = time.time()
    if type(sentences) == str:
        print('[ 한 문장 형태소 분석 ]')
        user_data = [sentences]
    else:
        print('[ 다중 문장 형태소 분석 ]')
        user_data = sentences

    async def get_pos(url):
        response = await loop.run_in_executor(None, requests.get, url)
        response = response.json()
        tokens = []
        for i in response['tokens']:
            m = pt.match(i)
            if m:
                if discard_verb:
                    if 'Verb' in m.group('pos'):
                        continue
                if discard_stopwords:
                    if m.group('pos') in ('Punctuation', 'Josa'):
                        continue
                if concat:
                    tokens.append(m.group('text') + '/' + m.group('pos'))
                else:
                    tokens.append((m.group('text'), m.group('pos')))
        return tokens

    async def excute(data):
        url = 'https://open-korean-text-api.herokuapp.com/tokenize?text={0}'
        result = [asyncio.ensure_future(get_pos(url.format(sent))) for sent in data]
        return await asyncio.gather(*result)

    loop = asyncio.get_event_loop()
    pos_result = loop.run_until_complete(excute(user_data))

    end_time = time.time()
    print('최종 수행시간:', end_time - start_time)
    return pos_result