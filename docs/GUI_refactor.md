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
### 目录结构（实际实施）
- `src/mdxscraper/gui/`
  - `main_window.py`（主窗口壳与编排）
  - `config_dialog.py`（配置对话框，暂未使用）
  - `pages/`（`basic_page.py`、`image_page.py`、`pdf_page.py`、`css_page.py`、`advanced_page.py`、`about_page.py`）
  - `components/`（`command_panel.py`、`file_picker.py`、`progress_panel.py`）
  - `services/`（`settings_service.py`、`presets_service.py`、`export_service.py`）
  - `workers/`（`conversion_worker.py`）
  - `assets/`（应用图标等资源）
  - `locales/`（多语言资源，待实施）
  - `styles/`（样式文件，待实施）

### 角色职责（要点）
- MainWindow：装配页面与组件、注入服务、连接信号、启停 Worker。
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
- Worker：`ConversionWorker` 只做耗时任务；发 `finished_sig/error_sig/log_sig`（可选 `progress_sig(int)`）；不直接操作 UI。

## 三、交互与实施规则
### 单向流程
1) Pages/CommandPanel 发信号 → MainWindow 编排
2) MainWindow 调用 Services 或启动 Worker
3) Worker/Services 回传 → MainWindow → CommandPanel 展示进度与日志

### 信号清单（实际实施）
- BasicPage → MainWindow：直接连接控件信号（`editingFinished`、`clicked`、`stateChanged`）
- ImagePage → MainWindow：`width_changed/zoom_changed/background_changed/jpg_quality_changed/png_optimize_changed/png_compress_changed/png_transparent_changed/webp_quality_changed/webp_lossless_changed/webp_transparent_changed`
- PDF/CSS Pages → MainWindow：`preset_changed/save_clicked`
- AdvancedPage → MainWindow：`with_toc_changed/wkhtmltopdf_path_changed`
- CommandPanel → MainWindow：`restoreRequested/importRequested/exportRequested/scrapeRequested`
- Worker → MainWindow：`log_sig/finished_sig/error_sig`

### 依赖注入（实际实施）
- `MainWindow(project_root)` 在内部创建服务实例：`SettingsService`、`PresetsService`；`ExportService` 在 `ConversionWorker` 中创建。
- 页面通过构造参数接收 `MainWindow` 引用，通过主窗口访问服务；页面不直接持有服务状态。
- 服务生命周期：在 `MainWindow.__init__` 中创建并管理，确保服务间共享 `ConfigManager` 实例。

### 错误与进度规范
- 错误：Service/Worker 捕获 → 文本化 → `error_sig(str)`；UI 仅展示，不在子线程弹窗。
- 日志：统一前缀（✅/⚠️/❌），避免与进度条重复；`CommandPanel` 负责展示与滚动。
- 所有错误/警告/信息统一通过 `log_sig` 到 `CommandPanel.appendLog()`；子线程不弹框；主线程仅在必要时使用 `QMessageBox`（如“必须先选择输出文件”）。
- 运行前集中校验：Scrape 触发时先调用 `SettingsService.validate()`（输入/字典/输出/后缀/启用规则），不通过则仅记录日志并轻量提示，不启动子线程。
- 进度：阶段化（准备/解析/导出/收尾）建议份额 10/40/40/10，可按格式微调。让 `ExportService` 给出阶段常量或在 `ConversionWorker` 内集中管理，避免散落魔法数。
- 进度信号命名一致性：文档用统一名称（建议 `progress_sig(int)`），与 `CommandPanel.setProgress(int)` 对应。

### 代码风格与约束
- UI 与服务层分离：页面不直接读写 `ConfigManager`，统一通过 `settings_service`；页面逻辑短小、以信号为边界。
- 类型与错误处理：对外 API 明确类型；异常在服务/worker 层封顶并通过信号/返回值向上冒泡，UI 只负责提示。
- 样式集中化：目前 `apply_modern_styling()` 仍在 `MainWindow` 中；未来可拆到 `theme_loader.py`（Fusion 启用 + QSS）统一管理。
- 命名与常量：输出类型、页签名称、阶段名称提取为 enums 或常量，避免硬编码重复。

### ConfigManager 使用与封装（已实施）
- ✅ UI/Worker 层不再直接访问 `cm._config`、`_resolve_path` 等内部属性，统一通过 `SettingsService` 公开方法。
- ✅ 主窗口关闭时通过 `SettingsService.persist_session_state()` 保存编辑器内容。
- 自动重命名开关：提供 `autoRenameOutputOnInputChange` 设置（默认开启），由 `SettingsService` 执行重命名策略；页面仅发出 `inputChanged`，不直接改写输出。
- 文件对话框策略：起始目录与默认文件名由 `SettingsService` 提供 helper（如 `get_start_dir(kind)`、`suggest_output_filename(input_path)`），避免在各页面分散实现。

### 预设与 TOML 解析（已实施）
- ✅ TOML 解析集中在 `PresetsService`（`parse_pdf_preset`、`parse_css_preset`）。
- ✅ 预设 I/O 操作通过 `PresetsService`（`iter_presets`、`load_preset_text`、`save_preset_text`）。
- ✅ 页面仅负责展示文本与触发保存/选择事件。
- 预设加载失败时的错误信息统一经 log_sig，不要在子线程里弹窗。

#### 统一预设选择的加载与保留
- 问题回顾：应用启动/导入/恢复时如果在 `reload_presets()` 内自动选择默认项（如 `default [built-in]`），会通过 `on_*_preset_changed` 覆盖已保存的 `preset_label`。
- 解决方案：
  - 调整初始化顺序：`reload_presets(auto_select_default=False)` → `sync_from_config()`，由后者恢复选择。
  - 保存预设后：`reload_presets(auto_select_default=False)` 并调用 `sync_pdf_to_config()/sync_css_to_config()`，保持当前选择与文本。
- 验收：
  - 重启应用/导入/恢复后，PDF/CSS 预设选择与 `config_latest.toml` 一致，不被默认项覆盖。

### 参数同步（已统一）
- 统一数据模型：为每个页面建立数据类 `BasicConfig/ImageConfig/AdvancedConfig/PdfConfig/CssConfig`。
- 服务封装：`SettingsService` 提供 `get_*_config()/update_*_config()`，屏蔽底层 `ConfigManager`。
- 页面职责：仅实现 `get_config()/set_config()` 与控件绑定，不直接读写配置树。
- 主窗口职责：`sync_from_config()` 统一拉取配置到页面；导出/运行/关闭前统一回写 `sync_*_to_config()`。
- 验收：关闭/导出/运行前可回写并持久化；启动/导入/恢复后按配置正确显示。

### 线程安全与信号规范（已实施）
- ✅ ConversionWorker 保持无 UI 依赖，只通过 `finished_sig/error_sig/log_sig` 回传；日志/进度展示统一在 `CommandPanel`。
- 取消/停止：`CommandPanel` 提供"停止"按钮；`ConversionWorker` 支持 `requestInterruption()` 或轮询中断标志，并在关键安全点快速退出，发出适当完成/错误信号并执行清理。

## 四、分步实施计划（已完成）
1. ✅ **抽出 Worker**
   - 将 `ConversionWorker` 迁至 `gui/workers/conversion_worker.py`；主窗口改为导入使用，信号保持不变。
   - 验收：main_window.py 不再定义 ConversionWorker；主窗口仅导入并连接信号；原有功能不回归。

2. ✅ **抽出 Services**
   - 新增 `gui/services/settings_service.py`（包装 `ConfigManager`）、`gui/services/presets_service.py`（预设 I/O/TOML）、`gui/services/export_service.py`（参数构建与调用 `core.converter`）。
   - 验收：UI 不再直接访问 ConfigManager 内部；预设读取/保存、TOML 解析在 PresetsService；导出参数构建在 ExportService；配置 CRUD 与校验在 SettingsService。

3. ✅ **抽出 Components**
   - 实现 `gui/components/command_panel.py`（全局操作+进度+日志）、`gui/components/progress_panel.py`、`gui/components/file_picker.py`；替换主窗口底部区域。
   - 在 `CommandPanel` 增加"清空日志""复制日志"操作（按钮/菜单），并暴露相应信号或方法供主窗口调用。
   - 验收：底部区域替换为 CommandPanel；支持"清空日志/复制日志"；提供 setEnabled/setProgress/appendLog API。

4. ✅ **拆分页面**
   - 将 Basic/Image/PDF/CSS/About 拆到 `gui/pages/*`，主窗口负责装配与信号桥接。
   - 验收：Basic/Image/PDF/CSS/About 全部独立文件；页面仅发信号与读写自身控件；主窗口编排，标签页始终启用。

5. ✅ **新增 Advanced 页**
   - 在 `gui/pages/advanced_page.py` 实现 with_toc 选项与 wkhtmltopdf_path 配置绑定（经 `SettingsService`）。
   - 验收：with_toc 与 wkhtmltopdf_path 与配置绑定；能被导出并正确影响导出行为。

6. ✅ **清理与类型化**
   - 移除主窗口中与服务层重复的解析/校验；统一类型注解；为关键纯函数/服务补最小单测（预设解析、图像参数构造、输出命名、启用规则）。
   - 验收：无 _config 越层访问；关键函数具备类型注解；新增的小型单测通过。

7. ✅ **统一页面同步模式**（本次更新）
   - 为 Basic/Image/Advanced/PDF/CSS 引入数据类；在 `SettingsService` 暴露 `get/update_*_config`；页面实现 `get_config/set_config`。
   - `MainWindow` 改为统一的 `sync_from_config()` 和 `sync_*_to_config()`；导出/运行/关闭前统一回写；启动/导入/恢复时统一拉取。
   - 处理预设选择覆盖：`reload_presets(auto_select_default=False)`，由 `sync_from_config()` 负责恢复。
   - 验收：应用重启/导入/恢复后，PDF/CSS 预设选择保持一致；各页面状态与配置一致；测试通过。

8. 🔄 **多语言界面（i18n）** - 待实施
   - 引入 `QTranslator`；新增 `gui/locales/`，提供基础翻译文件（如 `en_US`, `zh_CN`）。在入口或 `CommandPanel` 提供语言切换（菜单或设置项）。
   - 验收：语言切换即时或下次启动生效，布局不破；关键字符串已纳入翻译资源。

以上方案可渐进落地，每步完成后即可提交，确保回滚成本低且功能持续可用。
