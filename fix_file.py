with open('OpCore-Simplify-GUI.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复导入语句
content = content.replace('QListWidget, QStackedWidget', 'QListWidget, QListWidgetItem, QStackedWidget')

# 修复文档字符串中的无效字符
content = content.replace('"""验证必填字段（子类可重写', '"""Validate required fields (can be overridden by subclasses)')
content = content.replace('"""创建统一样式的按', '"""Create a button with unified style')

# 修复第948行的未终止字符串
content = content.replace('"自动检测完', '"Auto detection completed')

with open('OpCore-Simplify-GUI.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('文件修复完成')
