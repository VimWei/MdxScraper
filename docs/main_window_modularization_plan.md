# MainWindow 协调器化模块重构计划

基于 `docs/GUI_refactor.md`、`docs/csspdf_refactor.md`、`docs/preset_selection_unification.md` 的既有架构目标，现针对 `src/mdxscraper/gui/main_window.py` 体量与职责膨胀（~1000 行）的问题，制定进一步模块化（Coordinator 协调器模式）实施方案。

## 1. 目标与原则
- 将 `MainWindow` 压缩为“装配与编排”薄壳：负责 UI 组件装配、信号连接、任务委托。
- 将跨组件/跨服务的流程性逻辑下沉到“协调器（Coordinator）”。
- 遵循单一职责、信号驱动、强绑定（CSS/PDF 预设）与可测试性原则。
- 渐进式改造，保持功能可用与可回滚。

## 2. 目标目录结构（新增/调整）
```
src/mdxscraper/gui/
├── main_window.py                  # 仅装配、信号桥接、委托
├── coordinators/
│   ├── __init__.py
│   ├── config_coordinator.py       # 配置统一同步/导入导出/校验编排
│   ├── preset_coordinator.py       # 预设列表/选择/脏态/快照/统一加载
│   ├── file_coordinator.py         # 文件对话框/路径建议/打开目录
│   └── conversion_coordinator.py   # 运行/进度/日志/中断与收尾
└── styles/                         # 已实施主题与样式集中管理
```

## 3. 协调器职责与公共 API（草案）

### 3.1 ConfigCoordinator（配置协调）
- 职责：统一“从配置→页面”“从页面→配置”的拉取与回写；导入/导出编排；校验结果汇报。
- 依赖：`SettingsService`、`PresetsService`（只在需要冻结 Untitled 时）
- API：
```python
class ConfigCoordinator:
    def __init__(self, settings: SettingsService, presets: PresetsService): ...

    def sync_all_from_config(self, mw: MainWindow) -> None: ...
    def sync_all_to_config(self, mw: MainWindow) -> None: ...

    def sync_basic_from_config(self, mw: MainWindow) -> None: ...
    def sync_basic_to_config(self, mw: MainWindow) -> None: ...
    def sync_image_from_config(self, mw: MainWindow) -> None: ...
    def sync_image_to_config(self, mw: MainWindow) -> None: ...
    def sync_advanced_from_config(self, mw: MainWindow) -> None: ...
    def sync_advanced_to_config(self, mw: MainWindow) -> None: ...
    def sync_pdf_to_config(self, mw: MainWindow) -> None: ...  # 仅 label
    def sync_css_to_config(self, mw: MainWindow) -> None: ...  # 仅 label

    def import_config(self, mw: MainWindow, file_path: Path) -> None: ...
    def export_config(self, mw: MainWindow, file_path: Path) -> None: ...  # 内含冻结 Untitled 的编排

    def validate_and_log(self, mw: MainWindow) -> None: ...
```

### 3.2 PresetCoordinator（预设协调）
- 职责：统一预设的“枚举/选择/编辑器加载/脏态/* Untitled/快照/刷新”等场景；实现 `select_label_and_load()` 与 `_enter_untitled_state()` 的下沉与复用。
- 依赖：`PresetsService`、`SettingsService`
- API：
```python
class PresetCoordinator:
    def __init__(self, presets: PresetsService, settings: SettingsService): ...

    def reload_presets(self, mw: MainWindow, auto_select_default: bool = False) -> None: ...
    def select_label_and_load(self, mw: MainWindow, kind: str, label: str) -> None: ...
    def enter_untitled_state(self, mw: MainWindow, kind: str, clear_editor: bool) -> None: ...

    def on_pdf_preset_changed(self, mw: MainWindow, label: str) -> None: ...
    def on_css_preset_changed(self, mw: MainWindow, label: str) -> None: ...
    def on_pdf_text_changed(self, mw: MainWindow) -> None: ...
    def on_css_text_changed(self, mw: MainWindow) -> None: ...

    def autosave_untitled_if_needed(self, mw: MainWindow) -> None: ...
    def create_snapshots_if_needed_on_export(self, mw: MainWindow) -> tuple[str|None, str|None]: ...
```

### 3.3 FileCoordinator（文件对话框/路径）
- 职责：输入/字典/输出文件选择与默认路径建议、统一的相对路径/起始目录策略、打开用户数据目录。
- 依赖：`SettingsService`
- API：
```python
class FileCoordinator:
    def __init__(self, settings: SettingsService, project_root: Path): ...

    def choose_input(self, mw: MainWindow) -> None: ...
    def choose_dictionary(self, mw: MainWindow) -> None: ...
    def choose_output(self, mw: MainWindow) -> None: ...
    def open_user_data_dir(self, mw: MainWindow) -> None: ...
```

### 3.4 ConversionCoordinator（运行/进度/日志）
- 职责：运行前置同步与校验、收集编辑器文本、启动 `ConversionWorker`、连接进度/日志/完成/错误信号、禁用/启用按钮、优雅中断。
- 依赖：`SettingsService`、`PresetsService`、`ConversionWorker`
- API：
```python
class ConversionCoordinator:
    def __init__(self, settings: SettingsService, presets: PresetsService, project_root: Path, cm: ConfigManager): ...

    def run(self, mw: MainWindow) -> None: ...
    def on_finished(self, mw: MainWindow, message: str) -> None: ...
    def on_error(self, mw: MainWindow, message: str) -> None: ...
    def on_progress(self, mw: MainWindow, progress: int, text: str) -> None: ...
```

## 4. MainWindow 期望形态（示例片段）
```python
class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        # 1) 构建服务
        self.cm = ConfigManager(project_root)
        self.cm.load()
        self.settings = SettingsService(project_root, self.cm)
        self.presets = PresetsService(project_root)
        # 2) 构建协调器
        self.cfgc = ConfigCoordinator(self.settings, self.presets)
        self.pstc = PresetCoordinator(self.presets, self.settings)
        self.filec = FileCoordinator(self.settings, project_root)
        self.convc = ConversionCoordinator(self.settings, self.presets, project_root, self.cm)
        # 3) 装配 UI、连接信号（委托到协调器）
        self._setup_ui()
        self._connect_signals()
        # 4) 初始同步
        self.pstc.reload_presets(self, auto_select_default=False)
        self.cfgc.sync_all_from_config(self)
```

## 5. 迁移步骤（渐进与可回滚）
1) 提取 `PresetCoordinator`
   - 将 `reload_presets/select_label_and_load/_enter_untitled_state` 与 `on_*_preset_changed/on_*_text_changed/autosave_untitled_if_needed` 全量迁移；
   - MainWindow 中改为简单委托；
   - 验收：启动/导入/保存/刷新/导出快照/自动保存 Untitled 行为一致，日志一致。

2) 提取 `FileCoordinator`
   - 迁移 `choose_input/choose_dictionary/choose_output/open_user_data_dir`；
   - 验收：文件对话框起始目录、默认文件名、相对路径显示与之前一致。

3) 提取 `ConfigCoordinator`
   - 迁移 `sync_*_from_config/sync_*_to_config`、`import_config/export_config/validate_and_log`；
   - 与 `PresetCoordinator` 协作处理导入后恢复选择与导出快照；
   - 验收：重启/导入/导出后，PDF/CSS 选择保持，与强绑定规范一致；无 `preset_text` 持久化。

4) 提取 `ConversionCoordinator`
   - 迁移 `run_conversion` 及其信号槽；
   - 接入进度文本与百分比，保持 UI 反馈一致；
   - 验收：长任务可中断，完成/失败路径日志与按钮状态正确。

5) 清理与压缩 `MainWindow`
   - 删除已迁移的私有工具方法；
   - 保留编排、薄壳职责；
   - 目标行数：≤ 450 行。

## 6. 验收标准（Acceptance Criteria）
- 功能层面：
  - 启动同步、导入、保存、刷新、导出、运行 全流程行为与日志与现状一致或更佳；
  - PDF/CSS 强绑定生效：仅保存 `preset_label`，脏态/Untitled/快照逻辑符合 `csspdf_refactor.md`；
  - 线程/进度/日志显示正常，按钮状态切换正确，可中断。
- 结构层面：
  - `MainWindow` 行数 ≤ 450，且不包含业务实现细节；
  - 协调器无 UI 组件创建职责，仅编排既有组件与服务；
  - 各协调器接口有类型注解，单测可覆盖核心分支。

## 7. 测试要点
- 预设：
  - 重启后恢复选择；丢失 label → 进入 `* Untitled`；
  - 编辑脏态下运行/退出/导入 → 自动写入 `Untitled.toml`；
  - 导出（label=Untitled 或脏态）→ 自动生成快照并在导出配置中替换 label。
- 配置：
  - `sync_*_from/to_config` 全量覆盖；
  - 导入后无需手动选默认项，选择由配置驱动恢复；
  - 校验失败时仅记录警告，不阻断导出。
- 转换：
  - 进度阶段更新、日志输出、完成/失败提示；
  - 中断后能快速退出并清理状态。
- 样式：
  - 主题与基础样式已集中管理（已实施），与重构兼容。

## 8. 风险与回滚
- 风险：
  - 信号桥接遗漏导致页面不更新；
  - 预设选择与编辑器加载的时序回归；
  - 线程信号未连接导致进度/日志缺失。
- 缓解：
  - 分步骤提交，每步配套回归测试；
  - 保持 `MainWindow` 临时委托与原逻辑可切换（feature flag）；
  - 完成后统一删除废弃代码路径。
- 回滚策略：
  - 每个阶段结束都可回滚至上一个已验证版本；
  - 保持接口幂等，迁移以“复制→替换”的方式进行。

## 9. 工期与产出
- 预估 2-3 个工作日（取决于测试深度）。
- 产出：
  - 4 个协调器模块与相应单元测试；
  - 重构后的 `MainWindow`；
  - 更新后的开发文档与指南。

---
执行该计划后，`MainWindow` 将真正回归“薄壳”，复杂流程被统一封装到协调器，代码可维护性、可测试性与扩展性显著提升。
