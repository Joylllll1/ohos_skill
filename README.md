<div align="center">

# HarmonyOS PC 移植与上架助手

**辅助桌面应用移植到 HarmonyOS PC 的 Agent Skill，覆盖项目评估、工程接续、构建验证与上架发布。**

![Agent Skill](https://img.shields.io/badge/Agent-Skill-2563EB)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[快速开始](#快速开始) · [能做什么](#能做什么) · [文档](#文档) · [贡献与许可](#贡献与许可)

</div>

根据项目的语言、架构和依赖制定移植路线，也能接手已经做了一半的工程。通过流程说明、参考资料、计划模板和轻量检查工具，让 agent 查清现状、推进任务，并保存可继续执行的记录。

## 快速开始

### 安装

准备 Node.js 22.20+（含 npm/npx）和 Git。在待移植项目目录运行，按提示选择要安装到的 agent：

```bash
npx skills add Joylllll1/ohos_skill --skill harmonyos-pc-porting
```

默认安装到当前项目。如果希望在 Codex 的多个项目中使用，可以全局安装：

```bash
npx skills add Joylllll1/ohos_skill --skill harmonyos-pc-porting -a codex -g
```

安装方式与参数见 [Skills CLI 文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。也可下载仓库，让 agent 直接读取 `skills/harmonyos-pc-porting/SKILL.md`，无需安装 CLI。

### 使用

在能读取目标项目文件、且已加载技能的 agent 会话中发送：

```text
使用 $harmonyos-pc-porting 接手当前工程。
先检查代码、已有产物与移植记录，整理当前进度和下一步计划。
先不要修改应用代码、上传或提交审核。
```

agent 会给出**当前阶段、判断依据、剩余工作和接续计划**。只做评估不需要先准备 DevEco 或真机；构建、运行验证及发布时，再按项目补齐工具、设备和账号条件。

skill 的执行能力取决于宿主，不提供后台监控，也不保证任意项目都能自动完成移植或通过审核。

## 能做什么

| 能力 | 说明 |
|---|---|
| 评估移植路线 | 拆分界面、核心逻辑、运行时和平台依赖，优先验证关键难点 |
| 接手续作 | 区分开发、候选与线上版本，处理旧记录和最新状态的冲突 |
| 构建与验证 | 核对工具链、依赖、包与测试记录，明确已测和未测范围 |
| 上架与整改 | 整理签名、材料与审核反馈，按授权推进提交和发布 |
| 交接与恢复 | 遇到登录、权限或设备问题时保存断点，用户完成后核验并继续 |

另附 Python 标准库工具，支持文件盘点、空白台账创建和证据完整性检查。在仓库根目录运行：

```bash
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py inventory /path/to/project
python3 skills/harmonyos-pc-porting/scripts/porting_helper.py --help
```

盘点结果以 JSON 输出到终端。工具检查通过不等于应用可用或已经上架；阶段判断仍需核对具体证据。

## 文档

- [技能入口](skills/harmonyos-pc-porting/SKILL.md)：完整工作流程与工具用法。
- [技术路线](skills/harmonyos-pc-porting/references/routes.md) · [验证指南](skills/harmonyos-pc-porting/references/validation.md) · [发布流程](skills/harmonyos-pc-porting/references/release.md)
- [接手与状态核对](skills/harmonyos-pc-porting/references/resume.md) · [交接与恢复](skills/harmonyos-pc-porting/references/handoffs.md)
- [项目记录模板](skills/harmonyos-pc-porting/assets/porting-plan.md) · [官方来源索引](skills/harmonyos-pc-porting/references/sources.md)
- [验证记录](research/evaluation.md) · [流程检查](research/flow-review.md)

## 贡献与许可

欢迎提交使用反馈、文档修订和工具改进，修改与测试方法见 [贡献指南](CONTRIBUTING.md)。

原创文档与脚本采用 [MIT License](LICENSE)。分发 skill 时请保留其目录中的许可证；第三方资料保留各自的许可与权利声明。
