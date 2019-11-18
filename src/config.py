import os
import re
import json

def is_valid_filename(filename):
    illegal = re.compile('[\/:*?"<>|\t\n]')
    if illegal.findall(filename):
        return False
    else:
        return True



options = {
    "font-family": {
        "type": "select",
        "default": "sans-serif",
        "options": [
            "sans-serif",
            "serif",
            "monospace"
        ]
    },
    "font-size": {
        "type": "select",
        "default": "medium",
        "options": [
            "small",
            "medium",
            "large"
        ]
    },
    "menu": {
        "type": "select",
        "default": True,
        "options": [
            True,
            False
        ]
    }
}
default_setting = {
    "font-family": "sans-serif",
    "font-size": "medium",
    "menu": True
}

class Conf:
    def load(self, configpath):
        self.options = options
        if os.path.exists(configpath):
            with open('config.json', 'r') as f:
                config = json.load(f)
            result = {}
            for i,x in config.items():
                if self.check_valid_config(i, x):
                    result[i] = x
                else:
                    result[i] = self.options[i]['default']
        else:
            result = default_setting

        self.config = result
        self.reflect()
        return result
    
    def check_valid_config(self, key, value):
        if not self.options.get(key):
            return None

        if self.options[key]['type'] == 'select':
            return value in self.options[key]['options']
        
        if self.options[key]['type'] == 'input':
            if key == 'directory':
                return os.path.isdir(value)
            if key == 'default-file-name':
                return is_valid_filename(value) 
        return None

    def save(self):
        with open('config.json', 'w', encoding='utf8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def change(self, key, value):
        if self.check_valid_config(key, value):
            self.config[key] = value
            self.reflect()
            return True
        else:
            return False

    def reflect(self):
        self.defaultname = self.config['default-file-name'] if self.config.get('default-file-name') else 'untitled'
        self.defaultpath = self.config['directory'] if self.config.get('directory') else '.'
        self.defaultext = self.config['default-ext'] if self.config.get('default-ext') else '.stlf'

    def get(self):
        return self.config

    def get_options(self):
        return self.options

