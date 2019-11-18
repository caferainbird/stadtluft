#!/usr/bin/python
# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader
from util import resource_path

class Renderer:
    def __init__(self, path='./', temp_path='preview/template.html', css_path='preview/template.css', lang='en'):
        self.lang = lang
        self.env = Environment(loader=FileSystemLoader(path, encoding='utf8'))
        self.template = self.env.get_template(temp_path)
        self.set_css(css_path)
        self.save_path = resource_path('web/preview.html')

    def set_header(self, title=None, author=None, created_at=None, last_updated=None):
        self.title = title
        self.author = author
        self.created_at = created_at
        self.last_updated = last_updated
    
    def set_css(self, css_path):
        self.css_path = resource_path(css_path)
        with open(css_path, 'r') as f:
            self.css = f.read()

    def render(self, texts, path, text_size=0):
        html = self.template.render(
                {
                    'title': self.title, 
                    'author': self.author,
                    'texts': texts,
                    'text_size': text_size,
                    'created_at' : self.created_at,
                    'last_updated' : self.last_updated,
                    'lang' : self.lang,
                    'css' : self.css,
                    })
        with open(path, 'wb') as f:
            f.write(html.encode('utf-8'))
        return path

    def preview(self, texts, text_size):
        return self.render(texts, self.save_path, text_size)

    def export_html(self, texts, export_path):
        return self.render(texts, export_path)

    def export_markdwon(self, texts, export_path):
        out = ''
        # header
        header = ''
        if not self.created_at == '-':
            header += '{}<br>'.format(self.created_at)
        if not self.last_updated == '-':
            header += 'Last updated: {}'.format(self.last_updated)
        if header:
            out += '<div class="header" style="text-align:right;">{}</div>\n'.format(header)
        # title
        if self.title is not None:
            out += '# {}\n\n'.format(self.title)
        # author
        if self.author is not None:
            out += '<div class="author" style="text-align:right;">{}</div>\n\n'.format(self.author)
        # body
        with open(export_path, 'w') as f:
            f.write(out + '\n\n'.join(texts))

        return export_path

    def export_text(self, texts, export_path):
        out = ''
        if self.title is not None:
            out += '{}\n\n'.format(self.title)
        if self.author is not None:
            out += '{}\n\n'.format(self.author)
        with open(export_path, 'w') as f:
            f.write(out + '\n'.join(texts))
        return export_path

