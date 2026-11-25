# 官方与社区资料索引

核对日期：2026-11-16。按正在做的任务读取相关条目，不要求每次通读。华为商业 HarmonyOS 文档用于目标应用开发与商店分发；OpenHarmonyPCDeveloper 资料适用于对应社区渠道，不能代替华为平台的发布政策。

本文保存可追溯入口与适用范围。具体接口签名、最低 API、工具链路径、大小/尺寸、支持地区和控制台字段在执行时重新核对目标版本。抓取失败不能当作已核实正文。

## 项目定位与路线

- [鸿蒙电脑已有应用适配](https://developer.huawei.com/consumer/cn/multidevice/pc/adapt/)：桌面窗口、键鼠、焦点与从模拟器到目标设备的验证安排。
- [模块配置文件](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/module-configuration-file/)：`deviceTypes` 等应用模块声明，PC 使用 `2in1`；还需核对实际包中各模块。
- [跨平台开发方案](https://developer.huawei.com/consumer/cn/doc/guidebook/solution-0000002784651007/) 与 [编程语言](https://developer.huawei.com/consumer/cn/doc/guidebook/programming-language1-0000002593254720/)：了解框架/语言路线和支持来源，不能据此推断每个第三方插件已适配。

## Native、Web 与系统能力

- [NDK 开发导读](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/ndk-development-overview/) 与 [HarmonyOS ABI](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ohos-abi/)：C/C++ 工具链、目标 ABI 和互操作。新旧文档工具链名称存在变化，应核对安装的 SDK。
- [CMake 三方库示例](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/toolchain-cmake-build-project/) 与 [Hvigor CPP 配置](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/ide-hmos-hvigor-cpp/)：按工程版本配置原生构建、ABI 和依赖。
- [XComponent](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/napi-xcomponent-guidelines/)：原生绘制/交互接口依据，不是 GTK 官方兼容性认证。
- [ArkWeb 简介](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/web-component-overview/)、[页面调用应用](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/web-in-page-app-function-invoking/)、[应用调用页面](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/web-in-app-frontend-page-function-invoking)：Web 宿主与双向桥接；Electron 主进程能力需另行适配。
- [文件选择器](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-file-picker/)：用户选取文件的系统接口，验证取消、错误及应用可访问的结果。

## 构建、签名与设备验证

- [应用包结构](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/application-package-structure-stage/) 与 [命令行构建](https://developer.huawei.com/consumer/cn/doc/doccenter-deveco-studio/ide-hmos-command-line-building-app/)：了解 HAP/HSP/HAR/APP 及本项目的构建入口。
- [DevEco 发布应用](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-publish-app/)、[发布证书](https://developer.huawei.com/consumer/cn/doc/app/agc-help-add-releasecert-0000001946273961)、[发布 Profile](https://developer.huawei.com/consumer/cn/doc/app/agc-help-add-releaseprofile-0000001914714796)：依据当前工具版本确定签名与发布方式。
- [hdc](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/hdc/) 与 [云调试](https://developer.huawei.com/consumer/cn/doc/app/agc-help-clouddebug-debugapp-0000002289629821/)：安装、调试与设备工具；现行文档存在 APP 安装支持，不能沿用“.app 永远不能安装”的旧结论。签名、设备和系统限制仍须核对。

## 华为应用市场

- [创建应用](https://developer.huawei.com/consumer/cn/doc/App/agc-help-create-app-0000002247955506/)：账号下应用身份、APP ID 与包名。
- [发布指引](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-guide-0000002287176372) 与 [发布准备](https://developer.huawei.com/consumer/cn/doc/App/agc-help-release-app-prepare-0000002306311921/)：正式应用包、信息、材料、测试与提交阶段。
- [上传软件包](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-upload-pkg-0000002277983368/) 与 [配置支持设备](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-devicetype-0000002271592112)：包校验、分发设备和地区，升级时的设备范围限制亦需复查。
- [视觉素材规范](https://developer.huawei.com/consumer/cn/doc/App/agc-help-app-visual-asset-spec-0000002277607976/)：按应用类型和设备核实图标、截图数量/尺寸/格式/大小。2026-11-23 已读取普通应用 PC/2in1 对应表；规格基线和采集检查步骤见 [商店素材指南](store-assets.md)，每次上传/提审前仍须重新核对。
- [应用图标配置](https://developer.huawei.com/consumer/cn/doc/doccenter-feature-dev/bpta-app-icon-configuration/)：核对目标 SDK 下包内图标资源及引用；商店上传图标的尺寸不能直接替代包内配置要求。
- [应用图标设计规范](https://developer.huawei.com/consumer/cn/doc/design-guides/application-icon-0000001953444009/) 与 [配置应用启动页](https://developer.huawei.com/consumer/cn/doc/harmonyos-Guides/launch-page-config/)：2026-11-25 核对电脑双层图标规格、背景透明度及简易/增强启动页字段；源资源、最终包和实际显示分别验收。图标配置与启动页部分通过官方搜索正文核对，页面直接读取曾超时。
- [工程级 build-profile.json5](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-hvigor-build-profile-app/)：2026-11-25 核对产品的签名方案引用及 `appWithSignedPkg` 语义；按 DevEco 版本和分发用途选择，见 [签名配置与产物核验](signing.md)。
- [隐私说明](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-privacy-desc-0000002313477969)、[隐私声明](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-privacy-state-0000002278878296)、[资质审核要求](https://developer.huawei.com/consumer/cn/doc/App/80301/)：按实际数据处理、权限、地区、类目和主体准备对应材料。
- [APP 备案指引](https://developer.huawei.com/consumer/cn/doc/doccenter-submission/50130/)：按应用、地区与发布主体确认适用性和前置材料；不假设社区自动代办。
- [提交审核](https://developer.huawei.com/consumer/cn/doc/app/agc-help-release-app-submit-0000002286180890) 与 [升级应用版本](https://developer.huawei.com/consumer/cn/doc/app/agc-help-update-version-0000001146436549/)：跟踪审核和后续版本，不从上传状态推断上线。

## 可选：OpenHarmonyPCDeveloper 社区

- [共建指导](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/contribute/共建指导.md)：已有社区仓库则 fork 后提 PR；无仓库则申请，等管理员在 issue 回复仓库地址后再贡献代码。
- [建仓申请模板](https://gitcode.com/OpenHarmonyPCDeveloper/community/blob/master/NewRepository.md) · [建仓 issue 入口](https://gitcode.com/OpenHarmonyPCDeveloper/community/issues/create/choose)：按当前模板准备申请；先查组织仓库及 community 已有 issue，避免重复建仓。
- [开发文档索引](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/README_zh.md)：嵌入 CPython、Node.js、Java 等路线及三方库适配；匹配所用仓库提交与版本后再采用。
- [开源应用上架指南](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/contribute/开源应用上架指南.md)：该社区的命名和描述模板，来源说明不替代商店授权审核。
- [贡献指导](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/contribute/rules/贡献指导.md)：该社区适配项目根目录 `README.OpenSource` 等贡献要求。
- [发布规范](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/contribute/rules/发布规范.md)、[命名指导](https://gitcode.com/OpenHarmonyPCDeveloper/docs/blob/main/contribute/rules/命名指导.md)：社区 README/License/ChangeLog、仓库命名和版本要求，作用域限于此渠道。

共建指导与申请模板于 2026-11-22 通过 GitCode 公开 Contents API 核对，模板另由 raw 内容交叉核对；issue 入口由共建指导链接确认，未登录或实际提交。指南中的审核时间描述不作为本 skill 对管理员响应时间的承诺。

## 获取与有效性限制

本次调研的 GitCode 正文由公开 raw/Contents API 读取；部分华为页面由相同文档的可读别名或官方搜索正文交叉核对。部分原链接超时或只返回标题；社区发布规范链接的 `质量要求.md` 在对应位置返回 404，未据此补造要求。

未登录开发者中心验证用户账号权限、资质、当前可选字段或审核状态。进行真正提交时仍需要按目标账号和应用复核。
