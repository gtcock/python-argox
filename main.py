import os
import requests
from flask import Flask, send_file
from subprocess import Popen, PIPE, STDOUT
import threading

app = Flask(__name__)
port = int(os.getenv('PORT', 3000))

files_to_download_and_execute = [
    {
        'url': 'https://github.com/gtcock/demo/releases/download/cock/index.html',
        'filename': 'index.html',
    },
    {
        'url': 'https://github.com/gtcock/demo/releases/download/cock/server',
        'filename': 'server',
    },
    {
        'url': 'https://github.com/gtcock/demo/releases/download/cock/web',
        'filename': 'web',
    },
    {
        'url': 'https://github.com/gtcock/demo/releases/download/cock/config.json',
        'filename': 'config.json',
    },    
    {
        'url': 'https://github.com/gtcock/demo/releases/download/cock/bot',
        'filename': 'bot',
    },
    {
        'url': 'https://raw.githubusercontent.com/gtcock/demo/refs/heads/main/bingo.sh',
        'filename': 'bingo.sh',
    },
]

def check_file_exists(filename):
    """检查文件是否存在并且大小大于0"""
    if os.path.exists(filename):
        if os.path.getsize(filename) > 0:
            print(f'File {filename} already exists and is not empty, skipping download')
            return True
        else:
            print(f'File {filename} exists but is empty, will download again')
            return False
    return False

def download_file(url, filename):
    """如果文件不存在或为空才下载"""
    if check_file_exists(filename):
        return True
        
    print(f'Downloading file from {url}...')
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'Successfully downloaded {filename}')
        return True
    except requests.RequestException as error:
        print(f'Failed to download {filename}: {error}')
        return False

def give_executable_permission(filename):
    """只给存在的文件添加执行权限"""
    if os.path.exists(filename):
        print(f'Giving executable permission to {filename}')
        try:
            os.chmod(filename, 0o755)
            return True
        except Exception as error:
            print(f'Failed to give executable permission to {filename}: {error}')
            return False
    return False

def execute_script_in_background(script):
    """只执行存在的脚本"""
    if not os.path.exists(script):
        print(f'Script {script} does not exist, skipping execution')
        return False

    def run_script():
        process = Popen(['bash', script], stdout=PIPE, stderr=STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        process.stdout.close()
        process.wait()

    print(f'Executing script {script} in background...')
    thread = threading.Thread(target=run_script)
    thread.start()
    return True

def download_and_execute_files():
    success = True
    
    # 下载所有文件
    for file in files_to_download_and_execute:
        if not download_file(file['url'], file['filename']):
            success = False

    if not success:
        print('Some files failed to download')
        return False

    # 给需要的文件添加执行权限
    executable_files = ['bingo.sh', 'server', 'web', 'bot']
    for filename in executable_files:
        if not give_executable_permission(filename):
            success = False

    if not success:
        print('Failed to set executable permissions')
        return False

    # 执行脚本
    if os.path.exists('bingo.sh'):
        execute_script_in_background('bingo.sh')
    else:
        print('bingo.sh not found, skipping execution')
        success = False

    return success

@app.route('/')
def index():
    try:
        if os.path.exists('index.html'):
            return send_file('index.html')
        else:
            return 'index.html not found', 404
    except Exception as e:
        return f'Error loading index.html: {e}', 500

if __name__ == '__main__':
    if download_and_execute_files():
        app.run(host='0.0.0.0', port=port)
    else:
        print('There was a problem downloading and executing the files.')
