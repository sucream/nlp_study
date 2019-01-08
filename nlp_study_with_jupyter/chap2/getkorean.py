import requests
from urllib import parse
import re

comp = re.compile(r'\(/SS``\(/SS``([0-9]+?)/SN``\)/SS``\)/SS')
# comp = re.compile(r'\(\(([0-9]+?)\)\)')


def getkorean(ping, is_lsp=False):
    if ping is None:
        return None
    ping = parse.quote(ping)

    url = 'http://demo.forcewin.com:8100/kma/?txt=' + ping
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    response = requests.get(url=url, headers=headers, timeout=5)
    response = response.json()['body']['out']['result']

    if is_lsp:
        original = []
        result = []
        for idx in response:
            for key, val in idx.items():
                original.append(key)
                temp = []
                for i in val:
                    for keys, vals in i.items():
                        temp.append('/'.join((keys, vals)))
                        # if vals in ('NP', 'NNG', 'NNP', 'SN', 'VV', 'VCP', 'VCN', 'VX', 'VA'):
                        #     result.append('/'.join((keys, vals)))
                result.append(temp)

        for idx, group in enumerate(result):
            response = '``'.join(group)
            for mat in comp.finditer(response):
                response = re.sub(re.escape(mat.group()), '(('+mat.group(1)+'))/var_or_entity', response)
                result[idx] = response.split('``')
        # print('최종 리턴', result)
        return {'original': original, 'result': result}

    result = ''
    for idx in response:
        for key, val in idx.items():
            for i in val:
                for keys, vals in i.items():
                    result += keys + ' '

    return result[:-1]

