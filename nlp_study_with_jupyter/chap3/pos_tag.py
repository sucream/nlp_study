import re
import requests
from urllib import parse  # 한글을 올바르게 전달하기 위해 인코딩


pt = re.compile(r'(?P<text>.+?)\((?P<pos>.+):.+\)')
# 주로(Noun: 4, 2) 같은 패턴을 text와 pos로 분리해서 사용하기 위한 정규식


def twitter_pos(sentence, concat=False, discard_stopwords=False, discard_verb=False):
    print('[', sentence, '] \n형태소 분석중...', end=' : ')
    sentence = parse.quote(sentence)  # 한글 인코딩
    # print(sentence) 어떻게 변경되는지 확인해보세요
    
    url = 'https://open-korean-text-api.herokuapp.com/normalize?text='
    
    try:
        sentence = requests.get(url=url+sentence, timeout=2).json()
    except requests.exceptions.Timeout as e:
        print('너무 오래 걸림')
        return None
        
    sentence = parse.quote(sentence['strings'])  # 한글 인코딩
    
    url = 'https://open-korean-text-api.herokuapp.com/tokenize?text='
    try:
        response = requests.get(url=url+sentence, timeout=3).json()  # 웹 요청한 결과를 json(dict)으로
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