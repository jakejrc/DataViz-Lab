# DataViz Lab - 数据可视化课程辅助教学系统

为「Python 数据分析与可视化」课程设计的交互式教学平台。

## 功能模块

- **代码练习** — 4 章节 12 道练习题（Python基础、NumPy、Pandas、数据处理）
- **可视化实验室** — Matplotlib 6 种图表类型，支持参数实时调节
- **图表画廊** — 12 个预设图表（含 Seaborn 热力图、词云等）
- **数据清洗工作台** — CSV 上传，自动检测缺失值/重复值/异常值（IQR）

## 技术栈

- Python 3.6 + Flask
- Bootstrap 5 + CodeMirror
- Matplotlib（服务端渲染）
- NumPy / Pandas / Seaborn / WordCloud

## 启动

```bash
pip install flask numpy pandas matplotlib seaborn wordcloud jinja2
python app.py
```

浏览器打开 http://localhost:5000

## 课程信息

- 课程：Python 数据分析与可视化（64 学时，13 章）
- 教师：姜荣博士
- 学校：江苏工程职业技术学院
