from django.db import models

__author__ = 'xiaomao'


class Block(models.Model):
    id = models.IntegerField('Block ID', primary_key=True)
    name = models.CharField('Block Simple Name', max_length=100, db_index=True)
    fullname = models.CharField('Block Name', max_length=100, db_index=True)
    start = models.IntegerField('CodePoint that starts this block', db_index=True)
    end = models.IntegerField('CodePoint that ends this block', db_index=True)


class CodePoint(models.Model):
    id = models.IntegerField('Unicode CodePoint', primary_key=True)
    description = models.TextField('Character Description', db_index=True)
    block = models.ForeignKey(Block, verbose_name='Block of this CodePoint', db_index=True)