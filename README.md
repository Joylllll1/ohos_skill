<div align="center">

# HarmonyOS PC 移植与上架助手

**给移植桌面应用的开发者一套可由 coding agent 执行的流程：评估路线、接续工程、准备上架。**

![Agent Skill](https://img.shields.io/badge/Agent-Skill-2563EB)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Helper-Standard_Library-4B8BBE)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[快速开始](#快速开始) · [功能一览](#功能一览) · [技术架构](#技术架构) · [配置与测试](#配置与测试) · [文档地图](#文档地图) · [如何贡献](#如何贡献)

</div>

在目标项目的 agent 会话中使用：

```text
使用 $harmonyos-pc-porting 接手当前工程。
先检查代码、已有产物和移植记录，说明现在做到哪一步、哪些仍未完成，
并整理下一步计划。先不要修改应用代码、上传或提交审核。
```

预期交付是**当前阶段与依据、待办及其影响、可接续的计划**。已有工程沿用原记录；遇到账号或设备条件不足，会说明需要谁处理、如何确认完成、随后从哪里继续。

## 这是什么

这是一个帮助 coding agent 辅助移植和上架的 skill，包含流程说明、技术参考、计划模板和 Python 检查工具。它按项目的语言、架构、依赖与平台接口选择路线，适用于新项目评估、接手做到一半的工程、发布准备和审核整改。

完整流程覆盖：**范围盘点 → 路线原型 → 构建打包 → 功能集成 → 目标环境验证 → 发布候选 → 提交审核 → 审核、实际发布与维护**。每次任务只推进到用户要求的终点，不必从头重走。

流程围绕平台边界、构建、验证与发布检查组织，并提供官方资料索引。具体补丁和技术方案需按项目验证。skill 由宿主 agent 读取并执行；实际构建、设备操作和平台交互取决于该 agent 的工具与权限。

## 快速开始

### 方式一：让 agent 检查你的项目

需要一个能读取项目文件的 coding agent，以及本仓库的完整文件。只做检查和计划，不需要先安装 DevEco 或连接真机。

**无需安装也能开始。** 将本仓库所在位置替换为实际绝对路径，在待移植项目的会话中发送：

```text
请读取 /path/to/ohos_skill/skills/harmonyos-pc-porting/SKILL.md，
按其中流程检查当前项目。先给出现状、移植路线和待办计划，不修改代码或提交审核。
```

结果会出现在会话中；允许写计划时，agent 会沿用项目已有工作记录，或创建记录并给出路径。若只能聊天而不能访问文件，需先换到能访问工程的环境，不能把建议当成已完成检查。

**经常使用时，可安装到 Codex skills 目录。** macOS/Linux 下，在包含本 README 的仓库根目录执行：

```bash
# 尊重已有 CODEX_HOME；默认安装到 ~/.codex/skills
skill_dest="${CODEX_HOME:-$HOME/.codex}/skills/harmonyos-pc-porting"
if [ -e "$skill_dest" ] || [ -L "$skill_dest" ]; then
  echo "目标已存在，请先核对现有安装：$skill_dest"
else
  mkdir -p "$(dirname "$skill_dest")"
  cp -R skills/harmonyos-pc-porting "$skill_dest"
fi
```

这会复制完整 skill，包括参考资料、脚本和许可证。复制安装后，仓库更新不会自动同步到安装副本；更新前先核对已有版本。其他系统可以手动复制文件夹。

在加载了技能的会话中发送开头的 `$harmonyos-pc-porting` 请求。如果技能未出现在列表里，直接给出安装目录中 `SKILL.md` 的绝对路径即可。其他 agent 可按各自机制加载整个目录；跨 agent 的自动发现尚未全面测试。

### 方式二：先独立运行盘点工具

仅需 Python 3，无第三方 Python 依赖，也不需要 agent、SDK 或账号。在仓库根目录执行：

```bash
# 先扫描本仓库，确认工具可用
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py inventory .
```

终端会打印 JSON。以下是扫描本仓库时的部分字段：

```json
{
  "source_file_types": { ".py": 2 },
  "manifest_paths": [],
  "stack_signals": {
    "source_languages": ["Python"],
    "build_and_dependency_files": []
  },
  "truncated": false,
  "scan_errors": []
}
```

把 `.` 换成目标项目目录即可盘点其他工程。工具读取文件名和扩展名，输出构建文件线索与扫描范围；它不会执行项目脚本，也不会自动给出完整移植方案。

## 功能一览

| 模块 | 当前能力 |
|---|---|
| 项目盘点与路线选择 | 分析 Web/Electron、C/C++ GUI、解释器及混合架构，找出平台边界和需要先验证的能力 |
| 已有项目接手 | 区分开发版本、候选包与线上版本，按时间和证据处理旧记录冲突 |
| 构建与功能适配 | 指导工具链、依赖 ABI、资源、输入、存储及生命周期等检查，按问题定位适配层 |
| 验证与发布准备 | 记录模拟器或设备的验证范围，核对候选包、签名、材料和测试对象是否对应 |
| 用户交接与恢复 | 分别追踪登录、权限、设备、材料等阻塞，保存断点；完成后先核验再续接 |
| 审核与上线跟进 | 区分上传、提交、通过与实际发布，按授权处理退回整改及结果未知的操作 |
| 本地辅助工具 | `inventory` 盘点文件线索；`init` 新建台账；`check` 检查结构、证据路径、环境标签与哈希 |

例如旧计划写“待提交”，用户明确确认同一版本已上线，skill 会转为收尾计划并注明信息来源；缺少平台回执会列为证据待补，不据此重复提交。详见 [接手与状态核对](skills/harmonyos-pc-porting/references/resume.md)。

## 技术架构

| 组成 | 实现与职责 |
|---|---|
| Skill 入口与参考资料 | Markdown，供 agent 按任务加载，不绑定某一种应用技术栈 |
| 项目记录模板 | Markdown，承载阶段、候选身份、验证与交接记录 |
| 辅助工具 | Python 标准库，提供本地 CLI，无网络调用 |
| 可选阶段台账 | JSON，人工或 agent 填写；脚本检查完整性，不自动认证业务结论 |
| Codex 界面元数据 | `agents/openai.yaml`；其他宿主可忽略 |
| 工具测试 | Python `unittest`，使用临时目录与测试夹具 |

```text
ohos_skill/
├── skills/harmonyos-pc-porting/
│   ├── SKILL.md                 技能入口
│   ├── references/              路线、验证、发布、接手与交接
│   ├── assets/porting-plan.md   项目记录模板
│   ├── scripts/porting_helper.py
│   ├── agents/openai.yaml
│   └── LICENSE                  独立分发时保留
├── tests/                       辅助工具回归测试
├── research/                    官方资料与评估过程
├── CONTRIBUTING.md
└── LICENSE
```

agent 负责理解证据、选择下一动作和执行已授权工作；脚本负责可重复的结构与文件检查。`check` 的 `next_gate` 只是台账中首个 pending/blocked 阶段，可能意味着证据待补，不能当作自动重建、上传或提审指令。

## 常用命令

以下命令均从仓库根目录执行，`/path/to/project` 替换为实际工程路径：

```bash
# 盘点目标项目，JSON 输出到终端
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py inventory /path/to/project

# 可选：新建空白台账；父目录须存在，已有文件不会被覆盖
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py init /path/to/project/porting-workflow.json

# 填写台账后检查；--root 是证据文件的引用根目录
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py check /path/to/project/porting-workflow.json --root /path/to/project

# 查看命令参数
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py --help
```

已有项目可以继续用原 Markdown 记录，不必创建 JSON。空白台账的阶段均为 pending，执行 `init` 本身不会判断项目进度。

`check` 退出码：**0** 表示结构与证据完整性检查通过，仍可有未完成阶段；**1** 表示检查失败；**2** 表示参数或输入路径等调用错误。`inventory` 遍历出错时返回 1 并保留部分结果。工具不认证功能、合规或平台发布状态。

## 配置与测试

本仓库不需要 `.env`、API Key、数据库或后台服务。`CODEX_HOME` 仅影响上述 Codex 安装位置；执行 helper 不依赖它。

| 使用场景 | 需要什么；缺少时如何处理 |
|---|---|
| 阅读、评估与接手计划 | agent 能访问工程与记录；无法访问的内容明确列为未核验 |
| 构建鸿蒙应用 | 按项目准备 DevEco、SDK、原生工具链及依赖；缺少时继续可做的分析，交接具体环境条件 |
| 运行验证 | 匹配目标系统/API/ABI 的模拟器或设备；没有可用环境时保留未测项，不用构建成功替代 |
| 上传、提审或发布 | 对应账号权限、签名、材料与任务授权；只做检查或规划时不要求先完成这些操作 |

在仓库根目录运行工具测试：

```bash
python3 -B -m unittest discover -s tests -v
```

当前 19 项测试覆盖扫描边界、台账初始化、哈希与路径检查、证据环境及阻塞说明等。本地已在 Python 3.14 验证；其他 Python 版本的兼容性尚未建立测试矩阵。测试末尾显示 `OK` 表示工具用例通过，不表示真实应用移植或上架链路已通过。仓库目前未配置 CI，流程变更的验证方法见 [贡献指南](CONTRIBUTING.md)。

## 已知限制与常见问题

- **能自动移植任意桌面应用吗？** 不能。它提供可执行流程与辅助检查，具体技术方案、补丁和替代能力仍需逐项目验证。
- **一定需要真机吗？** 不一定，可以按验证范围使用匹配的模拟器；硬件相关能力和设备特有问题仍需对应环境。没有任何运行环境时只能推进可做部分。
- **用户登录后会自动继续吗？** 当前会话能观察或等待时按宿主机制续接，否则用户回复后继续。skill 不提供后台常驻、跨会话自动唤醒或持续审核监控。
- **工具没找到文件，是否说明没有产物？** 不是。`inventory` 默认最多扫描 5000 个普通文件，并跳过 `output/`、`build/`、依赖目录和符号链接；要沿项目记录定向核查这些位置。
- **台账检查通过，是否表示已经上架？** 不是。检查只涉及结构、文件、环境标签和哈希；实际进展与来源另记在计划中，用户口述不能冒充平台核验。
- **只能在 Codex 使用吗？** 文档和 Python 工具没有 Codex 专有 API 依赖；其他 agent 可读取使用，但自动发现、工具权限与完整执行效果需在对应宿主验证。

尚未建立节省工时或完整迁移成功率的系统性评估，也不保证商店审核结果。

## 文档地图

| 文档 | 何时查看 |
|---|---|
| [技能入口](skills/harmonyos-pc-porting/SKILL.md) | 使用 skill 的公共流程、阶段与交付要求 |
| [技术路线](skills/harmonyos-pc-porting/references/routes.md) | 根据技术栈选择适配方案 |
| [验证指南](skills/harmonyos-pc-porting/references/validation.md) | 制定功能与目标环境验证矩阵 |
| [发布流程](skills/harmonyos-pc-porting/references/release.md) | 准备签名、材料、审核整改与发布检查 |
| [接手与状态核对](skills/harmonyos-pc-porting/references/resume.md) | 继续已有项目或处理新旧记录冲突 |
| [交接与恢复](skills/harmonyos-pc-porting/references/handoffs.md) | 登录、权限、设备及平台等待 |
| [项目记录模板](skills/harmonyos-pc-porting/assets/porting-plan.md) | 保存计划、证据、候选身份与断点 |
| [来源索引](skills/harmonyos-pc-porting/references/sources.md) | 查阅官方与社区资料及其适用范围 |
| [评估记录](research/evaluation.md) / [流程检查](research/flow-review.md) / [官方资料调研](research/official-findings.md) | 查看设计依据、已做验证和未测部分 |

## 如何贡献

欢迎提交使用反馈、文档纠错、移植案例和工具改进。先看 [CONTRIBUTING.md](CONTRIBUTING.md)，其中说明了修改位置、问题复现、来源标注、验证方式和提交格式。

流程改动请提供具体场景与预期下一动作；脚本改动请验证相关行为。文档、模拟推演和真实环境实测分别记录，避免把一个项目的经验写成所有项目的强制要求。

## 许可证

本仓库的原创文档与脚本采用 [MIT License](LICENSE)，许可证文本见 [SPDX MIT](https://spdx.org/licenses/MIT.html)。单独复制或分发 skill 时，请一并保留其目录中的 `LICENSE`。

引用的第三方资料保留各自许可证与权利声明；本仓库的 MIT 许可不改变其授权。
