import os
JS = os.path.join('issues tracking', 'frontend', 'app.js')
js = open(JS, encoding='utf-8').read()
print('Before:', js.count(chr(10)), 'lines')
print('Writing missing page functions...')
