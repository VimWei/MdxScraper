## Advanced 标签页主题切换方案（设计与实施计划）

### 目标
- 在 Advanced 标签页提供“主题”切换能力，用户可在运行时一键切换 GUI 主题。
- 选择结果持久化到配置文件，启动时自动应用。
- 保持样式逻辑集中在 `ThemeLoader` 与 `apply_modern_styling`，降低维护成本。

### 范围
- GUI：Advanced 页新增主题选择控件与事件。
- MainWindow：读取/应用主题、监听并持久化变更。
- 设置：新增 `appearance.theme` 键，默认 `"default"`。
- 主题加载：沿用现有 `ThemeLoader`，基于 `*.qss` 和同名 `*.json` 的 `base_style`。

### 当前状态（基线）
- 主题文件：`src/mdxscraper/gui/styles/themes/default.qss`、`dark.qss` 等；可选 `default.json`、`dark.json` 用于 `base_style`（默认 Fusion）。
- 加载与应用：`MainWindow.apply_modern_styling()` 使用 `ThemeLoader` 应用基础样式和 QSS，但目前主题名写死为 `"default"`。
- Advanced 标签页：`AdvancedPage` 已有信号、布局与其它设置项（wkhtmltopdf 路径、数据目录）。

### 需求与设计
- 主题枚举
  - 扫描目录：`src/mdxscraper/gui/styles/themes/*.qss`，将文件名（stem）作为主题名（如 `default`、`dark`、`compact`）。
  - 无需硬编码，新增主题即插即用。

- 控件与交互（Advanced）
  - 在页首新增 `QLabel("Theme:") + QComboBox`。
  - 下拉框初始值为当前配置的主题；用户选择变更后即时应用。
  - 可选：增加“重置为默认”按钮。

- 持久化
  - 配置键：`appearance.theme`（字符串）。
  - 默认值：`"default"`。当配置缺失/无效或文件不存在时回退。
  - 读写通过 `SettingsService` → `ConfigManager`。

- 运行时应用
  - `AdvancedPage` 新增信号：`theme_changed(str)`。
  - `MainWindow` 监听：`on_theme_changed(theme: str)` → 调用 `apply_modern_styling(theme)`，然后 `settings.set("appearance.theme", theme); settings.save()`。
  - `apply_modern_styling(theme)`：
    - `ThemeLoader.apply_base_style(app, theme)`（读取 `themes/<theme>.json` 的 `base_style`，默认 `Fusion`）。
    - `self.setStyleSheet(theme_loader.load_theme(theme))`（读取 `themes/<theme>.qss`）。
    - 若 `*.qss` 加载失败，回退到 `default`。

### 文件与接口改动点
- Advanced 页（新增 UI 与信号）
  - 路径：`src/mdxscraper/gui/pages/advanced_page.py`
  - 新增：主题选择控件、目录扫描填充、`theme_changed: Signal(str)`；选择变更时 `emit`。

- 设置服务（读写配置）
  - 路径：`src/mdxscraper/gui/services/settings_service.py`
  - 使用：`get("appearance.theme", "default")` 与 `set("appearance.theme", theme)`。

- 主窗口（加载与即时应用）
  - 路径：`src/mdxscraper/gui/main_window.py`
  - `__init__`：启动读取主题，设置 Advanced 下拉框当前值，调用 `apply_modern_styling(theme)`。
  - 连接 `self.tab_advanced.theme_changed.connect(self.on_theme_changed)`；在处理函数中立即应用并持久化。
  - 将 `apply_modern_styling()` 改为接受 `theme_name: str`（默认 `"default"`）。

- 主题加载器（保持现状，保证回退）
  - 路径：`src/mdxscraper/gui/styles/theme_loader.py`
  - `load_theme(theme_name)`/`apply_base_style(app, theme_name)` 已具备；确保读取失败时返回空串并由调用方回退。

### 兼容性与回退策略
- 配置缺失/无效 → 使用 `"default"`。
- `themes/<theme>.qss` 读取失败 → 尝试 `default.qss`。
- `themes/<theme>.json` 缺失或格式错误 → `Fusion`。
- 始终优先保证应用可见、可操作（避免黑屏/无样式）。

### 实施步骤（按序执行）
1) Advanced 页：新增主题下拉框与信号；实现扫描 `themes/*.qss` 并填充；选择变更时 `emit`。
2) MainWindow：
   - `__init__` 读取 `appearance.theme`，调用 `apply_modern_styling(theme)`；
   - 连接 `theme_changed` → 立即应用与 `settings.set/save`；
   - 修改 `apply_modern_styling(theme_name: str = "default")`。
3) SettingsService：无新方法，直接用现有 `get/set/save`。
4) 回退与健壮性：在 `on_theme_changed` 与初始化应用处加入回退到 `default` 的逻辑。
5) 手动与自动测试：见下方测试用例。

### 测试用例
- 启动加载：无配置/非法值 → 自动应用 `default`，UI 正常。
- 切换主题：从 `default` → `dark` 立即生效，重启后仍为 `dark`。
- 文件缺失：删除 `dark.qss` 后选择 `dark` → 自动回退 `default`，无崩溃。
- JSON 缺失：`dark.json` 不存在 → 仍能应用 QSS，基础样式为 `Fusion`。
- 目录扩展：新增 `compact.qss` → 下拉框自动出现 `compact`，选择后生效。

### 风险与缓解
- 非法 QSS 导致控件异常：通过回退与最小化作用域（setStyleSheet 全局但可快速切回）缓解。
- 第三方主题质量参差：不在内置列表中做保证，建议仅展示扫描结果；提供“重置为默认”。

### 里程碑与预估
- 开发：0.5 天（UI+连接+回退）。
- 测试：0.5 天（覆盖主要场景）。
- 文档：本方案即交付文档，后续补充 README 节点（可选）。

### 交付物
- Advanced 页主题选择功能（UI、运行时应用、持久化）。
- 配置键 `appearance.theme` 写入 `data/configs/config_latest.toml`。
- 保持对新增主题文件的零改动支持（扫描式）。


