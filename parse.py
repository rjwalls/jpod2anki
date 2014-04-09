__author__ = 'wallsr'

import argparse
import os
import urllib

from bs4 import BeautifulSoup

_description = "scrapes JapanesePod lesson page to create Anki deck"

#Anki line style
_template = u'<span style="font-family: Mincho; font-size: 50px">!!!WORD!!!</span>\t<span style="font-size: 50px; ">!!!WORD!!!</span><br>!!!ANSWER!!!<br><span style="">[sound:!!!AUDIO!!!]</span>'


def main():
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("deck_file", nargs='?', default='ankideck',
                        help="The output deck filename, can contain a path.")
    parser.add_argument("html_page")
    parser.add_argument("-t", "--tag", type=str, default=None)
    parser.add_argument("-a", "--add", help="Add to existing files. Will overwrite files with same name", action='store_true')
    parser.add_argument("--textonly", action='store_true', help="Set to not download the audio files")
    args = parser.parse_args()


    ankifile = os.path.expanduser(args.deck_file)
    audio_dir = os.path.splitext(ankifile)[0] + '.media'

    if os.path.exists(audio_dir):
        if not args.add:
            print 'Directory %s already exists. Exiting...' % audio_dir
            exit(1)
    else:
        os.makedirs(audio_dir)

    words = get_vocab(args.html_page)

    #Create the file if it doesn't exist, otherwise append to it
    with open(ankifile, 'a+') as f:
        if args.tag:
            f.write("tags:%s" % args.tag + os.linesep)

        for word in words:
            filename = word['audio'].split('/')[-1]
            audiopath = os.path.join(audio_dir, filename)

            line = _template.replace("!!!WORD!!!", word['kana'])\
                .replace("!!!ANSWER!!!", word['english'])\
                .replace("!!!AUDIO!!!", filename).encode('utf-8')

            f.write(line + os.linesep)

            if not args.textonly:
                urllib.urlretrieve(word['audio'], audiopath)

    pass


def get_vocab(filepath):
    with open(filepath, 'r') as f:
        soup = BeautifulSoup(f)
        words_html = soup.find_all('tr', {"id": "tr_words_"})

        words = []

        for word in words_html:
            term = word.find_all('span', {'class': 'term'})[0].string
            kana = word.find_all('span', {'class': 'kana'})[0].string
            english = word.find_all('span', {'class': 'english'})[0].string

            audio = word.find_all('span', {'class': 'ill-onebuttonplayer s17x17px'})[0]['data-url']

            words.append({"term": term,
                          "kana": kana,
                          "english": english,
                          "audio": audio})

        return words


if __name__ == '__main__':
    main()
