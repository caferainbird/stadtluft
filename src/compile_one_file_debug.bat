pyinstaller main.py --hidden-import bottle_websocket --add-data eel\eel.js;eel --add-data web;web --exclude numpy --exclude pandas --exclude win32com --exclude cryptography --onefile --icon=favicon.ico
