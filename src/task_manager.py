"""
任务管理器 - 改进版（参考学习管理助手）
主要改进：
1. 添加提醒周期设置（每日/每周）
2. 添加上次提醒时间追踪
3. 添加提醒检查功能
4. 优化数据结构
"""

import json
import os
from datetime import datetime, date
from typing import List, Optional, Dict, Any


class TaskManager:
    """任务管理工具（改进版）"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        """
        初始化任务管理器
        
        Args:
            data_file: 存储任务的 JSON 文件路径
        """
        self.data_file = data_file
        self.tasks: List[Dict[str, Any]] = []
        self.load_tasks()
    
    def load_tasks(self) -> None:
        """从 JSON 文件加载任务"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载任务失败：{e}")
                self.tasks = []
        else:
            self.tasks = []
    
    def save_tasks(self) -> None:
        """将任务保存到 JSON 文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存任务失败：{e}")
    
    def create_task(self, title: str, description: str = "", task_type: str = "数值型", 
                    target_value: float = 100.0, unit: str = "%",
                    target_progress: float = 100.0, reminder_period: str = None) -> Dict[str, Any]:
        """
        创建新任务
            
        Args:
            title: 任务标题
            description: 任务描述（可选）
            task_type: 任务类型 ("数值型" 或 "树型")
            target_value: 目标数值（数值型任务使用）
            unit: 单位（数值型任务使用）
            target_progress: 目标进度百分比（默认 100%）
            reminder_period: 提醒周期 (None, "daily", "weekly")
                
        Returns:
            新创建的任务对象
        """
        task_id = max([t.get('id', 0) for t in self.tasks] + [0]) + 1
        now = datetime.now().isoformat()
        
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'task_type': task_type,
            'target_value': target_value,
            'unit': unit,
            'current_value': 0.0,
            'sub_tasks': [],
            'status': '未开始',
            'progress': 0,
            'progress_history': [],
            'created_at': now,
            'updated_at': now,
            # 新增：目标进度百分比
            'target_progress': target_progress,  # 目标进度百分比（默认 100%）
            # 新增：提醒功能
            'reminder_period': reminder_period,  # None, "daily", "weekly"
            'last_reminded': now if reminder_period else None
        }
        self.tasks.append(task)
        self.save_tasks()
        print(f"✓ 任务创建成功！任务 ID: {task_id}, 类型：{task_type}")
        return task
    
    def update_progress(self, task_id: int, increment_value: float, note: str = "") -> bool:
        """
        更新任务进度（累加方式）
            
        Args:
            task_id: 任务 ID
            increment_value: 增加的数值（正数）
            note: 进度备注（可选）
                
        Returns:
            更新是否成功
        """
        if increment_value < 0:
            print("✗ 增加的值必须为正数")
            return False
            
        task = self._get_task(task_id)
        if not task:
            print(f"✗ 任务 ID {task_id} 不存在")
            return False
            
        # 数值型任务：累加实际数值
        if task.get('task_type', '数值型') == '数值型':
            old_value = task.get('current_value', 0)
            new_value = old_value + increment_value
            task['current_value'] = new_value
            
            # 根据目标值和目标进度自动计算当前进度百分比（限制最大值 100%）
            target_value = task.get('target_value', 100)
            target_progress = task.get('target_progress', 100)  # 目标进度百分比（默认 100%）
            progress = (new_value / target_value) * target_progress if target_value > 0 else 0
            progress = min(progress, 100.0)  # 限制最大值为 100%
            task['progress'] = round(progress, 1)
            
            # 记录历史
            history_entry = {
                'old_value': old_value,
                'new_value': new_value,
                'increment': increment_value,
                'timestamp': datetime.now().isoformat(),
                'note': note
            }
            task['progress_history'].append(history_entry)
            
            # 更新状态
            if progress >= 100:
                task['status'] = '已完成'
            elif progress > 0:
                task['status'] = '进行中'
            else:
                task['status'] = '未开始'
            
            task['updated_at'] = datetime.now().isoformat()
            self.save_tasks()
            
            print(f"✓ 任务进度已增加 {increment_value}{task.get('unit', '')}，当前值：{old_value:.1f}/{task.get('target_value', 100)}{task.get('unit', '')}，进度：{task['progress']}%")
            return True
        
        # 树型任务的子任务也是数值型，处理方式相同
        return False
    
    def add_sub_task(self, parent_task_id: int, sub_task_title: str,
                     sub_task_description: str = "", reminder_period: str = None) -> bool:
        """
        为树型任务添加子任务
        
        Args:
            parent_task_id: 父任务 ID
            sub_task_title: 子任务标题
            sub_task_description: 子任务描述
            reminder_period: 提醒周期
            
        Returns:
            添加是否成功
        """
        parent_task = self._get_task(parent_task_id)
        if not parent_task:
            print(f"✗ 任务 ID {parent_task_id} 不存在")
            return False
        
        if parent_task['task_type'] != '树型':
            print(f"✗ 只有树型任务才能添加子任务")
            return False
        
        # 收集所有已有的 ID（包括主任务和子任务）
        all_ids = [t.get('id', 0) for t in self.tasks]
        for task in self.tasks:
            if task.get('task_type') == '树型':
                for sub_task in task.get('sub_tasks', []):
                    all_ids.append(sub_task.get('id', 0))
        
        sub_task_id = max(all_ids + [0]) + 1
        now = datetime.now().isoformat()
        
        sub_task = {
            'id': sub_task_id,
            'title': sub_task_title,
            'description': sub_task_description,
            'task_type': '数值型',  # 子任务固定为数值型
            'target_value': 100.0,
            'unit': '%',
            'current_value': 0.0,
            'sub_tasks': [],
            'status': '未开始',
            'progress': 0,
            'progress_history': [],
            'created_at': now,
            'updated_at': now,
            'target_progress': 100.0,  # 子任务目标进度百分比
            # 新增：提醒功能
            'reminder_period': reminder_period,
            'last_reminded': now if reminder_period else None
        }
        
        parent_task['sub_tasks'].append(sub_task)
        parent_task['updated_at'] = now
        
        self.save_tasks()
        print(f"✓ 子任务添加成功！子任务 ID: {sub_task_id}")
        return True
    
    def _get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务（支持查找子任务）"""
        # 先查找主任务
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        
        # 再查找子任务
        for task in self.tasks:
            if task.get('task_type') == '树型':
                for sub_task in task.get('sub_tasks', []):
                    if sub_task['id'] == task_id:
                        return sub_task
        
        return None
    
    def _calculate_tree_progress(self, task: Dict[str, Any]) -> float:
        """
        递归计算树型任务的进度
        
        Args:
            task: 任务对象
            
        Returns:
            树的总进度百分比
        """
        if not task.get('sub_tasks'):
            # 没有子任务，直接返回当前任务的进度
            return task.get('progress', 0)
        
        # 有子任务，计算所有子任务的平均进度
        total_progress = 0
        for sub_task in task['sub_tasks']:
            # 子任务是数值型任务，直接使用 progress 字段
            total_progress += sub_task.get('progress', 0)
        
        return total_progress / len(task['sub_tasks']) if task['sub_tasks'] else 0
    
    def update_tree_progress(self, tree_task_id: int) -> bool:
        """
        更新树型任务的进度（基于所有子任务的进度）
        
        Args:
            tree_task_id: 树型任务 ID
            
        Returns:
            更新是否成功
        """
        tree_task = self._get_task(tree_task_id)
        if not tree_task:
            print(f"✗ 任务 ID {tree_task_id} 不存在")
            return False
        
        if tree_task['task_type'] != '树型':
            print(f"✗ 只有树型任务才能使用此方法")
            return False
        
        # 计算树的总进度
        total_progress = self._calculate_tree_progress(tree_task)
        tree_task['progress'] = total_progress
        
        # 更新状态
        if total_progress >= 100:
            tree_task['status'] = '已完成'
        elif total_progress > 0:
            tree_task['status'] = '进行中'
        else:
            tree_task['status'] = '未开始'
        
        tree_task['updated_at'] = datetime.now().isoformat()
        self.save_tasks()
        
        print(f"✓ 树型任务进度已更新为 {total_progress:.1f}%")
        return True
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        # 查找并删除主任务
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                self.save_tasks()
                print(f"✓ 任务已删除")
                return True
        
        # 查找并删除子任务
        for task in self.tasks:
            if task.get('task_type') == '树型':
                for i, sub_task in enumerate(task.get('sub_tasks', [])):
                    if sub_task['id'] == task_id:
                        del task['sub_tasks'][i]
                        task['updated_at'] = datetime.now().isoformat()
                        self.save_tasks()
                        print(f"✓ 子任务已删除")
                        return True
        
        print(f"✗ 任务 ID {task_id} 不存在")
        return False
    
    def check_reminders(self) -> List[Dict[str, Any]]:
        """
        检查需要提醒的任务
        
        Returns:
            需要提醒的任务列表
        """
        today = date.today()
        reminders = []
        
        def _check_goal(goal):
            """递归检查目标"""
            if goal.get('reminder_period'):
                last_reminded = goal.get('last_reminded')
                if last_reminded:
                    last_date = datetime.fromisoformat(last_reminded).date()
                    days_passed = (today - last_date).days
                    
                    period = goal['reminder_period']
                    need_remind = False
                    
                    if period == "daily" and days_passed >= 1:
                        need_remind = True
                    elif period == "weekly" and days_passed >= 7:
                        need_remind = True
                    
                    if need_remind:
                        reminders.append(goal)
            
            # 递归检查子任务
            for sub_task in goal.get('sub_tasks', []):
                _check_goal(sub_task)
        
        for task in self.tasks:
            _check_goal(task)
        
        return reminders
    
    def mark_as_reminded(self, task_id: int) -> bool:
        """
        标记任务已提醒
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功
        """
        task = self._get_task(task_id)
        if not task:
            return False
        
        task['last_reminded'] = datetime.now().isoformat()
        self.save_tasks()
        print(f"✓ 任务已标记为提醒")
        return True


# 测试代码
if __name__ == "__main__":
    # 创建测试
    manager = TaskManager("test_improved.json")
    
    print("\n=== 测试提醒功能 ===")
    
    # 创建带提醒的任务
    task1 = manager.create_task(
        title="每日刷题",
        description="每天刷算法题",
        task_type="数值型",
        target_value=100,
        unit="题",
        reminder_period="daily"  # 每日提醒
    )
    
    # 创建周提醒任务
    task2 = manager.create_task(
        title="每周总结",
        description="每周学习总结",
        task_type="数值型",
        target_value=1,
        unit="次",
        reminder_period="weekly"  # 每周提醒
    )
    
    # 检查提醒
    reminders = manager.check_reminders()
    print(f"\n需要提醒的任务数：{len(reminders)}")
    for r in reminders:
        print(f"  - {r['title']} (周期：{r['reminder_period']})")
    
    # 清理测试文件
    if os.path.exists("test_improved.json"):
        os.remove("test_improved.json")
    
    print("\n✅ 改进版任务管理器测试完成！")
