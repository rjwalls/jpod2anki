__author__ = 'wallsr'

import argparse
import os
import urllib

from bs4 import BeautifulSoup

_description = "scrapes JapanesePod lesson page to create Anki deck"

#Anki line style
#Assumes a note template that takes the following five fields
_template = u'!!!WORD!!!\t!!!ANSWER!!!\t!!!READING!!!\t[sound:!!!AUDIO!!!]\t!!!EXAMPLE!!!\t!!!TAG!!!'


def main():
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("deck_file", nargs='?', default='ankideck',
                        help="The output deck filename, can contain a path.")
    parser.add_argument("html_page")
    parser.add_argument("-t", "--tag", type=str, default=None, help="Defaults to page title.")
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

    with open(args.html_page, 'r') as f:
        soup = BeautifulSoup(f)

        if not args.tag:
            args.tag = get_tag(soup)

        words = get_vocab(soup)

        for word in words:
            example = get_example(soup, word['kana'])

            if example:
                word['example'] = get_example_html(example)


    #Create the file if it doesn't exist, otherwise append to it
    with open(ankifile, 'a+') as f:
        #if args.tag:
        #    f.write("tags:%s" % args.tag + os.linesep)

        print "Adding %d words." % len(words)

        for word in words:
            if word['english'] is None:
                print 'No definition for: ', word['kana']
                continue

            filename = word['audio'].split('/')[-1]
            audiopath = os.path.join(audio_dir, filename)

            line = _template.replace("!!!WORD!!!", word['kana'])\
                .replace("!!!ANSWER!!!", word['english'])\
                .replace("!!!AUDIO!!!", filename)\
                .replace("!!!READING!!!", "")

            if 'example' in word:
                line = line.replace("!!!EXAMPLE!!!", word['example'])
            else:
                line = line.replace("!!!EXAMPLE!!!", "")

            if args.tag:
                line = line.replace("!!!TAG!!!", args.tag)
            else:
                line = line.replace("!!!TAG!!!", "")

            f.write(line.encode('utf-8') + os.linesep)

            if not args.textonly:
                urllib.urlretrieve(word['audio'], audiopath)

    pass


def get_tag(soup):
    #Grab the title to use for the tags
    titles = soup.find_all('div', {'class': 'ill-lesson-main-title'})

    if len(titles) == 0:
        print 'No title found. Not adding tags.'
        return

    tag = titles[0].string.replace('.', '_').replace(' ', '_')

    print 'Tag:', tag

    return tag


def get_vocab(soup):
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


def get_example_html(example):
    kana, english = example

    return u"%s<br><i>%s</i>" % (kana.strip(), english.strip())


def get_example(soup, kana_word):
    """
    Looks for an example sentence containing the word.
    """

    sentence_table_kana = soup.find_all('table', {'class': 'lesson-lbl-table lesson-transcript-Japanese transcript-7 ltr'})
    sentence_table_english = soup.find_all('table', {'class': 'lesson-lbl-table lesson-transcript-Japanese transcript-2 ltr'})

    kana_lines = sentence_table_kana[0].find_all('td', {'class': 'ctext'})
    kana_lines = [l.string for l in kana_lines]

    english_lines = sentence_table_english[0].find_all('td', {'class': 'ctext'})
    english_lines = [l.string for l in english_lines]

    #Split on '(' aka \uff08
    kana_word = kana_word.split(u'\uff08')[0].strip()

    #Remove the weird long tilde \uff5e, used by jpod to denote prefixes and suffixes
    kana_word = kana_word.replace(u'\uff5e', '')

    for x in xrange(len(kana_lines)):
        if kana_word in kana_lines[x]:
            return kana_lines[x], english_lines[x]

    #We didn't find the whole word, so we need to guess now.
    #e.g., Conjugated verbs won't match the kana_word
    #Restrict ourselves to matching at least two kana
    for y in xrange(len(kana_word), 1, -1):
        sub = kana_word[:y]
        for x in xrange(len(kana_lines)):
            if sub in kana_lines[x]:
                return kana_lines[x], english_lines[x]

    print 'No example found for: ', kana_word

    return


if __name__ == '__main__':
    main()
