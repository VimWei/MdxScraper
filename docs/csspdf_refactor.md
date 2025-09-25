## CSS/PDF 预设强绑定改造方案（中文版）

### 目标
- 让 `preset_label` 与 `preset_text` 强绑定、保持同步，消除“名实不符”。
- 配置文件只保存 `preset_label`，不再保存 `preset_text`，减小配置体积并简化语义。
- 启动/导入/运行时，均基于 `preset_label` 对应的文件内容工作，保证可复现性。
- 保留“编辑即所见”的直觉，但通过统一的 `Untitled` 流程将未命名修改安全落盘。

### 现状问题
- 配置臃肿：`pdf.preset_text`、`css.preset_text` 将全文写入配置。
- 预设失效：更新预设文件后，旧配置仍引用历史 `preset_text`。
- 语义割裂：`preset_label` 不一定对应当下使用的内容，给用户造成困惑。

### 新行为（规范）
- 持久化（配置）
  - 仅保存 `pdf.preset_label` 与 `css.preset_label`；不保存编辑器文本。
  - 应用退出、导出配置时，始终只写入 label。

- 加载（启动/导入）
  - 根据保存的 `preset_label`，从文件加载内容到编辑器。
  - 若找不到对应文件：进入 `* Untitled` 状态；编辑器留空，不加载可能存在的 `Untitled.toml`。

- 编辑与脏态
  - 编辑框有变更即视为脏态，组合框显示为 `* Untitled`（仅显示，不进入下拉列表）。
  - 不再提示“是否保存”，也不打断操作。

- Untitled 的统一规则
  - Scrape：若当前为脏态，先自动写入 `data/configs/{css|pdf}/Untitled.toml`（覆盖），并将当次运行使用该文件内容。
  - 退出：若当前为脏态，自动写入 `Untitled.toml`（覆盖），并将配置的 `preset_label` 固定为 `Untitled`。
  - 导入配置：若当前为脏态，先无提示地将编辑内容写入 `Untitled.toml`（覆盖），再执行导入；导入后按新配置的 label 加载。
  - 以上行为确保“编辑即所见”，同时始终有可靠的落盘位置与恢复路径。

- Export（导出配置）- 冻结 Untitled（必须）
  - 当导出配置且当前 `preset_label` 为 `Untitled` 时：
    - 立即在 `data/configs/{css|pdf}` 下创建快照文件：`Untitled-YYYYMMDD-HHMM.toml`，内容取自当前编辑器（必要时先落盘 Untitled 再复制）。
    - 在导出的配置中，将 `preset_label` 指向该快照文件的 label（即快照的文件名，不含扩展名）。
    - 这样他人导入该配置也能获得完全一致的效果，无需额外提示或二次导出。

- 运行（Scrape）的一致性
  - 一律按“文件内容”工作：若脏态，先落盘 Untitled，再从相应文件（Untitled 或已命名预设）读取内容参与运行。

### UI 变更
- 组合框（Preset 下拉）：
  - 继续列出所有预设标签（内置与用户）。
  - 编辑时显示 `* Untitled`（仅显示态，不加入列表）。
- 按钮：
  - 保留 `Save`（保存/另存为皆通过对话框完成）。
  - 不新增 `New` 与 `Delete`（清空直接编辑即可；删除在外部执行）。
  - 新增 `Refresh`（刷新预设列表，重新扫描用户目录并尽量保留当前选中），位置在 `Save` 按钮的左侧。
- 其他：
  - 不在 CSS/PDF 页增加 `Open Folder`，改为在 `Advanced` 页提供“打开用户数据目录”的统一入口。

### 边界与回退
- 找不到 label 对应的文件：
  - 进入 `* Untitled`，编辑器留空。
- 内置 vs 用户预设：
  - 内置位于 `src/mdxscraper/config/{css_styles|pdf_options}`，只读；
  - 用户预设位于 `data/configs/{css|pdf}`，`Refresh` 时重扫。
- 语法/解析失败：
  - 不中断流程，进入 `* Untitled`，编辑器留空，并记录日志。

### 服务与模型改动
- `SettingsService`
  - `get_pdf_config`/`get_css_config` 仅返回/持久化 `preset_label`。
  - 移除 `*.preset_text` 的读写。
- `PresetsService`
  - 维持“枚举/加载/保存文本”能力；新增：安全生成 `Untitled-YYYYMMDD-HHMM.toml` 快照的工具方法。
- `MainWindow`
  - 停止把编辑器文本写入配置。
  - 处理脏态：`textChanged` → 显示 `* Untitled`；
  - `Scrape`/`closeEvent`/`import_config`：若脏态，先无提示写入 `Untitled.toml`（覆盖）。
  - `export_config`：若 `label=Untitled`，创建快照并在导出内容中使用该快照 label。
  - `Refresh`：重扫预设、尽量保持当前选择；若消失则按“边界与回退”。
- `ConversionWorker`/`ExportService`
  - 读取文本的来源改为：按当前有效 label 对应的文件内容（脏态时先确保 Untitled 已落盘）。

### 数据流（新的）
- 启动/导入 → 读 label → 载文件到编辑器（若缺失，则 `* Untitled` 且留空）→ 编辑（脏态）→ `Scrape/退出/导入` 前自动写 `Untitled.toml` → 运行/保存/导出按规范执行。
- 导出（当 label=Untitled）→ 生成 `Untitled-YYYYMMDD-HHMM.toml` → 导出配置将 label 指向该快照。

### 测试要点
- 仅持久化 label（无 `preset_text`）。
- 脏态下 `Scrape/退出/导入` 自动写入 `Untitled.toml`（覆盖）。
- 导出时（label=Untitled）自动生成快照并将导出配置的 label 指向快照。
- 启动/导入时找不到 label 文件的回退逻辑可靠；`Refresh` 正常重扫。

### 最小落地改动点
- `src/mdxscraper/gui/pages/css_page.py` / `pdf_page.py`
- `src/mdxscraper/gui/main_window.py`
- `src/mdxscraper/gui/services/settings_service.py`
- `src/mdxscraper/gui/services/presets_service.py`
- `src/mdxscraper/gui/workers/conversion_worker.py`
- `src/mdxscraper/gui/services/export_service.py`
