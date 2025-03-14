# CPU Header Tool

一个用于解析和生成 CPU 头部的图形界面工具。

## 功能特点

- 现代化直观的图形用户界面
- 两个主要功能：
  1. 解析 CPU 头部：将十六进制格式转换为字段值
  2. 生成 CPU 头部：通过设置各个字段值生成十六进制格式
- 自动 CRC 计算
- 输入验证和错误处理
- 支持所有 CPU 头部字段

## 安装

1. 安装 Python 3.7 或更高版本（如果尚未安装）
2. 安装所需依赖项：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

运行应用程序：
```
python cpu_header_gui.py
```

### 解析 CPU 头部
1. 转到"Decode CPU Header"标签页
2. 输入空格分隔的十六进制 CPU 头部字符串
3. 点击"Decode Header"查看字段值

### 生成 CPU 头部
1. 转到"Generate CPU Header"标签页
2. 为所需字段输入值
3. 点击"Generate Header"获取十六进制输出
4. CRC 将自动计算

## 构建可执行文件

要创建独立的可执行文件：

1. 安装 PyInstaller：
   ```
   pip install pyinstaller
   ```

2. 创建可执行文件：
   ```
   pyinstaller --onefile --windowed --icon=app_icon.ico cpu_header_gui.py
   ```

可执行文件将在 `dist` 目录中创建。 