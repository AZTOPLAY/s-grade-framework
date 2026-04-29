# 技术方案模板 v1.0
## 用途：S级框架输出技术方案时的标准模板，包含代码示例

---

## 一、方案概述
[一句话描述方案目标]

## 二、技术架构
[架构图 + 技术栈选型表]

## 三、核心代码示例

### 3.1 主流程代码
```python
# 示例：主流程入口
def main():
    """
    主流程入口
    """
    # Step 1: 数据采集
    data = collect_data()
    
    # Step 2: 数据处理
    processed = process_data(data)
    
    # Step 3: 生成输出
    output = generate_output(processed)
    
    return output
```

### 3.2 核心模块代码
```python
# 示例：核心模块
class CoreModule:
    def __init__(self, config):
        self.config = config
    
    def execute(self, input_data):
        # TODO: 实现核心逻辑
        pass
```

## 四、API接口定义
```yaml
# API接口示例
endpoints:
  - path: /api/v1/action
    method: POST
    params:
      - name: param1
        type: string
        required: true
    response:
      code: 200
      data: {}
```

## 五、配置文件示例
```yaml
# config.yaml示例
app:
  name: "app-name"
  version: "1.0.0"
  
database:
  type: sqlite
  path: /path/to/db.sqlite
```

## 六、实施计划
| 阶段 | 周期 | 交付物 | 验收标准 |
|------|------|--------|----------|
| MVP | X天 | 基础功能 | 可运行、可测试 |
| 增强 | X天 | 完整功能 | 通过全量测试 |
| 优化 | X天 | 性能优化 | 性能提升X% |

## 七、风险与预案
| 风险 | 概率 | 影响 | 预案 |
|------|------|------|------|
| 风险1 | 高/中/低 | 高/中/低 | 具体措施 |

---

*模板版本：v1.0*
*最后更新：2026-04-27*
