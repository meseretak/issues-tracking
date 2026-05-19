with open(r'frontend\app.js', encoding='utf-8') as f:
    content = f.read()

content = content.replace(r'\`', '`')
content = content.replace(r'\${', '${')

with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed syntax escaping in JS.')
