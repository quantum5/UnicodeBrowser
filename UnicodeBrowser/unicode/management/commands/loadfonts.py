from django.contrib.staticfiles import finders
from django.core.management import BaseCommand
from django.db import transaction
from UnicodeBrowser.unicode.models import Font, Block

__author__ = 'xiaomao'


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


class Command(BaseCommand):
    args = ''
    help = 'Load my fonts'

    @transaction.commit_manually
    def handle(self, *args, **kwargs):
        try:
            for font, blocks in self.fontdata.iteritems():
                path = 'font/{}.woff'.format(font)
                if finders.find(path) is None:
                    self.stdout.write('Font not found: {}'.format(font))
                    continue
                obj = get_or_none(Font, short=font.lower())
                if obj is not None:
                    for block in obj.block_set.all():
                        block.font = None
                        block.save()
                    obj.delete()
                font = Font.objects.create(short=font.lower(), name=font, file=path)
                for block in blocks:
                    short = block.lower().replace(' ', '-')
                    object = get_or_none(Block, name=short)
                    if object is None:
                        self.stdout.write('Block not found: {}'.format(block))
                        continue
                    object.font = font
                    object.save()
                self.stdout.write('Added font: {}'.format(font.name))
        except Exception:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            raise
        else:
            transaction.commit()

    fontdata = {
        'Symbola': [
            'Superscripts and Subscripts',
            'Currency Symbols',
            'Combining Diacritical Marks for Symbols',
            'Letterlike Symbols',
            'Number Forms',
            'Arrows',
            'Mathematical Operators',
            'Miscellaneous Technical',
            'Control Pictures',
            'Optical Character Recognition',
            'Box Drawing',
            'Block Elements',
            'Geometric Shapes',
            'Miscellaneous Symbols',
            'Dingbats',
            'Miscellaneous Mathematical Symbols-A',
            'Supplemental Arrows-A',
            'Braille Patterns',
            'Supplemental Arrows-B',
            'Miscellaneous Mathematical Symbols-B',
            'Supplemental Mathematical Operators',
            'Miscellaneous Symbols and Arrows',
            'Supplemental Punctuation',
            'Yijing Hexagram Symbols',
            'Combining Half Marks',
            'Specials',
            'Byzantine Musical Symbols',
            'Musical Symbols',
            'Ancient Greek Musical Notation',
            'Tai Xuan Jing Symbols',
            'Counting Rod Numerals',
            'Mathematical Alphanumeric Symbols',
            'Mahjong Tiles',
            'Domino Tiles',
            'Playing Cards',
            'Miscellaneous Symbols And Pictographs',
            'Emoticons',
            'Transport And Map Symbols',
            'Alchemical Symbols',
        ],
        'Aegyptus': [
            'Egyptian Hieroglyphs',
            'Coptic',
            'Meroitic Hieroglyphs',
            'Meroitic Cursive',
        ]
    }
