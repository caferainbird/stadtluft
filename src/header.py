#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import io

re_start = re.compile('^/\*')
re_end = re.compile('\*/')
re_blank_line = re.compile('^ *\n')
re_comment = re.compile('#.*$')
re_operator = re.compile(' *: *')
re_header = re.compile('^/\*[^/]*\*/')

variables = [
        'title',
        'author',
        'created_at',
        'last_updated',
        ]

def split_header(string):
    if re_header.match(string):
        header = re_header.findall(string)[0]
        body = re_header.sub('', string)
    else:
        header = ''
        body = string
    return header, body.strip()+'\n'

def parse_header(header):
    buf = io.StringIO(header)
    res = [x.strip() for x in buf.readlines()]
    return {x.split(':')[0]:str(x.split(':')[1]).strip() for x in res if len(x.split(':')) == 2 and x.split(':')[0] in variables }

def read_header(f):
    header, body = split_header(f.read())
    return parse_header(header),body 

def write_file(filename, header, body):
    with open(filename, 'w', encoding='utf8', errors='ignore') as f:
        f.write(convert_header(header))
        f.write(body)

def convert_header(header):
    if len(header):
        res = '/*\n'
        res += '*' * 15 + ' FILE INFORMATION ' + '*' * 15 + '\n'
        
        for key,value in header.items():
            res += str(key) + ': ' + str(value) + '\n'
        res += '*' * 50 + '\n'
        res += '*/\n\n'
        return res
    else:
        return ''

def read_file(filename):
    for codec in ['utf8', 'sjis']:
        try:
            with open(filename, 'r', encoding=codec) as f:
                return read_header(f)
        except: 
            pass

    return None


