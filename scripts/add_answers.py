import sys
filepath = r'e:\Desktop\AI+训练师\AI+人工智能训练师-单选题.md'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

answers = {
    527: ("A（算法偏差）", "在构建业务架构时需要考虑算法偏差等AI风险。"),
    528: ("D（神经网络）", "神经网络不是业务流程构建方法。"),
    529: ("A（工作流）", "工作流技术是实现流程自动化的主要手段。"),
    530: ("A（公平性）", "构建业务框架时需要注意公平性等伦理问题。"),
    531: ("A（改进业务流程）", "精益六西格玛用于改进业务流程。"),
    532: ("B（评估流程性能的指标）", "关键绩效指标是评估流程性能的指标。"),
    533: ("C（设计人工智能系统）", "设计人工智能系统不属于价值流程映射的步骤。"),
    534: ("B（根本性重新设计）", "业务流程再造的目的是对现有流程进行根本性重新设计。"),
    535: ("D（组织模型）", "组织模型用于描述组织结构。"),
    536: ("B（BPMN工具）", "BPMN工具最适合用于业务流程建模和分析。"),
    537: ("B（服务导向架构）", "SOA是服务导向架构。"),
    538: ("A（最耗时的活动）", "瓶颈是指最耗时的活动。"),
    539: ("B（工作流引擎）", "工作流引擎是适合实现流程自动化的技术。"),
    540: ("A（业务规则引擎）", "业务规则引擎用于处理业务流程中的异常情况。"),
    541: ("A（监控和控制业务流程执行）", "流程管理是对业务流程执行进行监控和控制。"),
    542: ("B（详细展示不同参与者在流程中的职责和任务）", "泳道图的主要优势是详细展示不同参与者在流程中的职责和任务。"),
    543: ("D（实现利润最大化）", "实现利润最大化不是业务流程优化的直接目标。"),
    544: ("A（企业资源计划系统）", "ERP系统是企业资源计划系统。"),
    545: ("A（机器学习）", "机器学习是实现智能流程自动化的技术。"),
    546: ("C（增加收益）", "增加收益不是业务流程管理的直接优势。"),
    547: ("A（应用数字技术改造业务模式）", "数字化转型是应用数字技术改造业务模式。"),
    548: ("A（开发运维一体化）", "DevOps是开发运维一体化。"),
    549: ("B（关键绩效指标）", "关键绩效指标是评估流程绩效的常用方法。"),
    550: ("D（深度学习控制）", "深度学习控制不是业务流程控制的类型。"),
}

modified = False
result = []
i = 0
while i < len(lines):
    line = lines[i]
    result.append(line)

    for qnum in range(527, 551):
        prefix = f"{qnum}、"
        if line.strip().startswith(prefix):
            next_idx = i + 1
            has_answer = False
            while next_idx < len(lines) and next_idx < i + 10:
                next_line = lines[next_idx].strip()
                if next_line.startswith("**答案："):
                    has_answer = True
                    break
                if next_line.startswith(f"{qnum+1}、"):
                    break
                next_idx += 1

            if not has_answer and qnum in answers:
                ans,解析 = answers[qnum]
                result.append(f"\n**答案：{ans}**\n")
                result.append(f"**解析**：{解析}\n")
                modified = True
                print(f"Added answer for question {qnum}")

    i += 1

if modified:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(result)
    print("File updated successfully!")
else:
    print("No modifications made.")