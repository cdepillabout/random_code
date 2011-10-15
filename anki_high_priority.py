#!/usr/bin/env python2
# coding=utf-8

import os, sys

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

# This is a list of tuples.  The first value in the tuple is the
# deck name.  The second value in the tuple is the field name
# that we will use to match the word against.
deck_info = [("/home/illabout/.anki/decks/Core 2000 and 6000 Vocabulary and Senten.anki", "Vocab"),
             ("/home/illabout/.anki/decks/Core 10k.anki", "Vocab"),
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

def main():

    # make sure all of the decks exist
    for deckname, fieldname in deck_info:
        if not os.path.exists(deckname) or not os.path.isfile(deckname):
            sys.stderr.write("ERROR! Deck \"%s\" does not exist.\n" % deckname)

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



"""
    for f in words
    pass
"""

if __name__ == '__main__':
    main()

