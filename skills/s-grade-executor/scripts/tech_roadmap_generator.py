#!/usr/bin/env python3
"""
技术演进路线生成器 v1.0
用途：自动生成技术方案的演进路线，增强前瞻性

使用方式：
    from tech_roadmap_generator import generate_roadmap
    
    roadmap = generate_roadmap(
        current_tech="SQLite",
        target_tech="PostgreSQL",
        timeline_months=6
    )
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class RoadmapPhase:
    """演进阶段"""
    phase: int
    name: str
    duration_weeks: int
    objectives: List[str]
    deliverables: List[str]
    risks: List[str]


def generate_roadmap(
    current_state: str,
    target_state: str,
    timeline_months: int = 6,
    key_features: List[str] = None,
) -> Dict:
    """
    生成技术演进路线
    
    Args:
        current_state: 当前技术状态
        target_state: 目标技术状态
        timeline_months: 演进周期（月）
        key_features: 关键特性列表
    
    Returns:
        演进路线字典
    """
    if key_features is None:
        key_features = ["性能优化", "可扩展性", "可维护性"]
    
    # 计算阶段数量
    total_weeks = timeline_months * 4
    phases_count = min(max(timeline_months, 2), 4)  # 2-4个阶段
    weeks_per_phase = total_weeks // phases_count
    
    phases = []
    for i in range(phases_count):
        if i == 0:
            name = "基础建设"
            objectives = ["搭建基础设施", "完成技术验证"]
            deliverables = ["技术选型报告", "POC验证"]
            risks = ["技术选型偏差", "资源不足"]
        elif i == phases_count - 1:
            name = "全面落地"
            objectives = ["完成全量迁移", "优化性能指标"]
            deliverables = ["生产环境部署", "性能报告"]
            risks = ["迁移失败", "性能不达标"]
        else:
            name = f"能力增强-{i}"
            objectives = ["扩展功能覆盖", "提升系统稳定性"]
            deliverables = ["功能模块", "测试报告"]
            risks = ["功能延期", "质量问题"]
        
        phases.append(RoadmapPhase(
            phase=i + 1,
            name=name,
            duration_weeks=weeks_per_phase,
            objectives=objectives,
            deliverables=deliverables,
            risks=risks,
        ))
    
    return {
        "current_state": current_state,
        "target_state": target_state,
        "timeline_months": timeline_months,
        "phases": [p.__dict__ for p in phases],
        "key_features": key_features,
    }


def format_roadmap_markdown(roadmap: Dict) -> str:
    """格式化为Markdown"""
    lines = [
        f"# 技术演进路线",
        f"",
        f"## 演进目标",
        f"- 当前状态：{roadmap['current_state']}",
        f"- 目标状态：{roadmap['target_state']}",
        f"- 演进周期：{roadmap['timeline_months']}个月",
        f"",
        f"## 演进阶段",
        f"",
    ]
    
    for phase in roadmap["phases"]:
        lines.extend([
            f"### 阶段{phase['phase']}：{phase['name']}（{phase['duration_weeks']}周）",
            f"",
            f"**目标**：",
        ])
        for obj in phase["objectives"]:
            lines.append(f"- {obj}")
        
        lines.append(f"")
        lines.append(f"**交付物**：")
        for d in phase["deliverables"]:
            lines.append(f"- {d}")
        
        lines.append(f"")
        lines.append(f"**风险**：")
        for r in phase["risks"]:
            lines.append(f"- {r}")
        lines.append(f"")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 示例
    roadmap = generate_roadmap(
        current_state="SQLite单机版",
        target_state="PostgreSQL集群版",
        timeline_months=3,
    )
    print(format_roadmap_markdown(roadmap))
