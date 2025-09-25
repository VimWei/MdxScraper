# 预设选择与编辑器加载统一机制设计

## 问题背景

当前代码中，不同场景（启动同步、导入、保存、刷新、导出快照、自动保存 Untitled 后定位）都需要"更新下拉列表并选择某个值，同时更新编辑框"，但各场景的处理逻辑分散且不一致，导致：

- 代码重复：多处都有"设置下拉选中 + 加载编辑器内容"的相似逻辑
- 行为不一致：不同场景可能有细微差异，难以维护
- 状态管理复杂：需要手动管理 `_updating_*_editor` 标志来避免副作用

## 统一机制设计

### 核心原则

1. **单一职责**：下拉选择变化是唯一触发编辑器加载的入口
2. **信号驱动**：使用 PySide6 的信号/槽机制，`preset_changed` 信号统一处理编辑器加载
3. **状态约束**：程序化更新时抑制副作用，用户编辑时才进入 * Untitled 状态
4. **强绑定**：`preset_label` 与文件内容强绑定，配置只保存 label，运行时从文件加载内容

### 统一接口

#### 1. 核心方法：`select_label_and_load(kind, label)`

```python
def select_label_and_load(self, kind: str, label: str) -> None:
    """统一的选择预设并加载编辑器内容的入口"""
    if kind == 'pdf':
        combo = self.tab_pdf.pdf_combo
    else:
        combo = self.tab_css.css_combo
    
    # 查找并设置下拉选中项
    for i in range(combo.count()):
        if combo.itemText(i) == label:
            combo.setCurrentIndex(i)
            return
    
    # 如果找不到，进入 * Untitled 状态（无选中项）
    self._enter_untitled_state(kind, clear_editor=False)
    # 清理配置中的无效 label
    if kind == 'pdf':
        self.settings.set('pdf.preset_label', '')
    else:
        self.settings.set('css.preset_label', '')
```

#### 2. 信号处理：`on_*_preset_changed(label)`

```python
def on_pdf_preset_changed(self, label: str):
    """下拉选择变化时的统一处理"""
    idx = self.tab_pdf.pdf_combo.currentIndex()
    
    if idx < 0:  # 无选中项（* Untitled 状态）
        return
    
    path = self.tab_pdf.pdf_combo.itemData(idx)
    if not path:
        return
    
    try:
        # 加载文件内容到编辑器
        text = self.presets.load_preset_text(Path(path))
        self._updating_pdf_editor = True
        try:
            self.tab_pdf.pdf_editor.setPlainText(text)
        finally:
            self._updating_pdf_editor = False
        
        # 更新状态
        self.settings.set('pdf.preset_label', label)
        self.pdf_dirty = False
        self.last_pdf_label = label
        self.tab_pdf.show_dirty(False)
    except Exception as e:
        # 加载失败，进入 * Untitled 状态
        self.command_panel.appendLog(f"❌ Failed to load PDF preset: {e}. Switched to * Untitled state.")
        self._enter_untitled_state('pdf', clear_editor=True)
        # 清理配置中的失效 label
        self.settings.set('pdf.preset_label', '')
```

#### 3. 状态管理：`_enter_untitled_state(kind, clear_editor)`

```python
def _enter_untitled_state(self, kind: str, clear_editor: bool = True) -> None:
    """进入 * Untitled 状态的统一处理
    
    Args:
        kind: 'pdf' 或 'css'
        clear_editor: 是否清空编辑器内容
                     - True: 用于加载失败等异常情况
                     - False: 用于用户编辑导致的脏态，保留用户内容
    """
    if kind == 'pdf':
        combo = self.tab_pdf.pdf_combo
        editor = self.tab_pdf.pdf_editor
        dirty_label = 'pdf_dirty'
        show_dirty = self.tab_pdf.show_dirty
        set_flag = lambda v: setattr(self, '_updating_pdf_editor', v)
    else:
        combo = self.tab_css.css_combo
        editor = self.tab_css.css_editor
        dirty_label = 'css_dirty'
        show_dirty = self.tab_css.show_dirty
        set_flag = lambda v: setattr(self, '_updating_css_editor', v)
    
    # 根据参数决定是否清空编辑器
    if clear_editor:
        set_flag(True)
        try:
            editor.setPlainText("")
        finally:
            set_flag(False)
    
    # 清空下拉选择（不 blockSignals，让槽函数处理）
    combo.setCurrentIndex(-1)
    
    # 设置脏态
    setattr(self, dirty_label, True)
    show_dirty(True)
```

### 使用场景

#### 1. 启动同步

```python
def sync_from_config(self):
    # ... 其他同步逻辑 ...
    
    # 统一使用 select_label_and_load
    pdf_config = self.settings.get_pdf_config()
    if pdf_config.preset_label:
        self.select_label_and_load('pdf', pdf_config.preset_label)
    
    css_config = self.settings.get_css_config()
    if css_config.preset_label:
        self.select_label_and_load('css', css_config.preset_label)
```

#### 2. 导入配置

```python
def import_config(self):
    # ... 导入逻辑 ...
    
    # 导入后统一重新选择
    pdf_label = self.settings.get('pdf.preset_label', '')
    if pdf_label:
        self.select_label_and_load('pdf', pdf_label)
    
    css_label = self.settings.get('css.preset_label', '')
    if css_label:
        self.select_label_and_load('css', css_label)
```

#### 3. 保存预设

```python
def on_pdf_save_clicked(self):
    # ... 保存逻辑 ...
    
    # 保存后重新选择新保存的项
    saved_label = Path(file).stem
    self.reload_presets(auto_select_default=False)
    self.select_label_and_load('pdf', saved_label)
```

#### 4. 自动保存 Untitled

```python
def autosave_untitled(self, kind: str):
    # ... 保存 Untitled.toml ...
    
    # 保存后选择 Untitled（从 Untitled 状态切换到 Untitled 预设）
    self.reload_presets(auto_select_default=False)
    self.select_label_and_load(kind, 'Untitled')
```

#### 5. 导出快照

```python
def export_config(self):
    # ... 生成快照逻辑 ...
    
    # 生成快照后选择快照项
    if new_pdf_label:
        self.reload_presets(auto_select_default=False)
        self.select_label_and_load('pdf', new_pdf_label)
    
    if new_css_label:
        self.reload_presets(auto_select_default=False)
        self.select_label_and_load('css', new_css_label)
```

### 用户编辑处理

```python
def on_pdf_text_changed(self):
    """用户手动编辑时的处理"""
    if self._updating_pdf_editor:
        return  # 程序化更新，忽略
    
    # 进入 * Untitled 状态（保留用户内容）
    self._enter_untitled_state('pdf', clear_editor=False)
```

## 实现优势

### 1. 代码简化

- **消除重复**：所有"选择并加载"场景都调用 `select_label_and_load`
- **统一行为**：编辑器加载逻辑集中在 `on_*_preset_changed` 中
- **清晰职责**：选择下拉 vs 加载编辑器分离

### 2. 状态管理

- **信号驱动**：依赖 PySide6 信号机制，行为可预测
- **副作用控制**：程序化更新时抑制 `textChanged` 信号
- **状态一致**：`* Untitled` 状态统一通过 `_enter_untitled_state` 管理
- **强绑定**：配置只保存 `preset_label`，内容从文件加载，确保可复现性

### 3. 维护性

- **单一修改点**：加载逻辑变更只需修改 `on_*_preset_changed`
- **易于调试**：所有选择操作都经过统一路径
- **扩展友好**：新增场景只需调用 `select_label_and_load`

## 与强绑定架构的集成

### 状态定义

- **`* Untitled` 状态**：下拉选择为 `-1`（无选中项），编辑器可能包含用户未保存的内容
- **Untitled 预设**：下拉选择为名为 `Untitled` 的预设项，对应磁盘上的 `Untitled.toml` 文件

### 信号处理策略

采用方案A：不 blockSignals，统一由槽函数处理
- 所有下拉选择变化都通过 `on_*_preset_changed` 处理
- 槽函数内部通过 `currentIndex()` 判断状态
- 程序化设置 `-1` 时，槽函数直接返回，不执行加载逻辑

### 与现有架构的协调

- 配置只保存 `preset_label`，不保存 `preset_text`
- 启动/导入时根据 `preset_label` 加载对应文件内容
- 用户编辑时进入 `* Untitled` 状态，保留编辑器内容
- 运行/退出/导入前自动保存到 `Untitled.toml`
- 导出时若为 `* Untitled` 状态，生成快照并更新配置

## 迁移步骤

1. **提取统一方法**：实现 `select_label_and_load` 和 `_enter_untitled_state`
2. **重构现有场景**：将分散的选择逻辑替换为 `select_label_and_load` 调用
3. **简化信号处理**：确保 `on_*_preset_changed` 只负责加载，不处理选择
4. **集成强绑定**：移除配置中的 `preset_text` 保存，统一从文件加载
5. **测试验证**：确保所有场景行为一致

## 总结

通过统一的选择和加载机制，结合强绑定架构，可以：

- 消除代码重复，提高可维护性
- 确保行为一致性，减少边界情况
- 简化状态管理，降低出错概率
- 提供清晰的扩展点，便于未来功能添加
- 实现配置与内容的强绑定，确保可复现性
- 优化用户体验，避免意外丢失编辑内容

这种设计符合"单一职责"、"信号驱动"和"强绑定"的 GUI 开发最佳实践，使代码更加健壮和易于理解，同时与现有的 `csspdf_refactor.md` 架构完美集成。
