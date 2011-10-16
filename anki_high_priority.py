#!/usr/bin/env python2
# coding=utf-8

import os, sys, imp

import anki
from anki.cards import Card
from anki.facts import Fact


words = ['主に',
         '亀',
         'ブックオッフ',
         'poop',
         'なさる',
         '日帰り',
         '一種',
         '不在',
         '欠席',
         '絶対',
         ]


# this is the query used to check if there are any facts that
# match the word we are searching
sql_word_query = 'select id from facts where id in (select factId from fields where value = :field_value and fieldModelId in (select id from fieldModels where name = :field_name))'

def opendecks(deck_info):
    """
    Open all the decks that are listed at the top of the file in the
    deck_names variable.  This will raise an exception if it can't
    open one of the decks listed.

    This returns a list of tuples.  The tuples are of the form
    ("/path/to/deck", "fieldname", deckobject).
    """
    decks = []
    current_name = ''

    try:
        for name, fieldname in deck_info:
            current_name = name
            d = anki.DeckStorage.Deck(name)
            newinfo = (name, fieldname, d)
            decks.append(newinfo)
    except:
        sys.stderr.write("ERROR! Caught exception while opening deck \"%s\"\n" % current_name)
        sys.stderr.write("Trying to close all open decks...\n")
        for _, _, d in decks:
            d.close()
        sys.stderr.write("All open decks closed.  Re-raising exception.\n")
        raise

    return decks

def makefacthighpriority(deck, factid):
    """
    Adds the HighPriority tag to the fact with id factid in deck.
    """
    deck.addTags([factid], "HighPriority")
    deck.reset()
    fact = deck.s.query(Fact).get(factid)
    fact.setModified(textChanged=True, deck=deck)
    deck.setModified()

def creatercfiletemp(rcfile):
    """
    Create a template rc file in the user's home directory.
    The rcfile argument is the path to the rcfile to create.
    """
    f = open(rcfile, 'w')
    f.write("""

# This is the rcfile for the anki_high_priority program.
# This file specifies the decks and field you want to use
# to search for words that you already know.

# This is a list of tuples.  The first value in the tuple is the
# deck name.  The second value in the tuple is the field name
# that will be used to match the word against. This is interpreted as
# valid python code, so please keep the syntax the same.
# The syntax should be:
#
# deck_info = [ ("Deck name.anki", "fieldname"), ... ]
#
# The decks must be in your ~/.anki/decks/ directory.
# Here is an example of how to use this:
#
# deck_info = [
#                 ("Core 2000 and 6000 Vocabulary and Sentences.anki", "Vocab"),
#                 ("Core 10k.anki", "Japanse Word"),
#                 ("Subs2srs.anki", "Unknown Word"),
#             ]
#
# Please make sure to remove any rows that are blank.

deck_info = [
                ("", ""),
                ("", ""),
            ]
"""


def main():

    homedir = os.path.expanduser("~")
    rcfile = os.path.expanduser("~/.anki_high_priority_rc.py")
    decks_dir = os.path.expanduser("~/.anki/decks/")

    # make sure the decks_dir exists
    if not os.path.isdir(decks_dir):
        sys.stderr.write("ERROR! Anki decks directory does not exist (%s)!\n" % decks_dir)
        sys.exit(1)

    # make sure the rc file exists, and create a template if it doesn't
    if not os.path.isfile(rcfile):
        try:
            creatercfiletemp(rcfile)
            sys.stderr.write("ERROR! RC file (%s) does not exist.\n" % rcfile)
            sys.stderr.write("A template has been created for you.\n")
            sys.stderr.write("Please edit the template and try running this program again.\n")
            sys.exit(1)
        except:
            sys.stderr.write("ERROR! RC file (%s) does not exist.\n" % rcfile)
            sys.stderr.write("There was an error with creating it:\n")
            raise


    # get the deck info from the config file
    try:
        config = imp.load_source('anki_high_priority_config',
            '/home/illabout/.anki_high_priority_rc.py')
    except:


    # make sure all of the decks exist
    for deckname, fieldname in deck_info:
        if not os.path.isfile(deckname):
            sys.stderr.write("ERROR! Deck \"%s\" does not exist.\n" % deckname)
            sys.exit(1)

    decks = opendecks(deck_info)

    taggedwords = []

    try:
        # go through all of the words and find out if they are in each deck
        for w in words:
            print("Search for word %s" % (w.decode('utf8')))
            for deckname, fieldname, d in decks:
                print("\tSearching in deck %s" % deckname)
                factlist = d.s.column0(sql_word_query,
                        field_value=w.decode('utf8'), field_name=fieldname)
                for factid in factlist:
                    makefacthighpriority(d, factid)
                    taggedwords.append(w)
                print("\t\tfactlist = %s" % factlist)

        print("Tagged words:")
        for f in taggedwords:
            print(f.decode('utf8'))
        nottaggedwords = [w for w in words if w not in taggedwords]
        print("Not Tagged words:")
        for f in nottaggedwords:
            print(f.decode('utf8'))

    finally:
        for _, _, d in decks:
            d.save()
            d.close()



if __name__ == '__main__':
    main()

