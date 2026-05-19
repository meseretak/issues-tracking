with open(r'frontend\index.html', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'id="modal-' in line:
            print(f'{idx+1}: {line.strip()}')
