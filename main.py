from flask import Flask, render_template, send_from_directory, request
from datetime import datetime
import os

app = Flask(__name__)

# 配置文件上传和下载目录
app.config['STATIC_FOLDER'] = 'static'
app.config['DOWNLOAD_FOLDER'] = os.path.join(app.config['STATIC_FOLDER'], 'files')

@app.route('/')
def home():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('home.html', current_time=current_time)

@app.route('/source')
def source():
    return render_template('source.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/wiki')
def wiki():
    import json
    wiki_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['STATIC_FOLDER'], 'wiki_links.json')
    with open(wiki_file, 'r', encoding='utf-8') as f:
        wiki_data = json.load(f)
    return render_template('wiki.html', wiki_data=wiki_data)
    
@app.route('/search/<query>')
def search(query):
    import json
    query = query.strip().lower()
    
    if not query:
        return render_template('search.html', query='', matched_results=[], empty_query=True)
    
    wiki_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['STATIC_FOLDER'], 'wiki_links.json')
    with open(wiki_file, 'r', encoding='utf-8') as f:
        wiki_data = json.load(f)
    
    matched_results = []
    for category in wiki_data.get('categories', []):
        for link in category.get('links', []):
            if query in link.get('title', '').lower() or query in link.get('description', '').lower():
                matched_results.append({
                    'category': category.get('name', ''),
                    'title': link.get('title', ''),
                    'url': link.get('url', ''),
                    'description': link.get('description', '')
                })
    
    return render_template('search.html', query=query, matched_results=matched_results, empty_query=False)

@app.route('/source/<filename>')
def secure_download(filename):
    """安全的文件下载路由，无需登录但增加了基本防护"""
    # 只允许下载特定文件类型
    allowed_extensions = {'.docx', '.pdf', '.zip', '.txt'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return "不允许下载该类型的文件", 403
    
    # 防止路径遍历攻击
    filename = os.path.basename(filename)
    
    # 检查文件是否存在
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return render_template('404.html'), 404
    
    # 文件存在时发送文件
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    """自定义404错误处理程序"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
    