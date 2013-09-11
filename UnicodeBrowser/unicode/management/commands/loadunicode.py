from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError

from UnicodeBrowser.unicode.models import Block, CodePoint
from urllib2 import urlopen
from functools import partial
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import codecs
import re
import zipfile

__author__ = 'xiaomao'

auto_int = partial(int, base=0)
hex_int = partial(int, base=16)
re_block_name = re.compile(r'\((.*)\)')
re_code_point = re.compile(r'^([\da-f]{4,5})\t', re.I)


class Command(BaseCommand):
    args = ''
    help = 'Loads Unicode data from Unicode.org'

    def load_namelist(self):
        file = codecs.getreader('utf-8')(urlopen('http://www.unicode.org/Public/UNIDATA/NamesList.txt'))
        block_id = -1
        last_block = None
        last_char = None
        last_data = []
        chars = 0

        def save_last():
            if last_char is None:
                return
            description = '\n'.join(last_data)
            CodePoint.objects.create(id=last_char, description=description, block=last_block)
            del last_data[:]

        for line in file:
            line = line.strip('\n')
            code_point = re_code_point.match(line)
            if line.startswith('@@\t'):
                save_last()
                last_char = None
                # New block
                if last_block is not None:
                    self.stdout.write('Done block: {}, {:d} chars'.format(last_block.fullname, chars))
                start, name, end = line[3:].split('\t')
                redata = re_block_name.search(name)
                if redata:
                    name = redata.group(1)
                short = name.lower().replace(' ', '-')
                block_id += 1
                start = hex_int(start)
                end = hex_int(end)
                last_block = Block.objects.create(id=block_id, name=short, fullname=name, start=start, end=end)

                self.block_id_map[block_id] = short
                chars = 0
            elif code_point:
                save_last()
                last_char = hex_int(code_point.group(1))
                _, desc = line.split('\t')
                if not desc.startswith('<'):
                    last_data.append(desc)
                chars += 1
            elif line.startswith('\t='):
                last_data.append(line[3:])
        save_last()
        transaction.commit()

    def load_cjk(self):
        buffer = StringIO()
        self.download_to_buffer('http://www.unicode.org/Public/UNIDATA/Unihan.zip', buffer)
        count = [0]
        last_char = None
        definition = [None]
        mandarin = [None]
        block = [None]

        def save_last():
            if last_char is None:
                return
            text = []
            if definition[0] is not None:
                text.append('Character Meaning: ' + definition[0])
            if mandarin[0] is not None:
                text.append('Pronunciation: ' + mandarin[0])
            if block[0] is None or block[0].start > last_char or block[0].end < last_char:
                block[0] = Block.objects.get(start__lte=last_char, end__gte=last_char)
            text = '\n'.join(text)
            try:
                CodePoint.objects.create(id=last_char, description=text, block=block[0])
            except IntegrityError:
                point = CodePoint.objects.get(id=last_char)
                point.description = text
                point.save()

            definition[0] = None
            mandarin[0] = None
            count[0] += 1
            if count[0] & 0xFF == 0:
                self.stdout.write('Done CJK: {}'.format(count[0]), ending='\r')

        with zipfile.ZipFile(buffer) as zip:
            for line in codecs.getreader('utf-8')(zip.open('Unihan_Readings.txt')):
                if line.startswith('#'):
                    continue
                line = line.strip()
                if not line:
                    continue
                char, type, data = line.split('\t')
                char = hex_int(char[2:])
                if char != last_char:
                    save_last()
                    last_char = char
                if type == 'kDefinition':
                    definition[0] = data
                elif type == 'kMandarin':
                    mandarin[0] = data
        save_last()
        self.stdout.write('Done CJK: {}'.format(count[0]))

    def download_to_buffer(self, url, buffer):
        import time

        data = urlopen(url)
        size = int(data.info().getheaders('Content-Length')[0])
        self.stdout.write('Downloading {}, Size: {:,d}'.format(url.split('/')[-1], size))
        downloaded = 0
        block = 65536
        start = time.clock()
        while True:
            buf = data.read(block)
            if not buf:
                break
            downloaded += len(buf)
            buffer.write(buf)
            self.stdout.write('{:15,d} [{:6.2f}%] {:9.2f} kB/s'.format(
                              downloaded, downloaded * 100. / size,
                              downloaded / 1024. / (time.clock() - start)), ending='\r')
        self.stdout.write('{:15,d} [100.00%]'.format(downloaded))
        data.close()

    @transaction.commit_manually
    def handle(self, *args, **kwargs):
        self.block_id_map = {}
        Block.objects.all().delete()
        CodePoint.objects.all().delete()
        try:
            self.load_namelist()
            self.load_cjk()
        except Exception:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            raise
        else:
            transaction.commit()
