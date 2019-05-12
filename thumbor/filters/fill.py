#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado import gen

from thumbor import Engine
from thumbor.filters import BaseFilter, filter_method
from thumbor.ext.filters import _fill


class Filter(BaseFilter):

    def get_median_color(self):
        mode, data = self.engine.image_data_as_rgb()
        r, g, b = _fill.apply(mode, data)
        return '%02x%02x%02x' % (r, g, b)

    @gen.coroutine
    @filter_method(r'[\w]+', BaseFilter.Boolean)
    def fill(self, details, color, fill_transparent=False):
        width, height = yield Engine.get_image_size(self, details)
        bx = details.request_parameters.width if details.request_parameters.width != 0 else width
        by = details.request_parameters.height if details.request_parameters.height != 0 else height

        # if the color is 'auto'
        # we will calculate the median color of
        # all the pixels in the image and return
        if color == 'auto':
            color = self.get_median_color()

        try:
            fill_image = yield Engine.gen_image(self, details, (bx, by), color)
        except (ValueError, RuntimeError):
            fill_image = yield Engine.gen_image(self, details, (bx, by), '#%s' % color)

        px = int((bx - width) / 2)  # top left
        py = int((by - height) / 2)

        mode, imgdata = yield Engine.paste(self, details, fill_image, (px, py), merge=fill_transparent)
        yield Engine.set_image_data(self, details, imgdata)
        # yield Engine.set_image_data(self, details, imgdata)
        # self.engine.image = self.fill_engine.image
