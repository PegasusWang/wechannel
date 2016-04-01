#!/usr/bin/env python
# -*- coding:utf-8 -*-

from . import _env
from tornado.web import RequestHandler, HTTPError
import mako.lookup
import mako.template
import traceback
from mako import exceptions
from os.path import join
from settings import TEMPLATE_PATH as TEMPLATE_PATH
from settings import settings

MAKO_LOOK_UP = mako.lookup.TemplateLookup(
    cache_enabled=False if settings['debug'] else True,
    module_directory=join(_env.PREFIX, '_templates'),
    directories=TEMPLATE_PATH,
    input_encoding='utf-8',
    output_encoding='utf-8',
    filesystem_checks=False,
    encoding_errors='replace',
)


class BaseHandler(RequestHandler):
    def initialize(self, lookup=MAKO_LOOK_UP):
        '''Set template lookup object, Defalut is MAKO_LOOK_UP'''
        self._lookup = lookup

    def render_string(self, filename, **kwargs):
        '''Override render_string to use mako template.
        Like tornado render_string method, this method
        also pass request handler environment to template engine.
        '''
        try:
            template = self._lookup.get_template(filename)
            env_kwargs = dict(
                handler=self,
                request=self.request,
                current_user=self.current_user,
                locale=self.locale,
                _=self.locale.translate,
                static_url=self.static_url,
                xsrf_form_html=self.xsrf_form_html,
                reverse_url=self.application.reverse_url,
            )
            env_kwargs.update(kwargs)
            return template.render(**env_kwargs)
        except Exception:
            traceback.print_exc()
            return exceptions.html_error_template().render()

    def render(self, filename, **kwargs):
        self.finish(self.render_string(filename, **kwargs))

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        elif status_code == 500:
            self.render('500.html')
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)


class PageNotFoundHandler(BaseHandler):
    def get(self):
        # then call write_error
        raise HTTPError(404)
