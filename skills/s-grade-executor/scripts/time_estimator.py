#!/usr/bin/env python3
"""
S级框架时间预估器 - MVP版本

功能：
- 基于因子模型的时间预估
- 只考虑最关键的"模板可用性"系数
- 输出区间预估（min-expected-max）

使用方式：
    from time_estimator import TimeEstimator
    
    result = TimeEstimator.estimate(
        task_type="config_creation",
        complexity="complex",
        template_level="complete"
    )
    print(result)
    # {'min': 2.1, 'expected': 3.0, 'max': 3.9, 'confidence': 'high'}

版本: v1.0.0
日期: 2026-04-23
"""

from typing import Dict, Literal, Optional, Tuple
from dataclasses import dataclass
import warnings


# ============================================================
# 基础时间库（分钟）
# ============================================================
BASE_TIMES: Dict[str, Dict[str, float]] = {
    "config_creation": {
        "simple": 5,
        "medium": 15,
        "complex": 30,
    },
    "code_writing": {
        "simple": 10,
        "medium": 30,
        "complex": 60,
    },
    "documentation": {
        "simple": 5,
        "medium": 20,
        "complex": 60,
    },
    "research": {
        "simple": 15,
        "medium": 45,
        "complex": 120,
    },
    "analysis": {
        "simple": 10,
        "medium": 30,
        "complex": 90,
    },
    "evaluation": {
        "simple": 10,
        "medium": 25,
        "complex": 50,
    },
    "integration": {
        "simple": 15,
        "medium": 45,
        "complex": 90,
    },
}

# ============================================================
# 模板系数（最关键，解决80%问题）
# ============================================================
TEMPLATE_FACTORS: Dict[str, float] = {
    "none": 1.0,       # 无模板：从零开始
    "partial": 0.5,    # 部分模板：有参考但需修改
    "complete": 0.1,   # 完整模板：直接使用
}

# ============================================================
# 任务类型别名（便于使用）
# ============================================================
TASK_ALIASES: Dict[str, str] = {
    "config": "config_creation",
    "code": "code_writing",
    "doc": "documentation",
    "docs": "documentation",
    "write": "code_writing",
    "script": "code_writing",
    "research": "research",
    "analysis": "analysis",
    "eval": "evaluation",
    "assess": "evaluation",
    "integrate": "integration",
    "int": "integration",
}


@dataclass
class EstimationResult:
    """预估结果"""
    min: float
    expected: float
    max: float
    confidence: str
    base_time: float
    template_factor: float
    task_type: str
    complexity: str

    def to_dict(self) -> dict:
        return {
            "min": self.min,
            "expected": self.expected,
            "max": self.max,
            "confidence": self.confidence,
        }

    def __str__(self) -> str:
        confidence_emoji = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴",
        }
        emoji = confidence_emoji.get(self.confidence, "⚪")
        return (
            f"{emoji} 预估时间: {self.min}-{self.max} 分钟 "
            f"(预期 {self.expected} 分钟)"
        )

    def validate_ai_time(self, human_time: float) -> Tuple[bool, float, str]:
        """
        校验AI时间是否符合AI时间思维规范
        
        Args:
            human_time: 人类完成同任务所需时间（分钟）
            
        Returns:
            (是否合法, 加速比, 说明)
        """
        acceleration = human_time / self.expected
        if 10 <= acceleration <= 50:
            return True, round(acceleration, 1), f"✅ 加速比 {acceleration} 符合AI时间规范（10-50倍）"
        elif acceleration < 10:
            return False, round(acceleration, 1), f"⚠️ 加速比 {acceleration} 低于10倍，不符合AI时间思维，建议优化预估"
        else:
            return False, round(acceleration, 1), f"⚠️ 加速比 {acceleration} 高于50倍，预估过于激进，建议调整"

    @staticmethod
    def human_to_ai_time(human_time: float, acceleration: float = 25) -> float:
        """
        人类时间转换为AI时间
        
        Args:
            human_time: 人类完成时间（分钟）
            acceleration: 加速比，默认25倍（10-50倍区间中间值）
            
        Returns:
            AI预估时间（分钟）
        """
        if acceleration < 10 or acceleration > 50:
            warnings.warn(f"加速比 {acceleration} 不在推荐区间10-50，使用默认值25")
            acceleration = 25
        return round(human_time / acceleration, 1)


class TimeEstimator:
    """
    S级框架时间预估器 MVP版本
    
    核心公式：
        预估时间 = 基础时间 × 模板系数
    
    说明：
        - 基础时间：根据任务类型和复杂度
        - 模板系数：有无现成模板（最关键因子）
        - 区间：预期时间 ±30%
    
    使用示例：
        >>> est = TimeEstimator()
        >>> result = est.estimate("config_creation", "complex", "complete")
        >>> print(result)
        🟢 预估时间: 2.1-3.9 分钟 (预期 3.0 分钟)
    """

    def __init__(
        self,
        base_times: Optional[Dict[str, Dict[str, float]]] = None,
        template_factors: Optional[Dict[str, float]] = None,
    ):
        """
        初始化预估器
        
        Args:
            base_times: 自定义基础时间库
            template_factors: 自定义模板系数
        """
        self.base_times = base_times or BASE_TIMES
        self.template_factors = template_factors or TEMPLATE_FACTORS

    def estimate(
        self,
        task_type: str,
        complexity: Literal["simple", "medium", "complex"],
        template_level: Literal["none", "partial", "complete"] = "none",
    ) -> EstimationResult:
        """
        预估任务时间
        
        Args:
            task_type: 任务类型
                - config_creation / config / config_creation
                - code_writing / code / script
                - documentation / doc / docs
                - research
                - analysis
                - evaluation / eval / assess
                - integration / integrate / int
            complexity: 复杂度
                - simple: 简单任务
                - medium: 中等任务
                - complex: 复杂任务
            template_level: 模板可用性
                - none: 无模板，从零开始
                - partial: 部分模板，有参考但需修改
                - complete: 完整模板，直接使用
        
        Returns:
            EstimationResult: 预估结果
            
        Raises:
            ValueError: 无效的任务类型或复杂度
        """
        # 解析任务类型别名
        task_type = self._resolve_task_type(task_type)
        
        # 获取基础时间
        base_time = self._get_base_time(task_type, complexity)
        
        # 获取模板系数
        template_factor = self._get_template_factor(template_level)
        
        # 计算预期时间
        expected = base_time * template_factor
        
        # 计算区间（±30%）
        min_time = round(expected * 0.7, 1)
        max_time = round(expected * 1.3, 1)
        
        # 计算信心度
        confidence = self._get_confidence(template_level, template_factor)
        
        return EstimationResult(
            min=min_time,
            expected=round(expected, 1),
            max=max_time,
            confidence=confidence,
            base_time=base_time,
            template_factor=template_factor,
            task_type=task_type,
            complexity=complexity,
        )

    def _resolve_task_type(self, task_type: str) -> str:
        """解析任务类型（支持别名）"""
        task_lower = task_type.lower()
        
        # 检查别名
        if task_lower in TASK_ALIASES:
            return TASK_ALIASES[task_lower]
        
        # 检查完整类型
        if task_lower in self.base_times:
            return task_lower
        
        # 未知类型，使用默认值
        return "analysis"

    def _get_base_time(
        self,
        task_type: str,
        complexity: str,
    ) -> float:
        """获取基础时间"""
        if task_type not in self.base_times:
            # 默认使用 analysis
            task_type = "analysis"
        
        complexity_times = self.base_times[task_type]
        
        if complexity not in complexity_times:
            complexity = "medium"
        
        return complexity_times[complexity]

    def _get_template_factor(self, template_level: str) -> float:
        """获取模板系数"""
        return self.template_factors.get(template_level, 1.0)

    def _get_confidence(
        self,
        template_level: str,
        template_factor: float,
    ) -> str:
        """获取信心度"""
        if template_level == "complete":
            return "high"
        elif template_level == "partial":
            return "medium"
        else:
            return "low"

    def get_task_types(self) -> list:
        """获取支持的任务类型"""
        return list(self.base_times.keys())

    def get_complexities(self) -> list:
        """获取支持的复杂度"""
        return ["simple", "medium", "complex"]

    def get_template_levels(self) -> list:
        """获取支持的模板级别"""
        return list(self.template_factors.keys())


# ============================================================
# 便捷函数
# ============================================================
def estimate(
    task_type: str,
    complexity: str = "medium",
    template_level: str = "none",
    apply_calibration: bool = True,
) -> EstimationResult:
    """
    便捷函数：预估任务时间
    
    使用示例：
        >>> from time_estimator import estimate
        >>> result = estimate("config", "complex", "complete")
        >>> print(result)
        🟢 预估时间: 2.1-3.9 分钟 (预期 3.0 分钟)
    """
    estimator = TimeEstimator()
    result = estimator.estimate(task_type, complexity, template_level)
    
    # 应用校正因子（基于历史偏差数据：实际耗时通常比预估快15-25%）
    if apply_calibration:
        # 校正因子：增加预估时间，减少负偏差
        calibration_factor = 1.20  # 增加20%
        result.expected = round(result.expected * calibration_factor, 1)
        result.min = round(result.min * calibration_factor, 1)
        result.max = round(result.max * calibration_factor, 1)
    
    return result


def validate_ai_time(result: EstimationResult, human_time: float) -> Tuple[bool, float, str]:
    """
    便捷函数：校验AI时间规范
    """
    return result.validate_ai_time(human_time)


def human_to_ai_time(human_time: float, acceleration: float = 25) -> float:
    """
    便捷函数：人类时间转AI时间
    """
    return EstimationResult.human_to_ai_time(human_time, acceleration)


# ============================================================
# CLI 入口
# ============================================================
def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="S级框架时间预估器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s --type config --complexity complex --template complete
  %(prog)s --type code --complexity medium --template partial
  %(prog)s --list-types
  %(prog)s --interactive
        """,
    )
    
    parser.add_argument(
        "--type", "-t",
        dest="task_type",
        default="analysis",
        help="任务类型 (default: analysis)",
    )
    parser.add_argument(
        "--complexity", "-c",
        choices=["simple", "medium", "complex"],
        default="medium",
        help="复杂度 (default: medium)",
    )
    parser.add_argument(
        "--template", "-T",
        choices=["none", "partial", "complete"],
        default="none",
        help="模板可用性 (default: none)",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="列出所有任务类型",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互式预估",
    )
    parser.add_argument(
        "--human-time",
        type=float,
        help="人类完成时间（分钟），用于校验AI时间规范",
    )
    parser.add_argument(
        "--convert-human",
        type=float,
        help="转换人类时间为AI时间（分钟）",
    )
    parser.add_argument(
        "--acceleration",
        type=float,
        default=25,
        help="加速比（默认25，推荐10-50）",
    )
    
    args = parser.parse_args()
    
    # 实例化预估器
    estimator = TimeEstimator()
    
    # 列出任务类型
    if args.list_types:
        print("支持的任務類型：")
        for task_type in estimator.get_task_types():
            print(f"  - {task_type}")
        print("\n支持的複雜度：")
        for c in estimator.get_complexities():
            print(f"  - {c}")
        print("\n支持的模板級別：")
        for t in estimator.get_template_levels():
            print(f"  - {t}: 係數={estimator.template_factors[t]}")
        return
    
    # 交互式预估
    if args.interactive:
        print("=" * 50)
        print("S级框架时间预估器 - 交互模式")
        print("=" * 50)
        
        # 选择任务类型
        print("\n可用任务类型：")
        types = estimator.get_task_types()
        for i, t in enumerate(types, 1):
            print(f"  {i}. {t}")
        choice = input(f"\n选择任务类型 (1-{len(types)}, 默认1): ").strip()
        if choice:
            task_type = types[int(choice) - 1]
        else:
            task_type = types[0]
        
        # 选择复杂度
        print("\n复杂度：")
        complexities = estimator.get_complexities()
        for i, c in enumerate(complexities, 1):
            print(f"  {i}. {c}")
        choice = input(f"\n选择复杂度 (1-{len(complexities)}, 默认2): ").strip()
        if choice:
            complexity = complexities[int(choice) - 1]
        else:
            complexity = "medium"
        
        # 选择模板级别
        print("\n模板可用性：")
        templates = estimator.get_template_levels()
        for i, t in enumerate(templates, 1):
            factor = estimator.template_factors[t]
            desc = {
                "none": "无模板，从零开始",
                "partial": "部分模板，有参考但需修改",
                "complete": "完整模板，直接使用",
            }
            print(f"  {i}. {t}: {desc[t]} (系数={factor})")
        choice = input(f"\n选择模板级别 (1-{len(templates)}, 默认1): ").strip()
        if choice:
            template_level = templates[int(choice) - 1]
        else:
            template_level = "none"
        
        print()
        result = estimator.estimate(task_type, complexity, template_level)
        print(result)
        return
    
    # 转换人类时间为AI时间
    if args.convert_human:
        ai_time = EstimationResult.human_to_ai_time(args.convert_human, args.acceleration)
        print(f"🧠 人类时间: {args.convert_human} 分钟 → AI时间: {ai_time} 分钟 (加速比: {args.acceleration}x)")
        return
    
    # 直接预估
    result = estimator.estimate(args.task_type, args.complexity, args.template)
    print(result)
    
    # 校验AI时间规范
    if args.human_time:
        valid, acceleration, msg = result.validate_ai_time(args.human_time)
        print(msg)


if __name__ == "__main__":
    main()
