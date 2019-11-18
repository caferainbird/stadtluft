#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import eel.__init__ as eel
from editor import Editor

app = Editor()


# eel interface

@eel.expose
def get_page(page_number):
    return app.file.get_page(page_number)

@eel.expose
def get_page_size():
    return app.file.current_page + 1

@eel.expose
def get_title():
    return app.file.title

@eel.expose
def open_new_file():
    app.file.set_new()
    return app.file.filename

@eel.expose
def save_text(text):
    return app.file.save_text(text)

@eel.expose
def change_file():
    if app.file.open_file():
        return {
                'title' : app.file.title,
                'filename' : app.file.filename,
                'current_page' : app.file.current_page,
                'fullpath' : app.file.get_fullpath(),
                'file_exsists' : os.path.isfile(app.file.get_fullpath()),
                }
    return False

@eel.expose
def rename_file(filename, overwrite=False):
    app.file.rename(filename, overwrite=False)
    return True

@eel.expose
def get_stats():
    return app.file.get_stats()

@eel.expose
def get_config():
    return app.config.get()

@eel.expose
def get_header():
    result = app.file.get_header()
    return result

@eel.expose
def change_fileinfo(title, author):
    result = app.file.change_header(title, author)
    return result

@eel.expose
def get_config_options():
    return app.config.get_options()

@eel.expose
def save_config(config):
    for i,x in config.items():
        app.config.change(i, x)
    app.config.save()
    return app.config.get()


@eel.expose
def preview():
    return app.file.preview()

@eel.expose
def export_file():
    return app.file.export()

# launch eel

eel.init('web')
eel.start('main.html', size=(500, 400), options={
    'port': 0,
    # 'chromeFlags': ['--apps-debug'], # enable debug
    })

