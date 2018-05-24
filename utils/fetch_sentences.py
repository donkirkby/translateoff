from itertools import islice
import os
import re
import tarfile
from unicodedata import category

# noinspection PyPackageRequirements
import requests


def open_or_fetch(url, local_path):
    if not os.path.exists(local_path):
        print('Downloading', url)
        response = requests.get(url, stream=True)
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=16*1024):
                f.write(chunk)
    if local_path.endswith('.tar.bz2'):
        with tarfile.open(local_path, 'r:bz2') as f:
            tar_info = f.next()
            yield from f.extractfile(tar_info)
    else:
        with open(local_path) as f:
            yield from f


def fetch_sentences(characters):
    sentences_url = 'http://downloads.tatoeba.org/exports/sentences.tar.bz2'
    sentences = {}  # {id: (lang, text)}
    for line in open_or_fetch(sentences_url, 'downloads/sentences.tar.bz2'):
        sentence_id, lang, text = line.decode('utf8').strip().split('\t')
        if lang in ('cmn', 'eng'):
            sentences[sentence_id] = (lang, text)
        # lzh? hsn, gan? probably cmn, but are there any simplified?
    fetched_chinese_ids = set()
    links_url = 'http://downloads.tatoeba.org/exports/links.tar.bz2'
    for line in open_or_fetch(links_url, 'downloads/links.tar.bz2'):
        from_id, to_id = line.decode('utf8').strip().split('\t')
        from_lang, from_text = sentences.get(from_id, (None, ''))
        to_lang, to_text = sentences.get(to_id, (None, ''))
        if not (from_lang and to_lang):
            continue
        if from_lang == 'eng':
            from_text, to_text = to_text, from_text
            from_lang, to_lang = to_lang, from_lang
            from_id, to_id = to_id, from_id
        if to_lang == 'cmn':
            # Both sentences are Chinese.
            continue

        if from_id not in fetched_chinese_ids:
            if is_selected(from_text, characters):
                yield from_text, to_text
                fetched_chinese_ids.add(from_id)


def is_selected(text, characters):
    for c in text:
        t = category(c)
        if t not in ('Lo', 'Po'):
            return False
        if t == 'Lo' and c not in characters:
            return False
    return True


def main():
    hsk1_url = ('https://en.wiktionary.org/w/index.php'
                '?title=Appendix:HSK_list_of_Mandarin_words/Beginning_Mandarin'
                '&action=raw')
    simplified = {}
    hsk1 = set()
    for line in open_or_fetch(hsk1_url, 'downloads/hsk1.txt'):
        # * {{zh-l|半|tr=bàn}}
        # * {{zh-l|辦/办|tr=bàn}}
        match = re.match(r'\* {{zh-l\|(.)(/(.))?\|', line)
        if match:
            hsk1.add(match.group(1))
            if match.group(3):
                simplified[match.group(1)] = match.group(3)

    simplified_translation = str.maketrans(simplified)

    for chinese_text, english_text in islice(fetch_sentences(hsk1), 2000):
        print(chinese_text.translate(simplified_translation))
        print(english_text)


main()
