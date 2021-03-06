# -*- coding: utf-8 -*-
"""Haystack_tag_parsing.ipynb

Automatically generated by Colaboratory.

## Module Import
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re

"""## HTML 및 BeautifulSoup 오브젝트 열기"""

html = urlopen('https://project-haystack.org/tag')
bsObject = BeautifulSoup(html, 'html.parser')

"""## 파싱한 데이터에서 쓸데없는 tag 제거하는 함수"""

def remove_tag(content):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext

"""## tag 부분만 파싱후 내부 쓸데없는 tag 제거"""

tag = []
for i in range(0, len(bsObject.find_all('td')),2):
    tag.append(remove_tag(str(bsObject.find_all('td')[i])))

"""## 약 230개의 tag가 있음."""

len(tag)

tag

tagframe = pd.DataFrame(tag)

"""## tag의 내용(content)에 대한 parsing"""

doc = bsObject.find_all('p')

content = []
for i in range(len(doc)):
    content.append(re.sub('<.+?>','',str(doc[i]),0).strip())

"""## 페이지 마지막에 license 항목이 하나 잇어서 길이 안맞아 제거."""

content = content[:-1]   ## 마지막에 license 제외해줘야 한다.

content

"""## tag와 마찬가지로 230개의 content"""

len(content)

contentframe = pd.DataFrame(content)

"""## 최종 output 형태(임의대로 변경)로 저장"""

result = pd.concat([tagframe, contentframe], axis=1)
result.columns = ['tag', 'content']

result

result.to_csv('tag-content.csv', index=0)
