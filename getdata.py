from __future__ import print_function, unicode_literals
import io, re, os
import sqlite3
import codecs
import zipfile
from functools import partial
try:
    from urllib.request import urlopen,  urlretrieve
except ImportError:
    from urllib2 import urlopen
    from urllib import urlretrieve
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

uniopen = partial(io.open, encoding='utf-8')
autoint = partial(int, base=0)
hexint = partial(int, base=16)
intmap = {}
reblockname = re.compile(r'\((.*)\)')
recodepoint = re.compile(r'^([\da-f]{4,5})\t', re.I)

def create_blocks(db):
    db.execute('''CREATE TABLE IF NOT EXISTS blocks (
                    id INTEGER PRIMARY KEY,
                    name TEXT, fullname TEXT, start INTEGER, end INTEGER
                  )''')
    db.execute('''CREATE UNIQUE INDEX IF NOT EXISTS blocks_name ON blocks (name)''')
    db.execute('''CREATE UNIQUE INDEX IF NOT EXISTS blocks_fullname ON blocks (fullname)''')
    db.execute('''CREATE INDEX IF NOT EXISTS blocks_range ON blocks (start, end)''')

def create_codetable(db):
    db.execute('''CREATE TABLE IF NOT EXISTS codepoints (
                    id INTEGER PRIMARY KEY, desc TEXT,
                    bid INTEGER, block TEXT)''')
    db.execute('''CREATE INDEX IF NOT EXISTS cp_desc ON codepoints (desc)''')
    db.execute('''CREATE INDEX IF NOT EXISTS cp_bid ON codepoints (bid)''')

def load_namelist(db):
    file = codecs.getreader('utf-8')(urlopen('http://www.unicode.org/Public/UNIDATA/NamesList.txt'))
    blockid = -1
    lastblockname = None
    lastch = None
    lastdata = []
    chars = 0
    def savelast():
        if lastch is None:
            return
        db.execute('''INSERT OR REPLACE INTO codepoints(id, desc, bid, block)
                      VALUES (?, ?, ?, ?)''',
                   (lastch, '\n'.join(lastdata), blockid, intmap[blockid]))
        del lastdata[:]
    for line in file:
        line = line.strip('\n')
        codepoint = recodepoint.match(line)
        if line.startswith('@@\t'):
            # New block
            if lastblockname is not None:
                print('Done block: {}, {:d} chars'.format(lastblockname, chars))
            start, name, end = line[3:].split('\t')
            redata = reblockname.search(name)
            if redata:
                name = redata.group(1)
            short = name.lower().replace(' ', '-')
            blockid += 1
            try:
                db.execute('''INSERT OR REPLACE INTO blocks (id, name, fullname, start, end)
                            VALUES (?, ?, ?, ?, ?)''', (blockid, short,
                                name, hexint(start), hexint(end)))
            except sqlite3.IntegrityError:
                for key in intmap:
                    if intmap[key] == short:
                        blockid = key
            else:
                intmap[blockid] = short
            lastblockname = name
            chars = 0
        elif codepoint:
            savelast()
            lastch = hexint(codepoint.group(1))
            _, desc = line.split('\t')
            if not desc.startswith('<'):
                lastdata.append(desc)
            chars += 1
        elif line.startswith('\t='):
            lastdata.append(line[3:])
    savelast()
    db.commit()

def load_cjk(db):
    buffer = BytesIO()
    download_to_buffer('http://www.unicode.org/Public/UNIDATA/Unihan.zip', buffer)
    count = 0
    with zipfile.ZipFile(buffer) as zip:
        for line in codecs.getreader('utf-8')(zip.open('Unihan_Readings.txt')):
            if line.startswith('#'):
                continue
            line = line.strip()
            if not line:
                continue
            char, type, data = line.split('\t')
            if type == 'kDefinition':
                char = hexint(char[2:])
                id, block = db.execute('''SELECT id, name FROM blocks WHERE ?
                                            BETWEEN start AND end''', (char,)).fetchone()
                db.execute('''INSERT OR REPLACE INTO codepoints(id, desc, bid, block)
                                VALUES (?, ?, ?, ?)''', (char,
                            'Character Meaning: ' + data, id, block))
                count += 1
                if count & 0xFF == 0:
                    print('Done CJK: {}'.format(count), end='\r')
    db.commit()
    print('Done CJK: {}'.format(count))

def download_to_buffer(url, buffer):
    data = urlopen(url)
    size = int(data.info().getheaders('Content-Length')[0])
    print('Downloading {}, Size: {:,d}'.format(url.split('/')[-1], size))
    downloaded = 0
    block = 8192
    while True:
        buf = data.read(block)
        if not buf:
            break
        downloaded += len(buf)
        buffer.write(buf)
        print('{:15,d} [{:6.2f}%]'.format(downloaded, downloaded * 100. / size), end='\r')
    print('{:15,d} [100.00%]'.format(downloaded))
    data.close()

def main():
    import time
    db = sqlite3.connect('data/unicode.db')
    create_blocks(db)
    create_codetable(db)
    load_namelist(db)
    load_cjk(db)

if __name__ == '__main__':
    main()
