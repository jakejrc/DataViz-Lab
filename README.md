# DataViz Lab 📊

**数据可视化课程辅助教学系统** — 为《Python 数据分析与可视化》课程量身打造的交互式在线教学平台。

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/jakejrc/DataViz-Lab?label=v1.0)](https://github.com/jakejrc/DataViz-Lab/releases/tag/v1.0)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org)

---

## 📸 界面预览

> **注**：界面截图将在后续更新中添加，当前可本地运行查看效果。

### 首页
- 功能导航：代码练习、可视化实验室、图表画廊、数据清洗工作台
- 课程信息展示

### 代码练习
- 4 章节 12 道练习题
- 内置代码编辑器（CodeMirror）
- 一键运行，实时查看输出

### 可视化实验室
- 6 种 Matplotlib 图表类型
- 实时参数调节（滑块、颜色选择器、下拉框）
- 代码与图表同步更新

### 图表画廊
- 12 个预设图表（含 Seaborn 高级图表、词云）
- 一键生成示例

### 数据清洗工作台
- CSV 文件上传
- 自动检测缺失值、重复值、异常值
- 数据预览与下载

---

## ✨ 功能模块

### 1. 代码练习（12 道）
- **第 2 章：Python 基础**（6 题）
  - Hello World、变量与类型、条件判断、循环、函数、综合练习
- **第 3 章：NumPy**（2 题）
  - 数组创建与操作、广播运算
- **第 4 章：Pandas**（2 题）
  - Series 与 DataFrame、数据排序与统计
- **第 5 章：数据处理**（2 题）
  - 缺失值处理、数据合并

每道题包含：
- 📝 题目描述与提示
- 💻 可编辑代码编辑器（CodeMirror）
- ▶️ 一键运行，实时查看输出
- ✅ 参考答案

### 2. 可视化实验室
**Matplotlib 实时调节**（6 种图表类型）：
- 📈 折线图 — 调节线型、颜色、标记、线宽
- 📊 柱状图 — 调节颜色、透明度、误差线
- 🟠 散点图 — 调节大小、颜色、透明度、第三维
- 📦 箱线图 — 调节配色、网格、填充样式
- 🍩 饼图 — 调节颜色、爆炸效果、百分比显示
- 🗺️ 热力图 — 调节配色方案、标注、颜色条

**特点**：
- 滑块/颜色选择器/下拉框实时调节参数
- 代码与图表同步更新
- 支持中文字体渲染

### 3. 图表画廊（12 个预设）
- Matplotlib 基础图表（折线、柱状、散点、饼图、直方图、箱线图）
- Seaborn 高级图表（热力图、回归图、分类散点图、小提琴图、分布图）
- 词云生成（中文支持）

### 4. 数据清洗工作台
- 📤 上传 CSV 文件
- 🔍 自动检测：
  - 缺失值（NaN）及比例
  - 重复行及比例
  - 异常值（IQR 方法，检测所有数值列）
- 📊 数据预览（前 10 行）
- 📥 下载清洗后的数据

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.6 + Flask |
| 前端 | Bootstrap 5、CodeMirror 5、jQuery |
| 可视化 | Matplotlib、Seaborn、WordCloud |
| 数据处理 | NumPy、Pandas |
| 安全 | 沙箱执行（超时保护、受限 builtins） |

---

## 🚀 快速开始

### 本地部署

#### 安装依赖
```bash
pip install flask numpy pandas matplotlib seaborn wordcloud jinja2
```

#### 启动服务
```bash
python app.py
```

浏览器打开：**http://localhost:5000**

#### 使用 Docker（推荐）
```bash
docker run -p 5000:5000 jakejrc/dataviz-lab:v1.0
```

---

## 📚 课程信息

- **课程名称**：Python 数据分析与可视化
- **学时**：64 学时
- **章节**：13 章
- **教师**：姜荣昌 博士
- **学校**：江苏工程职业技术学院

---

## 🔒 安全特性

- ✅ 代码执行超时保护（10 秒）
- ✅ 受限 builtins（禁止 os、sys、subprocess 等危险操作）
- ✅ 沙箱环境执行（隔离全局命名空间）
- ✅ 中文字体自动配置（SimHei、Microsoft YaHei 等）

---

## 📁 项目结构

```
DataViz-Lab/
├── app.py                  # Flask 主应用
├── Dockerfile              # Docker 镜像定义
├── run_dataviz_lab.bat    # Windows 启动脚本
├── static/
│   ├── css/style.css      # 样式文件
│   └── datasets/          # 示例数据集
├── templates/
│   ├── index.html         # 首页
│   ├── exercises.html     # 代码练习
│   ├── matplotlib_lab.html # Matplotlib 实验室
│   ├── gallery.html       # 图表画廊
│   └── data_clean.html    # 数据清洗
└── README.md
```

---

## 🐳 Docker 部署

### 拉取镜像
```bash
docker pull jakejrc/dataviz-lab:v1.0
```

### 运行容器
```bash
docker run -d -p 5000:5000 --name dataviz-lab jakejrc/dataviz-lab:v1.0
```

### 访问应用
浏览器打开：http://localhost:5000

---

## 📝 更新日志

### v1.0（2026-05-01）
- ✨ 初始发布
- ✅ 12 道代码练习题（Python、NumPy、Pandas）
- ✅ Matplotlib 可视化实验室（6 种图表）
- ✅ 图表画廊（12 个预设）
- ✅ 数据清洗工作台（CSV 上传 + 自动检测）
- ✅ 安全沙箱执行环境
- ✅ 中文 Matplotlib 渲染支持

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。

---

**🔗 GitHub**: https://github.com/jakejrc/DataViz-Lab  
**🐳 Docker Hub**: https://hub.docker.com/r/jakejrc/dataviz-lab
