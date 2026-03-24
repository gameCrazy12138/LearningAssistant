"""
学习管理助手 v3.0 - 完全重写版
基于用户需求重新设计，实现所有核心功能

功能清单：
1. 任务详情弹窗 - 完整信息展示
2. 进度历史记录 - 每次更新记录
3. 任务筛选功能 - 按状态筛选
4. 统计看板 - 数据可视化
5. 树型任务手动设置 - 无子任务时手动输入

作者：AI Assistant
日期：2026-03-24
版本：v3.0.0
"""

import kivy
kivy.require('2.0.0')

# 🔥 先导入必要模块
import os
import sys
import platform
from datetime import datetime, date

# 🔥 导入字体注册（在 UI 组件之前）
from kivy.core.text import LabelBase

try:
    if platform.system() == 'Windows':
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'msyh.ttc')
        if os.path.exists(font_path):
            LabelBase.register(name='', fn_regular=font_path)
            print(f"[OK] 中文字体已注册：{font_path}")
except Exception as e:
    print(f"[WARN] 字体注册失败：{e}")

# 🔥 导入 Kivy 组件
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import json


# ============================================================================
# 数据模型层
# ============================================================================

class Task:
    """
    任务数据模型
    
    数据结构：
    {
        'id': int,              # 唯一标识
        'title': str,           # 任务标题
        'description': str,     # 任务描述
        'task_type': str,       # 任务类型（'数值型'/'树型'）
        'target_value': float,  # 目标值
        'unit': str,            # 单位
        'current_value': float, # 当前值
        'sub_tasks': list,      # 子任务列表（仅树型任务）
        'status': str,          # 状态（未开始/进行中/已完成）
        'progress': float,      # 进度百分比 0-100
        'progress_history': list,  # 进度历史记录
        'created_at': str,      # 创建时间
        'updated_at': str,      # 更新时间
    }
    """
    
    def __init__(self, task_data=None):
        if task_data:
            self.data = task_data
        else:
            self.data = {}
    
    @property
    def id(self):
        return self.data.get('id', 0)
    
    @property
    def title(self):
        return self.data.get('title', '')
    
    @property
    def progress(self):
        return self.data.get('progress', 0)
    
    @property
    def status(self):
        return self.data.get('status', '未开始')
    
    @property
    def task_type(self):
        return self.data.get('task_type', '数值型')
    
    def get_progress_history(self):
        """获取进度历史记录"""
        return self.data.get('progress_history', [])
    
    def add_history_record(self, value, note=""):
        """添加进度历史记录"""
        if 'progress_history' not in self.data:
            self.data['progress_history'] = []
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'note': note,
            'progress': self.progress
        }
        self.data['progress_history'].append(record)


class TaskManager:
    """
    任务管理器 - 负责所有任务数据的操作
    
    功能：
    - 从 JSON 文件加载任务
    - 保存任务到 JSON 文件
    - 创建新任务（支持数值型和树型）
    - 更新任务进度（累加方式，记录历史）
    - 删除任务
    - 修改任务信息
    - 任务筛选（按状态）
    - 统计数据分析
    """
    
    def __init__(self, data_file="data/tasks.json"):
        """
        初始化任务管理器
        
        参数:
            data_file: JSON 数据文件路径
        """
        # 🔥 PyInstaller 打包后路径处理
        if getattr(sys, 'frozen', False):
            # 打包后的环境：使用 exe 所在目录
            self.data_file = os.path.join(os.path.dirname(sys.executable), data_file)
        else:
            # 开发环境：使用 src 目录
            self.data_file = os.path.join(os.path.dirname(__file__), data_file)
        
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """从 JSON 文件加载所有任务"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                self.tasks = tasks_data
            print(f"[OK] 已加载 {len(self.tasks)} 个任务")
        except FileNotFoundError:
            self.tasks = []
            print("[INFO] 未找到任务文件，将创建新文件")
        except Exception as e:
            self.tasks = []
            print(f"[ERROR] 加载失败：{e}")
    
    def save_tasks(self):
        """保存所有任务到 JSON 文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            print("[OK] 任务已保存")
        except Exception as e:
            print(f"[ERROR] 保存失败：{e}")
    
    def create_task(self, title, description="", task_type="数值型", 
                    target_value=100.0, unit="%", target_progress=100.0):
        """
        创建新任务
        
        参数:
            title: 任务标题
            description: 任务描述
            task_type: 任务类型（'数值型' 或 '树型'）
            target_value: 目标值
            unit: 单位
            target_progress: 目标进度百分比（默认 100%）
        
        返回:
            创建的任务字典
        """
        # 生成唯一 ID
        task_id = max([t.get('id', 0) for t in self.tasks] + [0]) + 1
        
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'task_type': task_type,
            'target_value': target_value,
            'unit': unit,
            'current_value': 0.0,
            'sub_tasks': [],  # 树型任务的子任务列表
            'status': '未开始',
            'progress': 0,
            'progress_history': [],  # 进度历史记录
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'target_progress': target_progress,  # 目标进度百分比
        }
        
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def update_progress(self, task_id, increment_value, note=""):
        """
        更新任务进度（累加方式，记录历史）
        
        参数:
            task_id: 任务 ID
            increment_value: 增加的数值（正数）
            note: 备注信息
        
        返回:
            bool: 成功返回 True，失败返回 False
        """
        # 🔥 使用递归查找任务（支持主任务和子任务）
        task = self._find_task_by_id(self.tasks, task_id)
        
        if not task:
            print(f"[ERROR] 任务 ID {task_id} 不存在")
            return False
        
        # 🔥 检查：树型主任务有子任务时，不允许手动增加进度
        # 注意：子任务没有 'task_type' 字段或为 None，所以不会命中这个检查
        if task.get('task_type') == '树型' and task.get('sub_tasks'):
            print(f"[ERROR] 树型主任务有子任务，不能手动增加进度")
            print(f"     提示：请通过更新子任务进度来自动计算主任务进度")
            return False
        
        # 保存旧值用于比较
        old_value = task.get('current_value', 0)
        new_value = old_value + increment_value
        task['current_value'] = new_value
        
        # 根据目标值和目标进度自动计算当前进度百分比（限制最大值 100%）
        target_value = task.get('target_value', 100)
        target_progress = task.get('target_progress', 100)  # 目标进度百分比（默认 100%）
        old_progress = task.get('progress', 0)
        task['progress'] = (new_value / target_value) * target_progress if target_value > 0 else 0
        task['progress'] = min(task['progress'], 100.0)  # 限制最大值为 100%
        
        # 记录进度历史
        self._add_progress_history(task, increment_value, note)
        
        # 更新状态
        if task['progress'] >= 100:
            task['status'] = '已完成'
        elif task['progress'] > 0:
            task['status'] = '进行中'
        
        task['updated_at'] = datetime.now().isoformat()
        
        # 🔥 如果是子任务，更新后需要重新计算所有上级任务的进度（在保存之前）
        if 'task_type' not in task or task.get('task_type') is None:
            # 这是子任务，递归更新所有上级任务的进度
            self._update_all_parent_progress(self.tasks, task_id)
        
        # 保存数据（包括主任务的新进度）
        self.save_tasks()
        
        print(f"[OK] 任务进度已更新：+{increment_value}{task.get('unit', '')}")
        print(f"     当前值：{old_value:.1f} → {new_value:.1f}/{target_value}{task.get('unit', '')}")
        print(f"     进度：{old_progress:.1f}% → {task['progress']:.1f}%")
        
        return True
    
    def _update_all_parent_progress(self, tasks, child_id):
        """
        递归更新所有上级任务的进度（从叶子节点向上）
        
        参数:
            tasks: 任务列表
            child_id: 子任务 ID
        """
        for task in tasks:
            if 'sub_tasks' in task:
                # 检查是否包含该子任务
                for st in task['sub_tasks']:
                    if st['id'] == child_id:
                        # 找到直接父任务，重新计算进度
                        self._calculate_tree_task_progress(task)
                        # 继续向上更新
                        self._update_all_parent_progress(self.tasks, task['id'])
                        return
                # 递归查找子任务
                self._update_all_parent_progress(task['sub_tasks'], child_id)
    
    def _calculate_tree_task_progress(self, tree_task):
        """
        计算树型主任务的进度（从子任务平均进度）
        
        参数:
            tree_task: 树型主任务
        """
        sub_tasks = tree_task.get('sub_tasks', [])
        if not sub_tasks:
            return
        
        # 计算子任务的平均进度
        total_progress = sum(st.get('progress', 0) for st in sub_tasks)
        avg_progress = total_progress / len(sub_tasks)
        
        # 更新主任务进度
        tree_task['progress'] = avg_progress
        
        # 根据进度反推当前值
        target = tree_task.get('target_value', 100)
        tree_task['current_value'] = (avg_progress / 100.0) * target
        
        # 更新状态
        if avg_progress >= 100:
            tree_task['status'] = '已完成'
        elif avg_progress > 0:
            tree_task['status'] = '进行中'
        else:
            tree_task['status'] = '未开始'
        
        tree_task['updated_at'] = datetime.now().isoformat()
        
        print(f"[OK] 树型主任务进度已自动计算：{avg_progress:.1f}%")
        # 🔥 注意：不在这里调用 save_tasks()，由 update_progress() 统一保存
    
    def _add_progress_history(self, task, value, note=""):
        """
        添加进度历史记录
        
        参数:
            task: 任务字典
            value: 增加的数值
            note: 备注信息
        """
        if 'progress_history' not in task:
            task['progress_history'] = []
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'note': note,
            'progress': task['progress'],
            'current_value': task['current_value']
        }
        task['progress_history'].append(record)
    
    def set_manual_progress(self, task_id, manual_progress, note=""):
        """
        手动设置任务进度（用于树型任务无子任务时）
        
        参数:
            task_id: 任务 ID
            manual_progress: 手动设置的进度百分比（0-100）
            note: 备注信息
        
        返回:
            bool: 成功返回 True，失败返回 False
        """
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if not task:
            print(f"[ERROR] 任务 ID {task_id} 不存在")
            return False
        
        # 限制进度范围
        manual_progress = max(0, min(100, manual_progress))
        
        old_progress = task.get('progress', 0)
        task['progress'] = manual_progress
        
        # 根据进度反推当前值
        target = task.get('target_value', 100)
        task['current_value'] = (manual_progress / 100.0) * target
        
        # 记录进度历史
        self._add_progress_history(task, manual_progress - old_progress, f"手动设置：{note}")
        
        # 更新状态
        if task['progress'] >= 100:
            task['status'] = '已完成'
        elif task['progress'] > 0:
            task['status'] = '进行中'
        else:
            task['status'] = '未开始'
        
        task['updated_at'] = datetime.now().isoformat()
        self.save_tasks()
        
        print(f"[OK] 任务进度已手动设置为：{manual_progress}%")
        return True
    
    def delete_task(self, task_id):
        """
        删除任务（包括子任务）
        
        参数:
            task_id: 任务 ID
        
        返回:
            bool: 成功返回 True，失败返回 False
        """
        # 查找并删除主任务
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                self.save_tasks()
                print(f"[OK] 任务已删除：{task.get('title', '')}")
                return True
        
        # 查找并删除子任务
        for task in self.tasks:
            if task.get('task_type') == '树型':
                for i, sub_task in enumerate(task.get('sub_tasks', [])):
                    if sub_task['id'] == task_id:
                        del task['sub_tasks'][i]
                        task['updated_at'] = datetime.now().isoformat()
                        self.save_tasks()
                        print(f"[OK] 子任务已删除")
                        return True
        
        print(f"[ERROR] 任务 ID {task_id} 不存在")
        return False
    
    def update_task(self, task_id, **kwargs):
        """
        更新任务信息
        
        参数:
            task_id: 任务 ID
            **kwargs: 要更新的字段
        
        返回:
            bool: 成功返回 True，失败返回 False
        """
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            for key, value in kwargs.items():
                if key in task:
                    task[key] = value
            task['updated_at'] = datetime.now().isoformat()
            self.save_tasks()
            return True
        return False
    
    def get_filtered_tasks(self, status_filter="全部"):
        """
        按状态筛选任务
        
        参数:
            status_filter: 筛选条件（全部/未开始/进行中/已完成）
        
        返回:
            筛选后的任务列表
        """
        if status_filter == "全部":
            return self.tasks
        
        return [t for t in self.tasks if t.get('status') == status_filter]
    
    def get_statistics(self):
        """
        获取统计数据
        
        返回:
            统计字典
        """
        stats = {
            'total': len(self.tasks),
            '未开始': sum(1 for t in self.tasks if t.get('status') == '未开始'),
            '进行中': sum(1 for t in self.tasks if t.get('status') == '进行中'),
            '已完成': sum(1 for t in self.tasks if t.get('status') == '已完成'),
        }
        return stats
    
    def add_sub_task(self, parent_id, sub_task_data):
        """
        添加子任务（支持多层嵌套）
        
        参数:
            parent_id: 父任务 ID（可以是主任务或子任务）
            sub_task_data: 子任务数据字典
        
        返回:
            bool: 成功返回 True，失败返回 False
        """
        # 🔥 递归查找父任务（支持在主任务或子任务中查找）
        parent = self._find_task_by_id(self.tasks, parent_id)
        if not parent:
            print(f"[ERROR] 父任务 ID {parent_id} 不存在")
            return False
        
        # 🔥 检查：只有树型任务才能添加子任务
        # 注意：主任务有 task_type='树型'，子任务没有 task_type 字段
        if parent.get('task_type') != '树型' and 'task_type' in parent:
            print(f"[ERROR] 只有树型任务才能添加子任务")
            return False
        
        # 🔥 生成全局唯一的子任务 ID（使用更大的数字范围）
        # 子任务 ID = 父任务 ID * 1000 + 子任务序号
        if 'sub_tasks' not in parent:
            parent['sub_tasks'] = []
        
        # 🔥 清除子任务的 task_type 字段（用于 update_progress 判断）
        if 'task_type' in sub_task_data:
            del sub_task_data['task_type']
        
        sub_task_index = len(parent['sub_tasks']) + 1
        sub_task_data['id'] = parent['id'] * 1000 + sub_task_index
        sub_task_data['progress_history'] = []
        sub_task_data['created_at'] = datetime.now().isoformat()
        sub_task_data['updated_at'] = datetime.now().isoformat()
        
        parent['sub_tasks'].append(sub_task_data)
        parent['updated_at'] = datetime.now().isoformat()
        
        self.save_tasks()
        print(f"[OK] 子任务已添加：{sub_task_data.get('title', '')} (ID={sub_task_data['id']})")
        return True
    
    def _find_task_by_id(self, tasks, task_id):
        """
        递归查找任务（支持在主任务或子任务中查找）
        
        参数:
            tasks: 任务列表
            task_id: 任务 ID
        
        返回:
            任务对象，如果没找到返回 None
        """
        for task in tasks:
            if task.get('id') == task_id:
                return task
            # 🔥 递归查找子任务
            if 'sub_tasks' in task:
                found = self._find_task_by_id(task['sub_tasks'], task_id)
                if found:
                    return found
        return None
    
    def get_task_by_id(self, task_id):
        """
        根据 ID 获取任务（包括子任务）
        
        参数:
            task_id: 任务 ID
        
        返回:
            任务字典，不存在返回 None
        """
        # 先在主任务中查找
        for task in self.tasks:
            if task['id'] == task_id:
                return task
            
            # 在子任务中查找
            if 'sub_tasks' in task:
                for sub_task in task['sub_tasks']:
                    if sub_task['id'] == task_id:
                        return sub_task
        
        return None


# ============================================================================
# UI 组件层
# ============================================================================

class TaskCard(BoxLayout):
    """
    任务卡片 - 显示单个任务的 UI 组件
    
    布局结构（从上到下）：
    1. 标题栏：展开按钮 + 标题 + 状态标签
    2. 描述区域（如果有描述）
    3. 类型标签
    4. 进度条和进度百分比
    5. 功能按钮：查看详情 + 更新进度 + 添加子任务 + 编辑 + 删除
    6. 子任务容器（如果是树型任务且展开）
    """
    
    def __init__(self, task_data, on_view_details=None, on_update_progress=None, 
                 on_delete=None, on_add_subtask=None, on_edit=None, level=0, **kwargs):
        super().__init__(**kwargs)
        
        # 🔥 垂直布局，弹性高度
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [6, 6, 6, 6]  # 🔥 第三次优化（从 8 减到 6）
        self.spacing = 6  # 🔥 第三次优化（从 8 减到 6）
        
        # 🔥 保存层级信息（用于动态调整按钮大小）
        self.level = level
        
        # 保存回调函数
        self.task_data = task_data
        self.on_view_details_callback = on_view_details
        self.on_update_progress_callback = on_update_progress
        self.on_delete_callback = on_delete
        self.on_add_subtask_callback = on_add_subtask
        self.on_edit_callback = on_edit
        
        # 🔥 根据层级动态调整背景颜色和阴影
        # level 0: 浅灰色，level 1: 浅蓝色，level 2: 更浅蓝色，level 3+: 淡紫色
        if level == 0:
            bg_color = (0.97, 0.97, 0.97, 1)  # 主任务：浅灰色
            border_color = (0.4, 0.47, 0.92, 1)  # 蓝色边框
        elif level == 1:
            bg_color = (0.93, 0.96, 1.0, 1)  # 一级子任务：浅蓝色
            border_color = (0.2, 0.6, 1.0, 1)  # 亮蓝色边框
        elif level == 2:
            bg_color = (0.88, 0.94, 1.0, 1)  # 二级子任务：更浅蓝色
            border_color = (0.1, 0.5, 0.9, 1)  # 深蓝色边框
        else:
            bg_color = (0.94, 0.91, 1.0, 1)  # 三级及以上：淡紫色
            border_color = (0.6, 0.4, 0.9, 1)  # 紫色边框
        
        # 绘制背景、边框和阴影
        with self.canvas.before:
            # 🔥 阴影效果（深灰色，半透明）
            Color(0.7, 0.7, 0.7, 0.3)
            self.shadow_rect = RoundedRectangle(
                pos=(self.pos[0] + 3, self.pos[1] - 3),
                size=self.size,
                radius=[12, 12, 12, 12]
            )
            # 背景颜色
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12, 12, 12, 12])
            # 左侧边框颜色
            Color(*border_color)
            self.border_rect = RoundedRectangle(pos=(self.pos[0], self.pos[1]), size=(5, self.size[1]), radius=[3, 3, 3, 3])
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        # 🔥 关键：强制布局立即计算高度
        self.bind(minimum_height=self.setter('height'))
        
        self._build_ui()
    
    def _update_graphics(self, instance, value):
        """更新图形位置（包括背景和阴影）"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        
        if hasattr(self, 'border_rect'):
            self.border_rect.pos = (self.pos[0], self.pos[1])
            self.border_rect.size = (5, self.size[1])
        
        # 🔥 更新阴影位置
        if hasattr(self, 'shadow_rect'):
            self.shadow_rect.pos = (self.pos[0] + 3, self.pos[1] - 3)
            self.shadow_rect.size = self.size
    
    def _update_status_bg(self, instance, value):
        """更新状态标签背景位置"""
        if hasattr(self, 'status_bg_rect'):
            self.status_bg_rect.pos = instance.pos
            self.status_bg_rect.size = instance.size
    
    def _build_ui(self):
        """构建 UI - 彻底修复布局重叠问题"""
        
        # 1. 标题栏 - 使用 FloatLayout 避免挤压
        header = BoxLayout(
            size_hint_y=None,
            height=35,  # 🔥 第三次优化（从 38 减到 35）
            spacing=8,
            padding=[6, 3, 6, 3]  # 🔥 进一步减小内边距
        )
        
        # 展开按钮（仅树型任务且有子任务）
        # 🔥 主任务有 task_type='树型'，子任务没有 task_type 字段但有 sub_tasks
        is_tree_task = self.task_data.get('task_type') == '树型' or ('task_type' not in self.task_data and self.task_data.get('sub_tasks'))
        
        if is_tree_task and self.task_data.get('sub_tasks'):
            self.btn_expand = Button(
                text='▶',
                size_hint_x=None,
                width=30,  # 🔥 第三次优化（从 32 减到 30）
                font_size='17sp'  # 🔥 调大字体（从 15sp 到 17sp，+2sp）
            )
            self.btn_expand.bind(on_press=self._toggle_subtasks)
            header.add_widget(self.btn_expand)
        
        # 标题 - 使用弹性空间
        title_container = BoxLayout(size_hint_x=1.0)  # 占据剩余空间
        title = Label(
            text=self.task_data['title'],
            halign='left',
            valign='middle',
            font_size='15sp',  # 🔥 调大字体（从 14sp 到 15sp）
            bold=True,
            color=(0, 0, 0, 1),  # 🔥 黑色文字
            shorten=True,
            shorten_from='right'
        )
        title.bind(size=title.setter('text_size'))
        title_container.add_widget(title)
        header.add_widget(title_container)
        
        # 状态标签 - 固定宽度
        status = self.task_data.get('status', '未开始')
        status_colors = {
            '未开始': (0.6, 0.6, 0.6, 1),
            '进行中': (0.2, 0.6, 1, 1),
            '已完成': (0.2, 0.8, 0.2, 1)
        }
        color = status_colors.get(status, (0.6, 0.6, 0.6, 1))
        
        lbl_status = Label(
            text=status,
            size_hint_x=None,
            width=80,  # 🔥 第三次优化（从 85 减到 80）
            bold=True,
            font_size='12sp',  # 🔥 调大字体（从 11sp 到 12sp）
            halign='center',
            valign='middle'
        )
        
        with lbl_status.canvas.before:
            Color(*color)
            self.status_bg_rect = RoundedRectangle(pos=lbl_status.pos, size=lbl_status.size, radius=[6, 6, 6, 6])
        
        lbl_status.bind(pos=self._update_status_bg, size=self._update_status_bg)
        header.add_widget(lbl_status)
        
        self.add_widget(header)
        
        # 2. 描述（如果有）- 单独容器
        if self.task_data.get('description'):
            desc_container = BoxLayout(
                size_hint_y=None,
                height=30,  # 🔥 第三次优化（从 32 减到 30）
                padding=[6, 3, 6, 3]  # 🔥 进一步减小内边距
            )
            desc = Label(
                text=self.task_data['description'],
                halign='left',
                valign='top',
                font_size='12sp',  # 🔥 调大字体（从 11sp 到 12sp）
                color=(0, 0, 0, 1),  # 🔥 黑色文字
                shorten=True,
                shorten_from='right'
            )
            desc.bind(size=desc.setter('text_size'))
            desc_container.add_widget(desc)
            self.add_widget(desc_container)
        
        # 3. 类型标签 - 单独容器
        type_container = BoxLayout(
            size_hint_y=None,
            height=20,  # 🔥 第三次优化（从 22 减到 20）
            padding=[6, 0, 6, 0]  # 🔥 进一步减小内边距
        )
        type_label = Label(
            text=f"[{self.task_data.get('task_type', '数值型')}]",
            halign='left',
            valign='middle',
            font_size='10sp',  # 🔥 调大字体（从 9sp 到 10sp）
            color=(0, 0, 0, 1)  # 🔥 黑色文字
        )
        type_container.add_widget(type_label)
        self.add_widget(type_container)
        
        # 4. 进度信息 - 单独容器
        progress_container = BoxLayout(
            size_hint_y=None,
            height=25,  # 🔥 第三次优化（从 27 减到 25）
            padding=[6, 3, 6, 3],  # 🔥 进一步减小内边距
            spacing=6
        )
        progress = self.task_data.get('progress', 0)
        lbl_progress = Label(
            text=f"进度：{progress:.1f}%",
            halign='left',
            valign='middle',
            font_size='12sp',  # 🔥 调大字体（从 11sp 到 12sp）
            bold=True,
            color=(0, 0, 0, 1)  # 🔥 黑色文字
        )
        progress_container.add_widget(lbl_progress)
        self.add_widget(progress_container)
        
        # 5. 功能按钮 - 使用 GridLayout 确保平均分配
        # 🔥 根据任务层级动态调整按钮数量和大小
        is_tree_task = self.task_data.get('task_type') == '树型' or 'task_type' not in self.task_data
        num_buttons = 5 if is_tree_task else 4
        
        # 🔥 计算层级（根据左侧缩进判断）
        # 主任务：level=0，子任务：level=1,2,3...
        level = getattr(self, 'level', 0)
        
        # 🔥 根据层级动态调整按钮宽度（整体 +5px）
        # level 0: 125px, level 1: 105px, level 2: 85px, level 3+: 75px
        if level == 0:
            btn_width = 125  # 原 120
        elif level == 1:
            btn_width = 105  # 原 100
        elif level == 2:
            btn_width = 85   # 原 80
        else:
            btn_width = 75   # 原 70
        
        btn_grid = GridLayout(
            cols=num_buttons,
            size_hint_y=None,
            height=40,  # 🔥 第三次优化（从 44 减到 40）
            spacing=6,
            padding=[6, 6, 6, 6]
        )
        
        # 查看详情按钮
        btn_view = Button(
            text='查看详情',
            font_size='14sp',  # 🔥 增加字体（从 13sp 到 14sp）
            size_hint_x=None,
            width=btn_width
        )
        btn_view.bind(on_press=lambda x: self.on_view_details_callback(self.task_data) if self.on_view_details_callback else None)
        btn_grid.add_widget(btn_view)
        
        # 更新进度按钮
        btn_update = Button(
            text='+ 进度',
            font_size='14sp',  # 🔥 增加字体
            size_hint_x=None,
            width=btn_width
        )
        btn_update.bind(on_press=lambda x: self.on_update_progress_callback(self.task_data) if self.on_update_progress_callback else None)
        btn_grid.add_widget(btn_update)
        
        # 🔥 添加子任务按钮（仅树型任务，包括主任务和子任务）
        # 注意：主任务有 task_type='树型'，子任务没有 task_type 字段
        if is_tree_task:
            btn_add = Button(
                text='+ 子任务',
                font_size='14sp',  # 🔥 增加字体
                size_hint_x=None,
                width=btn_width
            )
            btn_add.bind(on_press=lambda x: self.on_add_subtask_callback(self.task_data) if self.on_add_subtask_callback else None)
            btn_grid.add_widget(btn_add)
        
        # 编辑按钮
        btn_edit = Button(
            text='编辑',
            font_size='14sp',  # 🔥 增加字体
            size_hint_x=None,
            width=btn_width
        )
        btn_edit.bind(on_press=lambda x: self.on_edit_callback(self.task_data) if self.on_edit_callback else None)
        btn_grid.add_widget(btn_edit)
        
        # 删除按钮 - 红色背景
        btn_delete = Button(
            text='删除',
            font_size='14sp',  # 🔥 增加字体
            size_hint_x=None,
            width=btn_width
        )
        
        def update_delete_bg(instance, value):
            if hasattr(instance, 'delete_bg_rect'):
                instance.delete_bg_rect.pos = instance.pos
                instance.delete_bg_rect.size = instance.size
        
        with btn_delete.canvas.before:
            Color(1, 0.4, 0.4, 1)
            btn_delete.delete_bg_rect = RoundedRectangle(pos=btn_delete.pos, size=btn_delete.size, radius=[8, 8, 8, 8])
        
        btn_delete.bind(pos=update_delete_bg, size=update_delete_bg)
        btn_delete.bind(on_press=lambda x: self.on_delete_callback(self.task_data['id']) if self.on_delete_callback else None)
        btn_grid.add_widget(btn_delete)
        
        self.add_widget(btn_grid)
        
        # 6. 子任务容器（仅树型任务，包括主任务和子任务）
        # 🔥 主任务有 task_type='树型'，子任务没有 task_type 字段但有 sub_tasks
        is_tree_task = self.task_data.get('task_type') == '树型' or ('task_type' not in self.task_data and self.task_data.get('sub_tasks'))
        
        if is_tree_task:
            self.subtask_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=0,
                padding=[25, 6, 6, 6],  # 🔥 第三次优化（从 30,8,8,8 减到 25,6,6,6）
                spacing=6  # 🔥 第三次优化（从 8 减到 6）
            )
            self.subtask_container.bind(minimum_height=self.subtask_container.setter('height'))
            self.add_widget(self.subtask_container)
            
            self.expanded = False
            self.sub_task_cards = []
            
            # 初始加载子任务
            self.refresh_subtasks()
    
    def _toggle_subtasks(self, instance):
        """切换子任务显示/隐藏"""
        self.expanded = not self.expanded
        instance.text = '▼' if self.expanded else '▶'
        
        # 🔥 记录展开状态到主屏幕
        if hasattr(self, 'on_view_details_callback') and self.on_view_details_callback:
            # 找到 MainScreen 实例
            main_screen = None
            widget = self
            while widget:
                if widget.__class__.__name__ == 'MainScreen':
                    main_screen = widget
                    break
                widget = widget.parent
            
            if main_screen and hasattr(main_screen, '_expanded_task_ids'):
                if self.expanded:
                    main_screen._expanded_task_ids.add(self.task_data['id'])
                else:
                    main_screen._expanded_task_ids.discard(self.task_data['id'])
        
        # 🔥 刷新子任务显示（强制重新计算高度）
        self.refresh_subtasks()
        
        # 🔥 强制触发父容器重新布局
        if hasattr(self, 'parent') and self.parent:
            self.parent.height = self.parent.minimum_height
    
    def refresh_subtasks(self):
        """刷新子任务显示"""
        if not hasattr(self, 'subtask_container') or self.subtask_container is None:
            return
        
        # 清空现有子任务卡片
        self.subtask_container.clear_widgets()
        self.sub_task_cards = []
        
        if not self.expanded:
            self.subtask_container.height = 0
            return
        
        # 获取子任务列表
        sub_tasks = self.task_data.get('sub_tasks', [])
        
        # 计算总高度
        total_height = 10  # padding
        
        for sub_task in sub_tasks:
            # 🔥 计算子任务层级：父任务 level + 1
            sub_level = self.level + 1
            
            # 创建子任务卡片
            sub_card = TaskCard(
                task_data=sub_task,
                on_view_details=self.on_view_details_callback,
                on_update_progress=self.on_update_progress_callback,
                on_delete=self.on_delete_callback,
                on_add_subtask=self.on_add_subtask_callback,
                on_edit=self.on_edit_callback,
                level=sub_level  # 🔥 传递层级信息
            )
            self.subtask_container.add_widget(sub_card)
            self.sub_task_cards.append(sub_card)
            total_height += sub_card.height + 5  # height + spacing
        
        total_height += 5  # bottom padding
        self.subtask_container.height = total_height


class MainScreen(BoxLayout):
    """
    主屏幕 - 应用的主要界面
    
    包含：
    - 顶部工具栏（新增任务、刷新、筛选、统计）
    - 任务列表区域
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()
        self.orientation = 'vertical'
        self.current_filter = "全部"
        self._expanded_task_ids = set()  # 🔥 记录展开的树型主任务 ID
        self._build_ui()
    
    def _build_ui(self):
        """构建 UI - 优化布局"""
        # 1. 顶部工具栏 - 优化高度和间距
        toolbar = BoxLayout(
            size_hint_y=None, 
            height=60,  # 增加高度
            spacing=15,  # 增加间距
            padding=[15, 10]
        )
        
        # 新增任务按钮 - 增大尺寸
        btn_add = Button(
            text='+ 新增任务',
            font_size='16sp',
            bold=True
        )
        btn_add.bind(on_press=self.show_add_task_dialog)
        toolbar.add_widget(btn_add)
        
        # 刷新按钮
        btn_refresh = Button(
            text='刷新',
            font_size='15sp'
        )
        btn_refresh.bind(on_press=lambda x: self.refresh_tasks())
        toolbar.add_widget(btn_refresh)
        
        # 筛选区域 - 增加宽度
        filter_layout = BoxLayout(
            size_hint_x=None, 
            width=320,  # 增加宽度容纳更多按钮
            spacing=8
        )
        filter_label = Label(
            text='筛选:',
            size_hint_x=None,
            width=60,
            bold=True,
            font_size='15sp'
        )
        filter_layout.add_widget(filter_label)
        
        # 筛选按钮组 - 统一样式
        self.btn_filter_all = Button(text='全部', font_size='14sp')
        self.btn_filter_all.bind(on_press=lambda x: self.set_filter("全部"))
        filter_layout.add_widget(self.btn_filter_all)
        
        self.btn_filter_pending = Button(text='未开始', font_size='14sp')
        self.btn_filter_pending.bind(on_press=lambda x: self.set_filter("未开始"))
        filter_layout.add_widget(self.btn_filter_pending)
        
        self.btn_filter_progress = Button(text='进行中', font_size='14sp')
        self.btn_filter_progress.bind(on_press=lambda x: self.set_filter("进行中"))
        filter_layout.add_widget(self.btn_filter_progress)
        
        self.btn_filter_completed = Button(text='已完成', font_size='14sp')
        self.btn_filter_completed.bind(on_press=lambda x: self.set_filter("已完成"))
        filter_layout.add_widget(self.btn_filter_completed)
        
        # 初始化选中状态
        self.btn_filter_all.bold = True
        
        toolbar.add_widget(filter_layout)
        
        # 统计看板按钮 - 增大尺寸
        btn_stats = Button(
            text='统计',
            font_size='16sp',
            bold=True
        )
        btn_stats.bind(on_press=lambda x: self.show_statistics())
        toolbar.add_widget(btn_stats)
        
        self.add_widget(toolbar)
        
        # 2. 任务列表区域 - 优化边距
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.tasks_container = GridLayout(
            cols=1,
            size_hint_y=None,
            padding=[15, 15, 15, 15],  # 🔥 第三次优化（从 20 减到 15）
            spacing=12  # 🔥 第三次优化（从 15 减到 12）
        )
        self.tasks_container.bind(minimum_height=self.tasks_container.setter('height'))
        scroll.add_widget(self.tasks_container)
        self.add_widget(scroll)
        
        # 初始加载任务
        self.refresh_tasks()
    
    def set_filter(self, status):
        """设置筛选条件"""
        self.current_filter = status
        
        # 更新按钮状态
        for btn in [self.btn_filter_all, self.btn_filter_pending, 
                    self.btn_filter_progress, self.btn_filter_completed]:
            btn.bold = False
        
        if status == "全部":
            self.btn_filter_all.bold = True
        elif status == "未开始":
            self.btn_filter_pending.bold = True
        elif status == "进行中":
            self.btn_filter_progress.bold = True
        elif status == "已完成":
            self.btn_filter_completed.bold = True
        
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """刷新任务列表"""
        print(f"[INFO] 刷新任务列表（筛选：{self.current_filter}）")
        
        # 清空现有卡片
        self.tasks_container.clear_widgets()
        
        # 获取筛选后的任务
        filtered_tasks = self.task_manager.get_filtered_tasks(self.current_filter)
        
        # 遍历所有任务
        for task in filtered_tasks:
            card = TaskCard(
                task_data=task,
                on_view_details=self.view_task_details,
                on_update_progress=self.update_task_progress,
                on_delete=self.delete_task,
                on_add_subtask=self.add_sub_task,
                on_edit=self.edit_task,
                level=0  # 🔥 主任务 level=0
            )
            
            # 🔥 恢复树型主任务的展开状态
            if task.get('task_type') == '树型' and task.get('sub_tasks'):
                if task['id'] in self._expanded_task_ids:
                    card.expanded = True
                    # 🔥 同步更新展开按钮文本
                    if hasattr(card, 'btn_expand'):
                        card.btn_expand.text = '▼'
                    # 🔥 刷新子任务显示
                    card.refresh_subtasks()
            
            self.tasks_container.add_widget(card)
        
        print(f"[OK] 已加载 {len(filtered_tasks)} 个任务")
    
    def show_add_task_dialog(self, instance):
        """显示新增任务对话框"""
        # 创建弹窗布局
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        # 标题
        title_label = Label(text='任务标题:', size_hint_y=None, height=40, halign='left')
        self.txt_title = TextInput(
            text='',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        layout.add_widget(title_label)
        layout.add_widget(self.txt_title)
        
        # 描述
        desc_label = Label(text='任务描述:', size_hint_y=None, height=40, halign='left')
        self.txt_description = TextInput(
            text='',
            size_hint_y=None,
            height=80,
            multiline=True
        )
        layout.add_widget(desc_label)
        layout.add_widget(self.txt_description)
        
        # 任务类型选择 - 🔥 带颜色反馈
        type_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        type_label = Label(text='任务类型:', size_hint_x=None, width=100, font_size='15sp')
        
        self.btn_type_numeric = Button(
            text='数值型',
            font_size='15sp',
            bold=True,
            background_color=(0.2, 0.6, 1, 1),  # 蓝色背景
            color=(1, 1, 1, 1)  # 白色文字
        )
        self.btn_type_numeric.bind(on_press=lambda x: self._set_task_type('数值型'))
        
        self.btn_type_tree = Button(
            text='树型',
            font_size='15sp',
            background_color=(0.9, 0.9, 0.9, 1),  # 灰色背景
            color=(0, 0, 0, 1)  # 黑色文字
        )
        self.btn_type_tree.bind(on_press=lambda x: self._set_task_type('树型'))
        
        type_layout.add_widget(type_label)
        type_layout.add_widget(self.btn_type_numeric)
        type_layout.add_widget(self.btn_type_tree)
        layout.add_widget(type_layout)
        
        self.current_task_type = '数值型'
        
        # 目标值和单位
        value_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        target_label = Label(text='目标值:', size_hint_x=None, width=80)
        self.txt_target = TextInput(
            text='100',
            size_hint_x=None,
            width=150,
            multiline=False
        )
        value_layout.add_widget(target_label)
        value_layout.add_widget(self.txt_target)
        
        unit_label = Label(text='单位:', size_hint_x=None, width=50)
        self.txt_unit = TextInput(
            text='%',
            size_hint_x=None,
            width=100,
            multiline=False
        )
        value_layout.add_widget(unit_label)
        value_layout.add_widget(self.txt_unit)
        
        layout.add_widget(value_layout)
        
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        btn_cancel = Button(text='取消')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        
        btn_confirm = Button(text='确定', bold=True)
        btn_confirm.bind(on_press=self._confirm_add_task)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
        layout.add_widget(btn_layout)
        
        # 创建弹窗
        popup = Popup(
            title='新增任务',
            content=layout,
            size_hint=(0.6, 0.8),
            auto_dismiss=False
        )
        popup.open()
    
    def _set_task_type(self, task_type):
        """设置任务类型 - 带视觉反馈"""
        self.current_task_type = task_type
        
        # 🔥 根据选中状态设置颜色
        if task_type == '数值型':
            self.btn_type_numeric.bold = True
            self.btn_type_numeric.background_color = (0.2, 0.6, 1, 1)  # 蓝色背景
            self.btn_type_numeric.color = (1, 1, 1, 1)  # 白色文字
            
            self.btn_type_tree.bold = False
            self.btn_type_tree.background_color = (0.9, 0.9, 0.9, 1)  # 灰色背景
            self.btn_type_tree.color = (0, 0, 0, 1)  # 黑色文字
        else:
            self.btn_type_tree.bold = True
            self.btn_type_tree.background_color = (0.2, 0.6, 1, 1)  # 蓝色背景
            self.btn_type_tree.color = (1, 1, 1, 1)  # 白色文字
            
            self.btn_type_numeric.bold = False
            self.btn_type_numeric.background_color = (0.9, 0.9, 0.9, 1)  # 灰色背景
            self.btn_type_numeric.color = (0, 0, 0, 1)  # 黑色文字
    
    def _confirm_add_task(self, instance):
        """确认添加任务"""
        title = self.txt_title.text.strip()
        if not title:
            print("[ERROR] 任务标题不能为空")
            return
        
        try:
            target_value = float(self.txt_target.text)
        except ValueError:
            print("[ERROR] 目标值必须是数字")
            return
        
        # 创建任务
        self.task_manager.create_task(
            title=title,
            description=self.txt_description.text.strip(),
            task_type=self.current_task_type,
            target_value=target_value,
            unit=self.txt_unit.text.strip()
        )
        
        # 刷新界面
        self.refresh_tasks()
        
        # 🔥 关闭弹窗
        # 找到弹窗并关闭
        popup = instance.parent.parent  # 获取弹窗引用
        while popup and not isinstance(popup, Popup):
            popup = popup.parent
        if popup:
            popup.dismiss()
        
        print(f"[OK] 任务已创建：{title}")
    
    def view_task_details(self, task_data):
        """查看任务详情弹窗"""
        # 创建滚动布局
        scroll_content = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(scroll_content)
        
        # 1. 基本信息
        info_group = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=200)
        
        title_label = Label(
            text=f"【{task_data['title']}】",
            size_hint_y=None,
            height=40,
            font_size='18sp',
            bold=True,
            halign='center'
        )
        info_group.add_widget(title_label)
        
        # 详细信息
        details = [
            f"ID: {task_data['id']}",
            f"类型：{task_data.get('task_type', '数值型')}",
            f"状态：{task_data.get('status', '未开始')}",
            f"目标值：{task_data.get('target_value', 100)} {task_data.get('unit', '%')}",
            f"当前值：{task_data.get('current_value', 0)} {task_data.get('unit', '%')}",
            f"进度：{task_data.get('progress', 0):.1f}%",
        ]
        
        if task_data.get('description'):
            details.append(f"描述：{task_data['description']}")
        
        for detail in details:
            lbl = Label(
                text=detail,
                size_hint_y=None,
                height=30,
                halign='left',
                font_size='14sp'
            )
            lbl.bind(size=lbl.setter('text_size'))
            info_group.add_widget(lbl)
        
        scroll_content.add_widget(info_group)
        
        # 2. 进度历史按钮
        btn_view_history = Button(
            text='查看进度历史',
            size_hint_y=None,
            height=50
        )
        btn_view_history.bind(on_press=lambda x: self.show_progress_history(task_data))
        scroll_content.add_widget(btn_view_history)
        
        # 3. 子任务信息（仅树型任务）
        if task_data.get('task_type') == '树型':
            sub_tasks = task_data.get('sub_tasks', [])
            if sub_tasks:
                lbl_subtasks = Label(
                    text=f"子任务数量：{len(sub_tasks)}",
                    size_hint_y=None,
                    height=40,
                    font_size='16sp',
                    bold=True
                )
                scroll_content.add_widget(lbl_subtasks)
                
                for sub_task in sub_tasks:
                    sub_info = f"  • {sub_task['title']}: {sub_task.get('progress', 0):.1f}%"
                    lbl_sub = Label(
                        text=sub_info,
                        size_hint_y=None,
                        height=30,
                        halign='left',
                        font_size='14sp'
                    )
                    scroll_content.add_widget(lbl_sub)
        
        # 4. 时间信息
        time_group = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=80)
        time_group.add_widget(Label(text='---', size_hint_y=None, height=20))
        time_group.add_widget(Label(
            text=f"创建时间：{task_data.get('created_at', '未知')[:19]}",
            size_hint_y=None,
            height=30
        ))
        time_group.add_widget(Label(
            text=f"更新时间：{task_data.get('updated_at', '未知')[:19]}",
            size_hint_y=None,
            height=30
        ))
        scroll_content.add_widget(time_group)
        
        # 5. 关闭按钮
        btn_close = Button(
            text='关闭',
            size_hint_y=None,
            height=50
        )
        btn_close.bind(on_press=lambda x: popup.dismiss())
        scroll_content.add_widget(btn_close)
        
        # 创建弹窗
        popup = Popup(
            title='任务详情',
            content=scroll,
            size_hint=(0.7, 0.8),
            auto_dismiss=False
        )
        popup.open()
    
    def show_progress_history(self, task_data):
        """显示进度历史记录弹窗"""
        # 创建布局
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        # 标题
        title = Label(
            text=f"【{task_data['title']}】进度历史",
            size_hint_y=None,
            height=50,
            font_size='16sp',
            bold=True
        )
        layout.add_widget(title)
        
        # 历史记录列表
        history = task_data.get('progress_history', [])
        
        if not history:
            lbl_no_history = Label(
                text='暂无进度历史记录',
                size_hint_y=None,
                height=100
            )
            layout.add_widget(lbl_no_history)
        else:
            # 使用 ScrollView
            scroll = ScrollView(size_hint=(1, 1))
            history_content = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
            history_content.bind(minimum_height=history_content.setter('height'))
            
            # 表头
            header = BoxLayout(size_hint_y=None, height=40, spacing=5)
            header.add_widget(Label(text='时间', bold=True))
            header.add_widget(Label(text='变化值', bold=True, size_hint_x=None, width=100))
            header.add_widget(Label(text='进度', bold=True, size_hint_x=None, width=80))
            header.add_widget(Label(text='备注', bold=True))
            history_content.add_widget(header)
            
            # 历史记录
            for record in reversed(history):  # 最新的在前
                row = BoxLayout(size_hint_y=None, height=40, spacing=5)
                
                timestamp = record.get('timestamp', '')[:19]
                value = record.get('value', 0)
                progress = record.get('progress', 0)
                note = record.get('note', '')
                
                row.add_widget(Label(text=timestamp))
                row.add_widget(Label(text=f"+{value}", size_hint_x=None, width=100))
                row.add_widget(Label(text=f"{progress:.1f}%", size_hint_x=None, width=80))
                row.add_widget(Label(text=note))
                
                history_content.add_widget(row)
            
            scroll.add_widget(history_content)
            layout.add_widget(scroll)
        
        # 关闭按钮
        btn_close = Button(text='关闭', size_hint_y=None, height=50)
        btn_close.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(btn_close)
        
        # 创建弹窗
        popup = Popup(
            title='进度历史',
            content=layout,
            size_hint=(0.8, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def update_task_progress(self, task_data):
        """更新任务进度弹窗"""
        # 创建布局
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        # 任务信息
        info = Label(
            text=f"任务：{task_data['title']}\n当前进度：{task_data.get('progress', 0):.1f}%",
            size_hint_y=None,
            height=80,
            font_size='14sp'
        )
        layout.add_widget(info)
        
        # 🔥 检查：树型主任务有子任务时，禁用进度更新
        if task_data.get('task_type') == '树型' and task_data.get('sub_tasks'):
            # 显示提示信息
            lbl_disabled = Label(
                text='⚠ 树型主任务已包含子任务\n\n请通过更新子任务进度来自动计算主任务进度\n主任务进度不能手动修改',
                size_hint_y=None,
                height=120,
                font_size='15sp',
                color=(1, 0.5, 0, 1),  # 橙色警告
                bold=True,
                halign='center'
            )
            layout.add_widget(lbl_disabled)
            
            # 显示子任务进度列表
            sub_tasks = task_data.get('sub_tasks', [])
            if sub_tasks:
                lbl_subtasks_title = Label(
                    text=f'\n子任务进度列表 ({len(sub_tasks)}个):',
                    size_hint_y=None,
                    height=40,
                    font_size='14sp',
                    bold=True
                )
                layout.add_widget(lbl_subtasks_title)
                
                for sub_task in sub_tasks:
                    sub_info = f"  • {sub_task['title']}: {sub_task.get('progress', 0):.1f}%"
                    lbl_sub = Label(
                        text=sub_info,
                        size_hint_y=None,
                        height=30,
                        halign='left',
                        font_size='14sp'
                    )
                    layout.add_widget(lbl_sub)
        
        # 树型任务无子任务 - 手动设置进度
        elif task_data.get('task_type') == '树型' and not task_data.get('sub_tasks'):
            # 树型任务无子任务 - 手动设置进度
            lbl_manual = Label(
                text='手动设置进度百分比:',
                size_hint_y=None,
                height=40
            )
            layout.add_widget(lbl_manual)
            
            manual_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            self.txt_manual_progress = TextInput(
                text=str(int(task_data.get('progress', 0))),
                multiline=False,
                input_filter='int'
            )
            manual_layout.add_widget(self.txt_manual_progress)
            
            btn_set = Button(text='设置进度')
            btn_set.bind(on_press=lambda x: self._confirm_manual_progress(task_data, popup))
            manual_layout.add_widget(btn_set)
            
            layout.add_widget(manual_layout)
        
        # 数值型任务 - 累加进度
        else:
            # 数值型任务或有子任务的树型任务 - 累加进度
            lbl_add = Label(
                text=f"增加进度 ({task_data.get('unit', '%')}):",
                size_hint_y=None,
                height=40
            )
            layout.add_widget(lbl_add)
            
            # 快捷按钮
            quick_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            for val in [1, 10, 50]:
                btn = Button(text=f'+{val}')
                btn.bind(on_press=lambda x, v=val: self._confirm_add_progress(task_data, v, '', popup))
                quick_layout.add_widget(btn)
            quick_layout.add_widget(Button(text='自定义'))
            layout.add_widget(quick_layout)
            
            # 自定义输入
            custom_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            self.txt_increment = TextInput(
                text='',
                multiline=False,
                hint_text='输入增加的数值'
            )
            custom_layout.add_widget(self.txt_increment)
            
            btn_custom = Button(text='确认增加')
            btn_custom.bind(on_press=lambda x: self._confirm_add_progress_from_input(task_data, popup))
            custom_layout.add_widget(btn_custom)
            
            layout.add_widget(custom_layout)
        
        # 备注
        lbl_note = Label(text='备注:', size_hint_y=None, height=30)
        layout.add_widget(lbl_note)
        
        self.txt_note = TextInput(
            text='',
            size_hint_y=None,
            height=60,
            multiline=True
        )
        layout.add_widget(self.txt_note)
        
        # 关闭按钮
        btn_close = Button(text='关闭', size_hint_y=None, height=50)
        btn_close.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(btn_close)
        
        # 创建弹窗
        popup = Popup(
            title='更新进度',
            content=layout,
            size_hint=(0.6, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def _confirm_add_progress(self, task_data, value, note, popup):
        """确认增加进度"""
        self.task_manager.update_progress(task_data['id'], value, note)
        self.refresh_tasks()
        popup.dismiss()
        print(f"[OK] 进度已更新：+{value}")
    
    def _confirm_add_progress_from_input(self, task_data, popup):
        """从输入框确认增加进度"""
        try:
            value = float(self.txt_increment.text)
            note = self.txt_note.text.strip()
            self._confirm_add_progress(task_data, value, note, popup)
        except ValueError:
            print("[ERROR] 请输入有效的数字")
    
    def _confirm_manual_progress(self, task_data, popup):
        """确认手动设置进度"""
        try:
            progress = float(self.txt_manual_progress.text)
            note = self.txt_note.text.strip()
            self.task_manager.set_manual_progress(task_data['id'], progress, note)
            self.refresh_tasks()
            popup.dismiss()
            print(f"[OK] 进度已手动设置为：{progress}%")
        except ValueError:
            print("[ERROR] 请输入有效的数字")
    
    def delete_task(self, task_id):
        """删除任务 - 带确认对话框"""
        # 创建确认对话框
        layout = BoxLayout(orientation='vertical', spacing=15, padding=[30, 30])
        
        lbl_confirm = Label(
            text='确定要删除这个任务吗？\n此操作不可恢复！',
            size_hint_y=None,
            height=100,
            font_size='16sp',
            halign='center'
        )
        lbl_confirm.bind(size=lbl_confirm.setter('text_size'))
        layout.add_widget(lbl_confirm)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=15)
        
        btn_cancel = Button(text='取消', font_size='15sp')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(btn_cancel)
        
        btn_confirm = Button(text='删除', font_size='15sp', bold=True)
        btn_confirm.bind(on_press=lambda x: self._confirm_delete(task_id, popup))
        btn_layout.add_widget(btn_confirm)
        
        layout.add_widget(btn_layout)
        
        popup = Popup(
            title='确认删除',
            content=layout,
            size_hint=(0.5, 0.4),
            auto_dismiss=False
        )
        popup.open()
    
    def _confirm_delete(self, task_id, popup):
        """确认删除任务"""
        self.task_manager.delete_task(task_id)
        self.refresh_tasks()
        popup.dismiss()
        print(f"[OK] 任务已删除：ID={task_id}")
    
    def add_sub_task(self, task_data):
        """添加子任务 - 完整实现"""
        # 创建添加子任务对话框
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        # 显示父任务信息
        parent_info = Label(
            text=f"为【{task_data['title']}】添加子任务",
            size_hint_y=None,
            height=50,
            font_size='15sp',
            bold=True,
            halign='center'
        )
        layout.add_widget(parent_info)
        
        # 子任务标题
        title_label = Label(text='子任务标题:', size_hint_y=None, height=40, halign='left')
        self.txt_subtask_title = TextInput(
            text='',
            size_hint_y=None,
            height=40,
            multiline=False,
            hint_text='输入子任务标题'
        )
        layout.add_widget(title_label)
        layout.add_widget(self.txt_subtask_title)
        
        # 子任务描述
        desc_label = Label(text='子任务描述:', size_hint_y=None, height=40, halign='left')
        self.txt_subtask_desc = TextInput(
            text='',
            size_hint_y=None,
            height=60,
            multiline=True,
            hint_text='可选'
        )
        layout.add_widget(desc_label)
        layout.add_widget(self.txt_subtask_desc)
        
        # 目标值和单位
        value_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        target_label = Label(text='目标值:', size_hint_x=None, width=80)
        self.txt_subtask_target = TextInput(
            text='100',
            size_hint_x=None,
            width=150,
            multiline=False
        )
        value_layout.add_widget(target_label)
        value_layout.add_widget(self.txt_subtask_target)
        
        unit_label = Label(text='单位:', size_hint_x=None, width=50)
        self.txt_subtask_unit = TextInput(
            text='%',
            size_hint_x=None,
            width=100,
            multiline=False
        )
        value_layout.add_widget(unit_label)
        value_layout.add_widget(self.txt_subtask_unit)
        
        layout.add_widget(value_layout)
        
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        btn_cancel = Button(text='取消', font_size='15sp')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(btn_cancel)
        
        btn_confirm = Button(text='确定', font_size='15sp', bold=True)
        btn_confirm.bind(on_press=lambda x: self._confirm_add_subtask(task_data, popup))
        btn_layout.add_widget(btn_confirm)
        
        layout.add_widget(btn_layout)
        
        # 创建弹窗
        popup = Popup(
            title='添加子任务',
            content=layout,
            size_hint=(0.6, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def _confirm_add_subtask(self, parent_task, popup):
        """确认添加子任务"""
        title = self.txt_subtask_title.text.strip()
        if not title:
            print("[ERROR] 子任务标题不能为空")
            return
        
        try:
            target_value = float(self.txt_subtask_target.text)
        except ValueError:
            print("[ERROR] 目标值必须是数字")
            return
        
        # 创建子任务数据
        sub_task = {
            'id': 0,  # 会在 TaskManager 中生成
            'title': title,
            'description': self.txt_subtask_desc.text.strip(),
            'task_type': '数值型',
            'target_value': target_value,
            'unit': self.txt_subtask_unit.text.strip(),
            'current_value': 0.0,
            'sub_tasks': [],
            'status': '未开始',
            'progress': 0,
            'progress_history': [],
            'target_progress': 100.0,  # 目标进度百分比
        }
        
        # 添加到父任务
        success = self.task_manager.add_sub_task(parent_task['id'], sub_task)
        if success:
            self.refresh_tasks()
            popup.dismiss()
            print(f"[OK] 子任务已添加：{title}")
    
    def edit_task(self, task_data):
        """编辑任务 - 完整实现"""
        # 创建编辑对话框
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        # 标题
        title_label = Label(text='编辑任务', size_hint_y=None, height=50, font_size='18sp', bold=True)
        layout.add_widget(title_label)
        
        # 任务标题
        lbl_title = Label(text='任务标题:', size_hint_y=None, height=40, halign='left')
        self.txt_edit_title = TextInput(
            text=task_data['title'],
            size_hint_y=None,
            height=40,
            multiline=False
        )
        layout.add_widget(lbl_title)
        layout.add_widget(self.txt_edit_title)
        
        # 任务描述
        lbl_desc = Label(text='任务描述:', size_hint_y=None, height=40, halign='left')
        self.txt_edit_desc = TextInput(
            text=task_data.get('description', ''),
            size_hint_y=None,
            height=80,
            multiline=True
        )
        layout.add_widget(lbl_desc)
        layout.add_widget(self.txt_edit_desc)
        
        # 目标值和单位
        value_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        lbl_target = Label(text='目标值:', size_hint_x=None, width=80)
        self.txt_edit_target = TextInput(
            text=str(task_data.get('target_value', 100)),
            size_hint_x=None,
            width=150,
            multiline=False
        )
        value_layout.add_widget(lbl_target)
        value_layout.add_widget(self.txt_edit_target)
        
        lbl_unit = Label(text='单位:', size_hint_x=None, width=50)
        self.txt_edit_unit = TextInput(
            text=task_data.get('unit', '%'),
            size_hint_x=None,
            width=100,
            multiline=False
        )
        value_layout.add_widget(lbl_unit)
        value_layout.add_widget(self.txt_edit_unit)
        
        layout.add_widget(value_layout)
        
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        btn_cancel = Button(text='取消', font_size='15sp')
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(btn_cancel)
        
        btn_save = Button(text='保存', font_size='15sp', bold=True)
        btn_save.bind(on_press=lambda x: self._confirm_edit_task(task_data, popup))
        btn_layout.add_widget(btn_save)
        
        layout.add_widget(btn_layout)
        
        # 创建弹窗
        popup = Popup(
            title='编辑任务',
            content=layout,
            size_hint=(0.6, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def _confirm_edit_task(self, task_data, popup):
        """确认编辑任务"""
        title = self.txt_edit_title.text.strip()
        if not title:
            print("[ERROR] 任务标题不能为空")
            return
        
        try:
            target_value = float(self.txt_edit_target.text)
        except ValueError:
            print("[ERROR] 目标值必须是数字")
            return
        
        # 更新任务
        self.task_manager.update_task(
            task_data['id'],
            title=title,
            description=self.txt_edit_desc.text.strip(),
            target_value=target_value,
            unit=self.txt_edit_unit.text.strip()
        )
        
        self.refresh_tasks()
        popup.dismiss()
        print(f"[OK] 任务已更新：{title}")
    
    def show_statistics(self):
        """显示统计看板弹窗"""
        # 获取统计数据
        stats = self.task_manager.get_statistics()
        
        # 创建布局
        layout = BoxLayout(orientation='vertical', spacing=15, padding=[30, 30])
        
        # 标题
        title = Label(
            text='任务统计看板',
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True
        )
        layout.add_widget(title)
        
        # 统计卡片
        cards_layout = GridLayout(cols=2, spacing=15, size_hint_y=None, height=200)
        
        # 总任务数
        self._add_stat_card(cards_layout, '总任务数', str(stats['total']), (0.4, 0.4, 0.4, 1))
        
        # 未开始
        self._add_stat_card(cards_layout, '未开始', str(stats['未开始']), (0.6, 0.6, 0.6, 1))
        
        # 进行中
        self._add_stat_card(cards_layout, '进行中', str(stats['进行中']), (0.2, 0.6, 1, 1))
        
        # 已完成
        self._add_stat_card(cards_layout, '已完成', str(stats['已完成']), (0.2, 0.8, 0.2, 1))
        
        layout.add_widget(cards_layout)
        
        # 完成率
        if stats['total'] > 0:
            completion_rate = (stats['已完成'] / stats['total']) * 100
            progress_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=80)
            
            lbl_rate = Label(
                text=f"完成率：{completion_rate:.1f}%",
                size_hint_y=None,
                height=40,
                font_size='16sp',
                bold=True
            )
            progress_layout.add_widget(lbl_rate)
            
            # 进度条
            with progress_layout.canvas.before:
                Color(0.9, 0.9, 0.9, 1)
                RoundedRectangle(pos=progress_layout.pos, size=(progress_layout.width, 20), radius=[10, 10, 10, 10])
                Color(0.2, 0.8, 0.2, 1)
                self.stat_progress_rect = RoundedRectangle(
                    pos=progress_layout.pos,
                    size=(progress_layout.width * (completion_rate / 100), 20),
                    radius=[10, 10, 10, 10]
                )
            
            progress_layout.bind(size=self._update_stat_progress)
            progress_layout.add_widget(Label(size_hint_y=None, height=10))
            
            layout.add_widget(progress_layout)
        
        # 关闭按钮
        btn_close = Button(text='关闭', size_hint_y=None, height=50)
        btn_close.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(btn_close)
        
        # 创建弹窗
        popup = Popup(
            title='统计看板',
            content=layout,
            size_hint=(0.6, 0.7),
            auto_dismiss=False
        )
        popup.open()
    
    def _add_stat_card(self, parent, label_text, value_text, color):
        """添加统计卡片"""
        card = BoxLayout(orientation='vertical', padding=[10, 10], spacing=5)
        
        with card.canvas.before:
            Color(*color)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[10, 10, 10, 10])
        
        lbl_label = Label(
            text=label_text,
            size_hint_y=None,
            height=30,
            font_size='14sp'
        )
        card.add_widget(lbl_label)
        
        lbl_value = Label(
            text=value_text,
            size_hint_y=None,
            height=50,
            font_size='24sp',
            bold=True
        )
        card.add_widget(lbl_value)
        
        parent.add_widget(card)
    
    def _update_stat_progress(self, instance, value):
        """更新统计进度条"""
        if hasattr(self, 'stat_progress_rect'):
            self.stat_progress_rect.pos = instance.pos
            # 需要重新计算宽度


# ============================================================================
# 应用入口
# ============================================================================

class LearningAssistantApp(App):
    """应用主类"""
    
    def build(self):
        """构建应用主界面"""
        # 🔥 导入 LabelBase 用于注册字体
        from kivy.core.text import LabelBase
        
        Window.size = (1000, 700)
        Window.minimum_width = 800
        Window.minimum_height = 600
        
        # 注册中文字体
        try:
            system = platform.system()
            
            if system == 'Windows':
                font_paths = [
                    r'C:\Windows\Fonts\msyh.ttc',
                    r'C:\Windows\Fonts\simsun.ttc',
                ]
            elif system == 'Darwin':
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',
                ]
            else:
                font_paths = [
                    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    LabelBase.register(name='Roboto', fn_regular=font_path)
                    print(f"[OK] 中文字体已注册：{font_path}")
                    break
                    
        except Exception as e:
            print(f"[ERROR] 字体注册失败：{e}")
        
        return MainScreen()


# ============================================================================
# 程序入口
# ============================================================================

if __name__ == '__main__':
    # 打印欢迎信息
    print("=" * 70)
    print("学习管理助手 v3.0 - 完全重写版")
    print("=" * 70)
    
    # 启动应用
    LearningAssistantApp().run()
