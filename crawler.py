import requests
import pymongo
import selenium

host = 'localhost'


def getRaw(URL):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    while True:
        try:
            res = requests.get(URL, headers=headers)
        except:
            continue
        return res.json()


def crawlNaver(word):
    li = []
    syn = []  # 유의어
    atn = []  # 반의어
    dia = []  # 사투리
    for i in range(1, 5):
        obj = getRaw(
            'https://ko.dict.naver.com/api3/koko/search?query=%s&m=pc&range=word&page=%d&shouldSearchOpen=false' % (
                word, i))
        for w in obj['searchResultMap']['searchResultListMap']['WORD']['items']:
            if w['matchType'][:5] == 'exact':
                li.append(w['entryId'])
    for i in li:
        obj = getRaw('https://ko.dict.naver.com/api/platform/koko/entry.nhn?entryId=%s&meanType=undefined' % i)
        if not obj['entry']['relateds']:
            continue
        for w in obj['entry']['relateds']:
            if w['related_type'] == 'syn':  # adjacent
                syn.append(w['related_content'])
            elif w['related_type'] == 'opposite' or w['related_type'] == 'atn':
                atn.append(w['related_content'])
            elif w['related_type'] == 'dialect':
                dia.append(w['related_content'])
    return syn, atn


def connectDB():
    while True:
        try:
            conn = pymongo.MongoClient(host, 27017)
            wordDB = conn["wordDB"]
            return wordDB
        except:

            pass


def getWord(word):
    wordDB = connectDB()
    if wordDB['word'].find_one({"word": word}):
        data = wordDB['word'].find_one({"word": word})
        return data['syn'], data['atn']
    n_syn, n_atn = crawlNaver(word)

    syn = n_syn
    atn = n_atn
    ts = set(syn)
    ts.discard(word)
    syn = list(ts)
    ts = set(atn)
    ts.discard(word)
    atn = list(ts)
    wordDB['word'].insert_one({
        'word': word,
        'syn': syn,
        'atn': atn
    })
    return syn, atn


print(getWord(input()))