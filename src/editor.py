#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import datetime

from tkinter import filedialog
from tkinter import Tk

import header as hd
import generator as gen
from config import Conf
from util import resource_path

def replace(sentence, target='\n', to=''):
    if sentence is None:
        sentence = ''
    if type(sentence) is bool:
        sentence = ''
    replacer = re.compile(target)
    return replacer.sub(to, str(sentence))
    
def separate(text, split_string='\n+'):
    splitter = re.compile(split_string)
    res = splitter.split(str(text))
    return [x for x in res if len(x)]

def is_valid_filename(filename):
    illegal = re.compile('[\/:*?"<>|\t\n]')
    if illegal.findall(filename):
        return False
    else:
        return True


class Editor:
    defaultname = 'untitled'
    defaultpath = '.'
    defaultext = '.stlf'

    def __init__(self):
        self.config = Conf()
        self.config.load(resource_path('config.json'))
        self.file = Container(self.defaultname, self.defaultpath, self.defaultext)

class Container:
    def __init__(self, filename='untitled', filepath='.', fileext='.stlf'):
        self.defaultname = filename
        self.defaultpath = filepath
        self.defaultext = fileext
        self.defaultauthor = ''
        self.renderer = gen.Renderer()
        self.set_new()
    
    def get_default_name(self):
        max_retry = 100
        n = 0
        for i in range(max_retry):
            if i == 0:
                candidate = self.defaultname
            else:
                candidate = self.defaultname + '({})'.format(n)
            if os.path.isfile(candidate + self.defaultext):
                continue
            else:
                result = '/'.join([self.defaultpath, self.defaultname + self.defaultext])
                return result
                break
    
    def set_existing_file(self, fullpath):
        self.set_pathinfo(fullpath)
        if self.load():
            self.need_save_confirm = False
            return True
        else:
            return False

    def set_new(self):
        self.set_pathinfo(self.get_default_name())
        self.pages = {}
        self.need_save_confirm = True
        self.body = ''
        self.current_page = len(self.pages)
        self.set_fileinfo({'created_at' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    def set_fileinfo(self, dic):
        attrs = {
                'title': self.defaultname, 
                'author': self.defaultauthor,
                'created_at': '-',
                'last_updated': '-',
                }
        for key in attrs.keys():
            if dic.get(key):
                setattr(self, key, dic[key])
            else:
                setattr(self, key, attrs[key])
        self.set_header()

    def set_header(self):
        self.header = {
                'title': self.title,
                'author': self.author,
                'created_at': self.created_at,
                'last_updated': self.last_updated,
                }

    def get_header(self):
        return self.header

    def change_header(self, title, author):
        self.title = title if len(title) > 0  else 'untitled'
        self.author = author
        self.set_header()
        return self.get_header()

    def set_pathinfo(self, fullpath):
        path, ext = os.path.splitext(fullpath)
        path, name = os.path.split(path)
        self.set_path(path)
        self.set_name(name)
        self.set_ext(ext)

    def set_name(self, filename):
        self.filename = filename

    def set_path(self, filepath):
        self.path = filepath

    def set_ext(self, fileext):
        self.ext = fileext

    def get_fullpath(self):
        return '/'.join([self.path, self.filename + self.ext])

    def rename(self, new_name, overwrite=False):
        old_file = self.get_fullpath()
        new_file = '/'.join([self.path, new_name + self.ext])
        if os.path.isfile(new_file):
            if overwrite:
                os.remove(new_file)
                if not os.path.isfile(old_file):
                    # no need to rename existiong file.
                    with open(new_file, 'w'):
                        pass
                    return True
            else:
                return False
        self.set_name(new_name)
        os.path.rename(old_file, new_file)
        return True

    def open_file(self):
        candidate = ask_file_open(self.path)
        if(candidate):
            return self.set_existing_file(candidate)

    def load(self):
        file_path = self.get_fullpath()
        result = hd.read_file(file_path)
        if result is None:
            return False
        self.header = result[0]
        self.body = result[1]
        self.header['created_at'] = self.get_created_at(file_path)
        self.header['last_updated'] = self.get_updated_at(file_path)
        if not self.header.get('title'):
            self.header['title'] = self.filename
        self.set_fileinfo(self.header)
        self.pages = {i: x for i,x in enumerate(separate(self.body))}
        self.current_page = len(self.pages)
        return True

    def save(self):
        if self.need_save_confirm:
            # save confirmation
            if self.title:
                initial_name = self.title
            else:
                initial_name = 'untitled'

            candidate = ask_file_save(self.path, initial_name + '.stlf')

            if candidate:
                self.set_pathinfo(candidate)
                self.need_save_confirm = False
            else:
                return False
        self.last_updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.header['last_updated'] = self.last_updated
        self.set_header()
        hd.write_file(self.get_fullpath(), self.header, self.body)
        self.created_at = self.get_created_at(self.get_fullpath())
        self.set_header()
        return {
                'created_at' : self.created_at,
                'updated_at' : self.last_updated
                }


    def preview(self):
        self.renderer.set_header(**self.header)
        return self.renderer.preview(separate(self.body), len(self.body))

    def export(self):
        self.renderer.set_header(**self.header)
        candidate = ask_file_export(self.path, self.filename)

        if candidate:
            self.renderer.set_header(**self.header)
            if candidate.endswith('.md'):
                self.renderer.export_markdwon(separate(self.body), candidate)
            elif candidate.endswith('.htm') or candidate.endswith('.html'):
                self.renderer.export_html(separate(self.body), candidate)
            else:
                self.renderer.export_text(separate(self.body), candidate)
            return True

        return False

    def save_text(self, text, splitter='\n'):
        self.append(text, splitter)
        return self.save()
    
    def append(self, text, splitter='\n'):
        res = replace(text)
        self.pages[self.current_page] = res
        self.body = self.body + res + '\n'
        self.current_page = len(self.pages)

    def get_page(self, page_number):
        return self.pages.get(page_number)

    def get_stats(self):
        result = {
                'title' : self.title,
                'author' : self.author,
                'created_at': self.created_at,
                'last_updated': self.last_updated,
                'text_size' : len(self.body),
                'page_size' : len(self.pages),
                'fullpath' : self.get_fullpath(),
                }
        return result

    def get_created_at(self, file_path):
        created_at = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        return created_at.strftime('%Y-%m-%d %H:%M:%S')

    def get_updated_at(self, file_path):
        updated_at = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        return updated_at.strftime('%Y-%m-%d %H:%M:%S')


def ask_file_open(file_dir):
    root = Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    root.update()
    file_type = [
            ('stadtluft document', '*.stlf'),
            ('text file','*.txt *.text'),
            ('All files','*.*')
            ]
    result =  filedialog.askopenfilename(filetypes = file_type, initialdir = file_dir)
    root.destroy()
    return result

def ask_file_save(file_dir, initial_name):
    root = Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    root.update()
    file_type = [
            ('stadtluft document','*.stlf'),
            ('text file','*.txt *.text'), 
            ('All files','*.*'), 
        ]
    result =  filedialog.asksaveasfilename(
            initialfile = initial_name,
            initialdir = file_dir,
            title = 'Save as',
            filetypes = file_type,
            defaultextension='.stlf'
            )
    root.destroy()
    return result

def ask_file_export(file_dir, initial_name=''):
    if initial_name is None or len(str(initial_name)) == 0:
        initial_name = 'untitled'
    root = Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    root.update()
    file_type = [
            ('text file','*.txt *.text'), 
            ('markdown file','*.md'), 
            ('html file','*.html *.htm'), 
            ('All files','*.*'), 
        ]
    result =  filedialog.asksaveasfilename(
            initialfile = initial_name,
            initialdir = file_dir,
            title = 'Export as',
            filetypes = file_type,
            defaultextension='.txt'
            )
    root.destroy()
    return result


