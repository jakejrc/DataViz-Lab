# -*- coding: utf-8 -*-
"""
DataViz Lab - 数据可视化辅助教学系统
课程: Python数据分析与可视化
"""
import os
import sys
import json
import traceback
import io
import signal
import platform
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# ============ matplotlib 全局配置（只执行一次）============
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DengXian', 'KaiTi', 'FangSong']
matplotlib.rcParams['axes.unicode_minus'] = False

import numpy as np
import pandas as pd

# ============ 代码执行超时工具 ============
_EXEC_TIMEOUT = 10  # 秒

class _ExecTimeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise _ExecTimeout("代码执行超时（超过{}秒）".format(_EXEC_TIMEOUT))

def _run_with_timeout(code, global_vars, local_vars, timeout):
    """跨平台的超时执行方案"""
    if platform.system() != 'Windows':
        # Unix: 用 signal.SIGALRM
        old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(timeout)
        try:
            exec(code, global_vars, local_vars)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows: 无 SIGALRM，用线程 + 强制终止
        import threading
        result_holder = {'error': None}

        def target():
            try:
                exec(code, global_vars, local_vars)
            except Exception as e:
                result_holder['error'] = e

        t = threading.Thread(target=target)
        t.daemon = True
        t.start()
        t.join(timeout)
        if t.is_alive():
            # 线程仍在运行 → 超时
            raise _ExecTimeout("代码执行超时（超过{}秒）".format(timeout))
        if result_holder['error']:
            raise result_holder['error']

# ============ 安全的 builtins ============
_SAFE_BUILTINS = None

def _get_safe_builtins():
    """构建安全的 builtins：移除 os, sys, subprocess 等危险模块"""
    global _SAFE_BUILTINS
    if _SAFE_BUILTINS is not None:
        return _SAFE_BUILTINS
    import builtins
    safe = {}
    blocked = {'open', 'exit', 'quit', 'input', 'breakpoint',
               'compile', 'eval', 'exec', 'globals', 'locals',
               'memoryview', 'staticmethod', 'classmethod'}
    for name in dir(builtins):
        if name.startswith('_') or name in blocked:
            continue
        safe[name] = getattr(builtins, name)
    # 保留 print 和 type（教学必需）
    safe['print'] = builtins.print
    safe['type'] = builtins.type
    safe['range'] = builtins.range
    safe['len'] = builtins.len
    safe['int'] = builtins.int
    safe['float'] = builtins.float
    safe['str'] = builtins.str
    safe['list'] = builtins.list
    safe['dict'] = builtins.dict
    safe['tuple'] = builtins.tuple
    safe['set'] = builtins.set
    safe['bool'] = builtins.bool
    safe['sum'] = builtins.sum
    safe['max'] = builtins.max
    safe['min'] = builtins.min
    safe['sorted'] = builtins.sorted
    safe['enumerate'] = builtins.enumerate
    safe['zip'] = builtins.zip
    safe['map'] = builtins.map
    safe['filter'] = builtins.filter
    safe['isinstance'] = builtins.isinstance
    safe['hasattr'] = builtins.hasattr
    safe['getattr'] = builtins.getattr
    safe['setattr'] = builtins.setattr
    safe['abs'] = builtins.abs
    safe['round'] = builtins.round
    safe['pow'] = builtins.pow
    safe['divmod'] = builtins.divmod
    safe['chr'] = builtins.chr
    safe['ord'] = builtins.ord
    safe['hex'] = builtins.hex
    safe['oct'] = builtins.oct
    safe['bin'] = builtins.bin
    safe['repr'] = builtins.repr
    safe['id'] = builtins.id
    safe['hash'] = builtins.hash
    safe['callable'] = builtins.callable
    safe['iter'] = builtins.iter
    safe['next'] = builtins.next
    safe['reversed'] = builtins.reversed
    safe['slice'] = builtins.slice
    safe['object'] = builtins.object
    safe['super'] = builtins.super
    safe['property'] = builtins.property
    safe['Exception'] = builtins.Exception
    safe['ValueError'] = builtins.ValueError
    safe['TypeError'] = builtins.TypeError
    safe['KeyError'] = builtins.KeyError
    safe['IndexError'] = builtins.IndexError
    safe['AttributeError'] = builtins.AttributeError
    safe['ZeroDivisionError'] = builtins.ZeroDivisionError
    safe['RuntimeError'] = builtins.RuntimeError
    safe['StopIteration'] = builtins.StopIteration
    safe['NotImplementedError'] = builtins.NotImplementedError
    safe['__import__'] = builtins.__import__
    _SAFE_BUILTINS = {'__builtins__': safe}
    return _SAFE_BUILTINS

# ============ 首页 ============
@app.route('/')
def index():
    return render_template('index.html')

# ============ 代码练习 ============
@app.route('/exercises')
def exercises():
    return render_template('exercises.html')

# ============ Matplotlib 实验室 ============
@app.route('/matplotlib_lab')
def matplotlib_lab():
    return render_template('matplotlib_lab.html')

# ============ 图表画廊 ============
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

# ============ 数据清洗工作台 ============
@app.route('/data_clean')
def data_clean():
    return render_template('data_clean.html')

# ============ 代码执行 API ============
@app.route('/api/run_code', methods=['POST'])
def run_code():
    # BUG FIX #3: 空值检查
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'output': '', 'error': '请求数据为空，请发送 JSON 格式数据'})

    code = data.get('code', '')
    if not code.strip():
        return jsonify({'success': False, 'output': '', 'error': '未提供代码'})

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error

    result = {'success': True, 'output': '', 'error': '', 'has_plot': False, 'plot_data': ''}

    try:
        import matplotlib.pyplot as plt

        plt.close('all')

        # BUG FIX #4: 使用安全的 builtins，允许 import（教学需要）但限制危险内置函数
        safe_globals = _get_safe_builtins().copy()
        safe_globals.update({
            'np': np, 'numpy': np,
            'pd': pd, 'pandas': pd,
            'plt': plt, 'matplotlib': matplotlib,
        })

        local_vars = {}

        # BUG FIX #1: 带超时的代码执行
        _run_with_timeout(code, safe_globals, local_vars, _EXEC_TIMEOUT)

        if plt.get_fignums():
            import base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plot_data = base64.b64encode(buf.read()).decode('utf-8')
            result['has_plot'] = True
            result['plot_data'] = plot_data
            plt.close('all')

    except _ExecTimeout as e:
        result['success'] = False
        result['error'] = str(e)
    except Exception as e:
        result['success'] = False
        result['error'] = traceback.format_exc()

    result['output'] = redirected_output.getvalue()
    error_output = redirected_error.getvalue()
    if error_output and result['success']:
        result['output'] += error_output

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    return jsonify(result)

# ============ 练习题库 API ============
@app.route('/api/exercises/<chapter>')
def get_exercises(chapter):
    exercises_data = {
        'ch2': [
            {
                'id': 'ch2_1', 'title': 'Hello World',
                'desc': '输出 Hello, DataViz Lab!',
                'template': '# 请在下方编写代码\nprint("Hello, DataViz Lab!")',
                'difficulty': 1
            },
            {
                'id': 'ch2_2', 'title': '变量与数据类型',
                'desc': '创建变量并查看类型',
                'template': '# 创建变量并查看类型\nname = "Python"\nage = 30\nprint("name的类型:", type(name))\nprint("age的类型:", type(age))',
                'difficulty': 1
            },
            {
                'id': 'ch2_3', 'title': '列表操作',
                'desc': '创建列表，添加元素，删除元素',
                'template': '# 列表操作练习\nlst = [1, 2, 3, 4, 5]\nprint("原始列表:", lst)\n\n# 添加元素6\nlst.append(6)\nprint("添加6后:", lst)\n\n# 删除元素3\nlst.remove(3)\nprint("删除3后:", lst)',
                'difficulty': 2
            },
            {
                'id': 'ch2_4', 'title': '字典操作',
                'desc': '创建字典并进行增删改查',
                'template': '# 字典操作练习\nstudent = {"name": "张三", "age": 20, "score": 85}\nprint("原始字典:", student)\n\n# 添加新字段\nstudent["gender"] = "男"\n# 修改分数\nstudent["score"] = 90\n# 删除年龄\ndel student["age"]\nprint("操作后:", student)',
                'difficulty': 2
            },
            {
                'id': 'ch2_5', 'title': 'for循环',
                'desc': '用for循环计算1到100的和',
                'template': '# 计算1到100的和\ntotal = 0\nfor i in range(1, 101):\n    total += i\nprint("1到100的和:", total)',
                'difficulty': 2
            },
            {
                'id': 'ch2_6', 'title': '函数定义',
                'desc': '定义函数计算列表平均值',
                'template': '# 定义计算平均值的函数\ndef calc_mean(lst):\n    if not lst:\n        return 0\n    return sum(lst) / len(lst)\n\n# 测试\ndata = [85, 90, 78, 92, 88]\nprint("平均值:", calc_mean(data))',
                'difficulty': 3
            },
        ],
        'ch3': [
            {
                'id': 'ch3_1', 'title': '创建数组',
                'desc': '用numpy创建一维和二维数组',
                'template': 'import numpy as np\n\n# 创建一维数组\na = np.array([1, 2, 3, 4, 5])\nprint("一维数组:", a)\nprint("形状:", a.shape)\n\n# 创建二维数组\nb = np.array([[1,2,3],[4,5,6]])\nprint("二维数组:\\n", b)\nprint("形状:", b.shape)',
                'difficulty': 1
            },
            {
                'id': 'ch3_2', 'title': '数组运算',
                'desc': '演示广播机制',
                'template': 'import numpy as np\n\na = np.array([[1,2,3],[4,5,6]])\nb = np.array([10, 20, 30])\n\n# 广播机制：二维数组 + 一维数组\nresult = a + b\nprint("广播运算结果:\\n", result)',
                'difficulty': 2
            },
            {
                'id': 'ch3_3', 'title': '统计函数',
                'desc': '使用numpy统计函数分析数据',
                'template': 'import numpy as np\n\ndata = np.random.randint(0, 100, 20)\nprint("数据:", data)\nprint("均值:", np.mean(data))\nprint("标准差:", round(np.std(data), 2))\nprint("最大值:", np.max(data))\nprint("最小值:", np.min(data))\nprint("中位数:", np.median(data))',
                'difficulty': 2
            },
        ],
        'ch4': [
            {
                'id': 'ch4_1', 'title': 'Series创建',
                'desc': '创建和操作Pandas Series',
                'template': 'import pandas as pd\n\n# 创建Series\ns = pd.Series([85, 90, 78, 92, 88],\n              index=["语文","数学","英语","物理","化学"],\n              name="成绩")\nprint(s)\nprint("\\n均值:", s.mean())',
                'difficulty': 1
            },
            {
                'id': 'ch4_2', 'title': 'DataFrame操作',
                'desc': '创建DataFrame并进行增删改查',
                'template': 'import pandas as pd\n\n# 创建DataFrame\ndf = pd.DataFrame({\n    "姓名": ["张三", "李四", "王五"],\n    "语文": [85, 90, 78],\n    "数学": [92, 88, 95],\n    "英语": [78, 85, 82]\n})\nprint("原始数据:\\n", df)\n\n# 添加总分列\ndf["总分"] = df["语文"] + df["数学"] + df["英语"]\nprint("\\n添加总分:\\n", df)\n\n# 按总分排序\ndf_sorted = df.sort_values("总分", ascending=False)\nprint("\\n按总分排序:\\n", df_sorted)',
                'difficulty': 2
            },
        ],
        'ch5': [
            {
                'id': 'ch5_1', 'title': '缺失值处理',
                'desc': '检测并处理缺失值',
                'template': 'import pandas as pd\nimport numpy as np\n\n# 创建含缺失值的数据\ndf = pd.DataFrame({\n    "A": [1, 2, np.nan, 4, 5],\n    "B": [np.nan, 2, 3, np.nan, 5],\n    "C": [1, 2, 3, 4, 5]\n})\nprint("原始数据:\\n", df)\n\nprint("\\n缺失值统计:\\n", df.isnull().sum())\n\n# 均值填充\ndf_fill = df.fillna(df.mean())\nprint("\\n均值填充后:\\n", df_fill)',
                'difficulty': 2
            },
        ],
    }
    data = exercises_data.get(chapter, [])
    return jsonify(data)

# ============ Matplotlib 参数预设 ============
@app.route('/api/matplotlib_presets')
def matplotlib_presets():
    presets = {
        'scatter': {
            'name': '散点图',
            'code': 'import matplotlib.pyplot as plt\nimport numpy as np\n\nnp.random.seed(42)\nx = np.random.randn(50)\ny = 2 * x + np.random.randn(50)\n\nplt.figure(figsize=(8, 6))\nplt.scatter(x, y, c="{color}", s={size}, alpha={alpha}, marker="{marker}")\nplt.title("{title}", fontsize=14)\nplt.xlabel("X轴")\nplt.ylabel("Y轴")\nplt.grid({grid})\nplt.show()',
            'params': {
                'color': {'type': 'color', 'default': '#3498db'},
                'size': {'type': 'range', 'min': 10, 'max': 200, 'default': 50},
                'alpha': {'type': 'range', 'min': 0.1, 'max': 1.0, 'default': 0.7, 'step': 0.1},
                'marker': {'type': 'select', 'options': ['o', 's', '^', 'D', 'v', '*', 'p', 'h'], 'default': 'o'},
                'title': {'type': 'text', 'default': '散点图示例'},
                'grid': {'type': 'checkbox', 'default': True},
            }
        },
        'line': {
            'name': '折线图',
            'code': 'import matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 50)\ny1 = np.sin(x)\ny2 = np.cos(x)\n\nplt.figure(figsize=(8, 6))\nplt.plot(x, y1, color="{color1}", linestyle="{linestyle1}", linewidth={linewidth}, label="sin(x)")\nplt.plot(x, y2, color="{color2}", linestyle="{linestyle2}", linewidth={linewidth}, label="cos(x)")\nplt.title("{title}", fontsize=14)\nplt.xlabel("X")\nplt.ylabel("Y")\nplt.legend()\nplt.grid({grid})\nplt.show()',
            'params': {
                'color1': {'type': 'color', 'default': '#e74c3c'},
                'color2': {'type': 'color', 'default': '#3498db'},
                'linestyle1': {'type': 'select', 'options': ['-', '--', '-.', ':'], 'default': '-'},
                'linestyle2': {'type': 'select', 'options': ['-', '--', '-.', ':'], 'default': '--'},
                'linewidth': {'type': 'range', 'min': 1, 'max': 5, 'default': 2},
                'title': {'type': 'text', 'default': '正弦与余弦'},
                'grid': {'type': 'checkbox', 'default': True},
            }
        },
        'bar': {
            'name': '柱状图',
            'code': 'import matplotlib.pyplot as plt\nimport numpy as np\n\ncategories = ["Python", "Java", "C++", "JavaScript", "Go"]\nvalues = [85, 72, 65, 78, 55]\n\nplt.figure(figsize=(8, 6))\nplt.bar(categories, values, color="{color}", alpha={alpha}, edgecolor="white", linewidth=1.5)\nplt.title("{title}", fontsize=14)\nplt.xlabel("编程语言")\nplt.ylabel("热度指数")\nplt.grid(axis="{grid_axis}", alpha=0.3)\nplt.show()',
            'params': {
                'color': {'type': 'color', 'default': '#2ecc71'},
                'alpha': {'type': 'range', 'min': 0.3, 'max': 1.0, 'default': 0.8, 'step': 0.1},
                'title': {'type': 'text', 'default': '编程语言热度排行'},
                'grid_axis': {'type': 'select', 'options': ['y', 'x', 'both'], 'default': 'y'},
            }
        },
        'pie': {
            'name': '饼图',
            'code': 'import matplotlib.pyplot as plt\n\nlabels = ["Python", "Java", "C++", "JavaScript", "其他"]\nsizes = [35, 25, 15, 15, 10]\ncolors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]\nexplode = (0.05, 0, 0, 0, 0)\n\nplt.figure(figsize=(8, 6))\nplt.pie(sizes, explode=explode, labels=labels, colors=colors,\n        autopct="%1.1f%%", shadow={shadow}, startangle={startangle})\nplt.title("{title}", fontsize=14)\nplt.show()',
            'params': {
                'shadow': {'type': 'checkbox', 'default': True},
                'startangle': {'type': 'range', 'min': 0, 'max': 360, 'default': 90},
                'title': {'type': 'text', 'default': '编程语言市场份额'},
            }
        },
        'boxplot': {
            'name': '箱线图',
            'code': 'import matplotlib.pyplot as plt\nimport numpy as np\n\nnp.random.seed(42)\ndata = [np.random.normal(0, std, 100) for std in range(1, 4)]\n\nplt.figure(figsize=(8, 6))\nplt.boxplot(data, patch_artist={patch_artist},\n            boxprops=dict(facecolor="{box_color}", color="{line_color}"),\n            medianprops=dict(color="{median_color}", linewidth=2))\nplt.title("{title}", fontsize=14)\nplt.xlabel("组别")\nplt.ylabel("值")\nplt.grid({grid})\nplt.show()',
            'params': {
                'patch_artist': {'type': 'checkbox', 'default': True},
                'box_color': {'type': 'color', 'default': '#3498db'},
                'line_color': {'type': 'color', 'default': '#2c3e50'},
                'median_color': {'type': 'color', 'default': '#e74c3c'},
                'title': {'type': 'text', 'default': '箱线图示例'},
                'grid': {'type': 'checkbox', 'default': True},
            }
        },
        'heatmap': {
            'name': '热力图',
            'code': 'import matplotlib.pyplot as plt\nimport numpy as np\n\nnp.random.seed(42)\ndata = np.random.rand(6, 6)\nlabels = ["A", "B", "C", "D", "E", "F"]\n\nplt.figure(figsize=(8, 6))\nplt.imshow(data, cmap="{cmap}", interpolation="nearest")\nplt.colorbar()\nplt.xticks(range(6), labels)\nplt.yticks(range(6), labels)\nplt.title("{title}", fontsize=14)\n\nfor i in range(6):\n    for j in range(6):\n        plt.text(j, i, "%.2f" % data[i,j], ha="center", va="center", fontsize=10)\n\nplt.show()',
            'params': {
                'cmap': {'type': 'select', 'options': ['viridis', 'plasma', 'inferno', 'magma', 'Blues', 'Reds', 'Greens', 'YlOrRd', 'coolwarm'], 'default': 'viridis'},
                'title': {'type': 'text', 'default': '热力图示例'},
            }
        },
    }
    return jsonify(presets)

# ============ 数据集列表 ============
@app.route('/api/datasets')
def list_datasets():
    ds_dir = os.path.join(app.static_folder, 'datasets')
    if not os.path.exists(ds_dir):
        os.makedirs(ds_dir)
    files = [f for f in os.listdir(ds_dir) if f.endswith(('.csv', '.xlsx', '.xls'))]
    return jsonify(files)

if __name__ == '__main__':
    print("""
    ================================================
       DataViz Lab - 数据可视化辅助教学系统
       访问: http://localhost:5000
    ================================================
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
