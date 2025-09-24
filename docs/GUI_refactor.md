# MdxScraper GUI 重构与模块化建议

（基于 src/mdxscraper/gui/main_window.py）

## 一、概览与目标
### 现状速览
- 主窗口承担：窗体壳、表单输入（Basic）、多标签页（Image/PDF/CSS/About）、预设管理、配置导入导出、样式、任务执行、日志与进度、线程管理等。
- `ConversionWorker` 在同文件定义并直接调用核心逻辑；UI 与业务/耗时逻辑耦合明显。

### 存在的问题
- 单一文件多职责，难维护、难测试；预设/配置/导出散落在 UI。
- 子线程与 UI 交织，阻塞风险与可扩展性差；页面与全局操作职责混杂。

### 设计目标
- 主窗口变薄：仅负责装配与编排，不承载业务与耗时逻辑。
- 分层清晰：UI（展示/交互）→ Service（业务）→ Worker（耗时）。
- 信号解耦：以 Signal/Slot 解耦部件与线程；页面只发配置变更，全局操作集中到 `CommandPanel`。
- 组件复用：抽取 `FilePicker/ProgressPanel/CommandPanel` 等可复用组件，减少重复代码。

## 二、架构总览
### 目录结构（建议）
- `src/mdxscraper/gui/`
  - `app.py`（入口装配）
  - `main_window.py`（主窗口壳与编排）
  - `pages/`（`basic_page.py`、`image_page.py`、`pdf_page.py`、`css_page.py`、`advanced_page.py`、`about_page.py`）
  - `components/`（`command_panel.py`、`file_picker.py`、`progress_panel.py`）
  - `services/`（`settings_service.py`、`presets_service.py`、`export_service.py`）
  - `workers/`（`conversion_worker.py`）
  - `locales/`（多语言资源，如 `en_US.qm`、`zh_CN.qm`）
  - `styles/`（可选）与 `assets/`

### 角色职责（要点）
- MainWindow：装配页面与组件、注入服务、连接信号、启停 Worker、`update_tab_enablement()`。
- Pages：
  - Basic：输入/字典/输出与基础选项（不含全局按钮）。
  - Image：图像选项；`syncFromConfig()/syncToConfig()`；发 `imageConfigChanged`。
  - PDF/CSS：预设选择/编辑/保存；经 `PresetsService`；发 `*TextChanged`。
  - Advanced：with_toc 选项、wkhtmltopdf_path 相关配置绑定（经 `SettingsService`）。
  - About：纯展示。
- Components：
  - CommandPanel：全局主操作（恢复/导入/导出、Scrape）+ 进度 + 日志；信号 `restoreRequested/importRequested/exportRequested/scrapeRequested`；方法 `setProgress/appendLog/setEnabled`。
  - FilePicker/ProgressPanel：复用小部件。
- Services：
  - SettingsService：封装 `ConfigManager`（读写/校验/保存加载），隐藏 `_config` 细节。
  - PresetsService：预设 I/O 与 TOML 解析。
  - ExportService：构建导出参数并调用 `core.converter`。
- Worker：`ConversionWorker` 只做耗时任务；发 `finished_sig/error_sig/log_sig`（可选 `progress(int)`）；不直接操作 UI。

## 三、交互与实施规则
### 单向流程
1) Pages/CommandPanel 发信号 → MainWindow 编排
2) MainWindow 调用 Services 或启动 Worker
3) Worker/Services 回传 → MainWindow → CommandPanel 展示进度与日志
4) MainWindow 基于输出后缀更新标签可用性

### 信号清单
- Pages → MainWindow：`inputChanged/dictionaryChanged/outputChanged/optionsChanged/imageConfigChanged/pdfTextChanged/cssTextChanged/advancedChanged`
- CommandPanel → MainWindow：`restoreRequested/importRequested/exportRequested/scrapeRequested`
- Worker → MainWindow（再转 UI）：`log_sig/finished_sig/error_sig`（可选 `progress(int)`）

### 依赖注入
`MainWindow(SettingsService, PresetsService, ExportService)`；页面通过构造参数接收所需服务，不在内部创建。

### 错误与进度规范
- 错误：Service/Worker 捕获 → 文本化 → `error_sig(str)`；UI 仅展示，不在子线程弹窗。
- 日志：统一前缀（✅/⚠️/❌），避免与进度条重复；`CommandPanel` 负责展示与滚动。
- 进度：阶段化（准备/解析/导出/收尾）建议份额 10/40/40/10，可按格式微调。

### 启用规则
将输出后缀到标签可用性的判定抽象为纯函数，由服务层提供并覆盖测试；本文不展开具体实现。

### 代码风格与约束
- UI 与服务层分离：页面不直接读写 `ConfigManager`，统一通过 `settings_service`；页面逻辑短小、以信号为边界。
- 类型与错误处理：对外 API 明确类型；异常在服务/worker 层封顶并通过信号/返回值向上冒泡，UI 只负责提示。
- 样式集中化：`theme_loader.py` 统一设置 Fusion 与 QSS，避免在多个页面重复调用 `setStyleSheet`。

## 四、分步实施计划（TODOS)
1. 抽出 Worker
   - 将 `ConversionWorker` 迁至 `gui/workers/conversion_worker.py`；主窗口改为导入使用，信号保持不变。
2. 抽出服务
   - 新增 `gui/services/settings_service.py`（包装 `ConfigManager`）、`gui/services/presets_service.py`（预设 I/O/TOML）、`gui/services/export_service.py`（参数构建与调用 `core.converter`）。
3. 抽出组件
   - 实现 `gui/components/command_panel.py`（全局操作+进度+日志）、`gui/components/progress_panel.py`、`gui/components/file_picker.py`；替换主窗口底部区域。
   - 在 `CommandPanel` 增加“清空日志”“复制日志”操作（按钮/菜单），并暴露相应信号或方法供主窗口调用。
4. 拆分页面
   - 将 Basic/Image/PDF/CSS/About 拆到 `gui/pages/*`，主窗口负责装配与信号桥接；保留/集中 `update_tab_enablement()`。
5. 清理与类型化
   - 移除主窗口中与服务层重复的解析/校验；统一类型注解；为关键纯函数/服务补最小单测（预设解析、图像参数构造、输出命名、启用规则）。
6. 新增 Advanced 页
   - 在 `gui/pages/advanced_page.py` 实现 with_toc 选项与 wkhtmltopdf_path 配置绑定（经 `SettingsService`）。
7. 多语言界面（i18n）
   - 引入 `QTranslator`；新增 `gui/locales/`，提供基础翻译文件（如 `en_US`, `zh_CN`）。在入口或 `CommandPanel` 提供语言切换（菜单或设置项）。

以上方案可渐进落地，每步完成后即可提交，确保回滚成本低且功能持续可用。
