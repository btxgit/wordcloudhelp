#!/usr/bin/env python3

'''
                     __    __             ____       __
 _    _____  _______/ /___/ /__  __ _____/ / /  ___ / /__
| |/|/ / _ \/ __/ _  / __/ / _ \/ // / _  / _ \/ -_) / _ \
|__,__/\___/_/  \_,_/\__/_/\___/\_,_/\_,_/_//_/\__/_/ .__/
                                                   /_/
python 3 code that demonstrates the creation of a
wordcloud that conforms to a mask and colormap

'''

import os
import sys
import json
import argparse
import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

# Global default values
WORDFILE = 'input/words.json'
STOPFILE = 'input/stopwords.txt'
MASKFILE = 'img/zoid_mask2_trans.png'
COLORFILE = 'img/zoid_big2_trans.png'
OUTFILE = 'wordcloud_output.png'
DEFRES = (1600, 1600)

class wchelp(object):
    ''' This class generates a word cloud in a fairly manual
        process.  Instead of working from your own dictionary,
        you can just pass in a string holding the text you want
        to make the image out of.  In this case, you would use
        the generate method rather than
        generate_from_frequencies()
    '''
    def __init__(self,
                 wordfile=WORDFILE,
                 stopfile=STOPFILE,
                 maskfile=MASKFILE,
                 colorfile=COLORFILE,
                 outfile=OUTFILE,
                 outres=DEFRES,
                 verbose=0):
        self.words = {}
        self.weighted_words = {}
        self.totwords = 0
        self.stopwords = []

# Prepare stopfile words - 1 word per linee
        if os.path.exists(stopfile):
            with open(stopfile, 'rt', encoding='utf-8') as fd:
                self.stopwords = [ frstr for frstr in list(set(fd.read().split('\n'))) if frstr != '' ]

# Prepare word file - a dict stored in JSON encoding
        dels = []
        if os.path.exists(wordfile):
            with open(wordfile, 'rt', encoding='utf-8') as fd:
                self.words = json.loads(fd.read())
            for word in self.words.keys():
                if word in self.stopwords:
                    dels.append(word)
                else:
                    self.totwords += self.words[word]

# Remove any words in the stopwords
            for delword in dels:
                del(self.words[delword])

            for word in self.words.keys():
                wt = self.words[word] / self.totwords
                self.weighted_words[word] = wt
                if verbose > 0:
                    print("Word {} represents {} of the {} words, giving it a weight of {:.8f}".format(word, self.words[word], self.totwords, wt))

# Prepare mask & colormap
        mask_im = Image.open(maskfile, 'r')
        colors_im = Image.open(colorfile, 'r')
        self.shitty_mask = np.array(mask_im)
        self.shitty_colors = np.array(colors_im)

        self.wcloud = WordCloud(mask=self.shitty_mask, stopwords=self.stopwords,
                                min_font_size=2, max_font_size=80,
                                max_words=1000,
                                width=outres[0],
                                height=outres[1],
                                relative_scaling=0.50)

        self.wcloud.generate_from_frequencies(self.weighted_words)
        image_colors = ImageColorGenerator(self.shitty_colors, default_color=(0,0,0))
        self.wcloud.recolor(color_func=image_colors)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="wordcloud help")

    parser.add_argument('-o', type=str, default=OUTFILE, dest='outputfile', help='Set the output path for the wordcloud image')
    parser.add_argument('-s', type=str, default=STOPFILE, dest='stopfile', help='Set the path of your stopwords file, 1 word per line')
    parser.add_argument('-v', default=0, action='count', dest='verbosity', help='Verbosity - specify to see some debug output')
    parser.add_argument('-w', type=str, default=WORDFILE, dest='wordfile', help='Set the path of the JSON-encoded input for your weighted dictionary wordlist')
    parser.add_argument('--colors', type=str, default=COLORFILE, dest='colorfile', help='Set a color file for your wordcloud output')
    parser.add_argument('--mask', type=str, default=MASKFILE, dest='maskfile', help='Set a mask file for your wordcloud output')
    parser.add_argument('--width', type=int, default=1600, dest='width', help='Set the output image\'s width')
    parser.add_argument('--height', type=int, default=1600, dest='height', help='Set the output image\'s height')

    args = parser.parse_args(sys.argv[1:])

# Instantiate the class defined above with the vals set in the arg parser
    wc = wchelp(wordfile=args.wordfile,
                stopfile=args.stopfile,
                maskfile=args.maskfile,
                colorfile=args.colorfile,
                outfile=args.outputfile,
                outres=(args.width, args.height),
                verbose=args.verbosity)

    wc.wcloud.to_file(args.outputfile)
    print("Output file: {}".format(args.outputfile))
