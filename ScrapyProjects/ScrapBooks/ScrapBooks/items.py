#!/usr/bin/python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class ScrapbooksItem(Item):

    # define the fields for your item here like:
    # name = scrapy.Field()

    URL = Field()
    bookLink = Field()
    bookAuthor = Field()
    bookTitle = Field()
    bookCover = Field()
    bookImage = Field()


			