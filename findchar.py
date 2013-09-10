from __future__ import print_function, unicode_literals
import sqlite3

def main():
    db = sqlite3.connect('data/unicode.db')
    try:
        while True:
            query = raw_input('>>> ').split()
            format = '''SELECT codepoints.id, desc, blocks.fullname
                        FROM codepoints, blocks WHERE blocks.id = bid
                        AND ({})'''.format(' OR '.join(['desc LIKE ?'] * len(query)))
            for row in db.execute(format, ['%{}%'.format(a) for a in query]):
                print('\t'.join(map(unicode, row)))
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == '__main__':
    main()
