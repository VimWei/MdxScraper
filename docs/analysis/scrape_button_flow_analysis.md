# Scrape 按钮调用流程分析

## 概述

本文档详细分析了从按下 Scrape 按钮开始，MdxScraper 程序的完整执行流程。通过模块化设计，程序采用了分层架构，每层都有明确的职责分工。

**注意**: 本文档已根据v4.7的重构架构进行更新，反映了从 `gui/` 子目录到独立模块的迁移，以及新增的 Services 和 Coordinators 层。

## 完整调用流程图

```
用户点击 Scrape 按钮
    ↓
CommandPanel.btn_scrape.clicked
    ↓
发出 scrapeRequested 信号
    ↓
MainWindow.run_conversion()
    ↓
ConversionCoordinator.run()
    ↓
创建并启动 ConversionWorker 线程
    ↓
ConversionWorker.run()
    ↓
ExportService.execute_export()
    ↓
根据输出格式调用相应的转换函数
    ├── mdx2html() - HTML 转换
    ├── mdx2pdf() - PDF 转换
    └── mdx2img() - 图片转换
    ↓
通过信号回调更新 UI
    ├── progress_sig - 进度更新
    ├── log_sig - 日志输出
    ├── finished_sig - 完成通知
    └── error_sig - 错误处理
```

## 详细调用链分析

### 1. 按钮触发层

**文件**: `src/mdxscraper/gui/components/command_panel.py`

```python
# 第57行: 按钮点击事件连接
self.btn_scrape.clicked.connect(self.scrapeRequested.emit)
```

- **职责**: 定义 Scrape 按钮并发出信号
- **关键代码**: 当用户点击按钮时，发出 `scrapeRequested` 信号

### 2. 主窗口连接层

**文件**: `src/mdxscraper/gui/main_window.py`

```python
# 第155行: 信号连接
self.command_panel.scrapeRequested.connect(self.run_conversion)

# 第336-337行: 转换方法
def run_conversion(self):
    self.convc.run(self)
```

- **职责**: 接收信号并委托给协调器
- **关键代码**: 直接调用 `ConversionCoordinator.run()` 方法

### 3. 协调器层 (Coordinator)

**文件**: `src/mdxscraper/coordinators/conversion_coordinator.py`

```python
# 第22-41行: 主要协调逻辑
def run(self, mw) -> None:
    # 同步所有页面配置到设置
    mw.cfgc.sync_all_to_config(mw)
    # 自动保存未命名的预设
    mw.preset_coordinator.autosave_untitled_if_needed(mw)
    # 禁用 Scrape 按钮
    mw.command_panel.btn_scrape.setEnabled(False)
    # 获取编辑器内容
    pdf_text = mw.tab_pdf.pdf_editor.toPlainText()
    css_text = mw.tab_css.css_editor.toPlainText()
    # 创建并启动工作线程
    self.worker = ConversionWorker(self.project_root, self.cm, pdf_text=pdf_text, css_text=css_text)
    # 连接信号
    self.worker.finished_sig.connect(lambda msg: self.on_finished(mw, msg))
    self.worker.error_sig.connect(lambda msg: self.on_error(mw, msg))
    self.worker.log_sig.connect(lambda text: self.on_log(mw, text))
    self.worker.progress_sig.connect(lambda p, t: self.on_progress(mw, p, t))
    # 启动线程
    self.worker.start()
```

- **职责**: 协调整个转换流程，管理 UI 状态
- **关键功能**:
  - 同步配置到设置服务
  - 自动保存预设
  - 禁用/启用按钮
  - 创建工作线程并连接信号

### 4. 工作线程层 (Worker)

**文件**: `src/mdxscraper/workers/conversion_worker.py`

```python
# 第30-143行: 主要工作逻辑
def run(self):
    try:
        # 获取配置信息
        cfg = self._settings_service.get_config_dict()
        basic = cfg.get('basic', {}) if isinstance(cfg, dict) else {}
        input_val = basic.get('input_file')
        dict_val = basic.get('dictionary_file')
        output_val = basic.get('output_file')
        
        # 验证必需字段
        if not input_val or not dict_val or not output_val:
            missing = []
            if not input_val: missing.append('basic.input_file')
            if not dict_val: missing.append('basic.dictionary_file')
            if not output_val: missing.append('basic.output_file')
            raise ValueError('Missing required field(s): ' + ', '.join(missing))
        
        # 解析路径
        input_file = self._settings_service.resolve_path(input_val)
        mdx_file = self._settings_service.resolve_path(dict_val)
        output_path = self._settings_service.resolve_path(output_val)
        
        # 应用时间戳
        timestamp_enabled = self._settings_service.get_output_add_timestamp()
        if timestamp_enabled:
            from datetime import datetime
            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_dir = output_path.parent
            output_name = output_path.name
            output_path = output_dir / (current_time + '_' + output_name)
        
        # 执行转换
        def progress_callback(progress: int, message: str):
            scaled_progress = 10 + int((progress / 100) * 80)
            self.progress_sig.emit(scaled_progress, message)
        
        found, not_found, invalid_words = self._export_service.execute_export(
            input_file, mdx_file, output_path, 
            pdf_text=self._pdf_text or '', 
            css_text=self._css_text or '', 
            settings_service=self._settings_service, 
            progress_callback=progress_callback
        )
        
        # 处理备份和无效词汇文件
        # 发送完成信号
        self.finished_sig.emit(msg)
        
    except Exception as e:
        self.error_sig.emit(str(e))
```

- **职责**: 在后台线程中执行实际的转换工作
- **关键功能**:
  - 获取和验证配置
  - 解析文件路径
  - 调用导出服务
  - 处理备份和无效词汇
  - 通过信号报告进度和结果

### 5. 导出服务层 (Service)

**文件**: `src/mdxscraper/services/export_service.py`

```python
# 第52-79行: 导出执行逻辑
def execute_export(self, input_file: Path, mdx_file: Path, output_path: Path,
                    pdf_text: str = '', css_text: str = '', 
                    settings_service: Optional[SettingsService] = None,
                    progress_callback: Optional[Callable[[int, str], None]] = None):
    from mdxscraper.core.converter import mdx2html, mdx2pdf, mdx2img
    
    suffix = output_path.suffix.lower()
    h1_style, scrap_style, additional_styles = self.parse_css_styles(css_text)
    
    if suffix == '.html':
        with_toc = settings_service.get('basic.with_toc', True)
        return mdx2html(mdx_file, input_file, output_path, with_toc=with_toc,
                        h1_style=h1_style, scrap_style=scrap_style, 
                        additional_styles=additional_styles,
                        progress_callback=progress_callback)
    elif suffix == '.pdf':
        pdf_options = self.build_pdf_options(pdf_text)
        wkhtmltopdf_path = settings_service.get('advanced.wkhtmltopdf_path', 'auto')
        with_toc = settings_service.get('basic.with_toc', True)
        return mdx2pdf(mdx_file, input_file, output_path, pdf_options, with_toc=with_toc,
                       h1_style=h1_style, scrap_style=scrap_style, 
                       additional_styles=additional_styles,
                       wkhtmltopdf_path=wkhtmltopdf_path, 
                       progress_callback=progress_callback)
    elif suffix in ('.jpg', '.jpeg', '.png', '.webp'):
        img_opts = self.build_image_options(suffix)
        with_toc = settings_service.get('basic.with_toc', True)
        return mdx2img(mdx_file, input_file, output_path, img_options=img_opts, 
                       with_toc=with_toc, h1_style=h1_style, scrap_style=scrap_style, 
                       additional_styles=additional_styles,
                       progress_callback=progress_callback)
    else:
        raise RuntimeError(f"Unsupported output extension: {suffix}")
```

- **职责**: 根据输出格式选择合适的转换方法
- **关键功能**:
  - 解析 CSS 样式
  - 构建 PDF 和图片选项
  - 根据文件扩展名调用相应的转换函数

### 6. 核心转换层 (Core)

**文件**: `src/mdxscraper/core/converter.py`

#### HTML 转换
```python
# 第21-132行: mdx2html()
def mdx2html(mdx_file, input_file, output_file, with_toc=True, 
              h1_style=None, scrap_style=None, additional_styles=None, 
              progress_callback=None):
    # 加载字典和解析输入
    dictionary = Dictionary(mdx_file)
    lessons = WordParser(str(input_file)).parse()
    
    # 处理每个课程和单词
    for lesson in lessons:
        for word in lesson['words']:
            result = dictionary.lookup_html(word)
            # 构建 HTML 结构...
    
    # 合并 CSS 样式和嵌入图片
    right_soup = merge_css(right_soup, mdx_file.parent, dictionary.impl, additional_styles)
    right_soup = embed_images(right_soup, dictionary.impl)
    
    # 写入 HTML 文件
    with open(output_file, 'wb') as file:
        file.write(html)
```

#### PDF 转换
```python
# 第135-181行: mdx2pdf()
def mdx2pdf(mdx_file, input_file, output_file, pdf_options, ...):
    # 先生成 HTML
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        found, not_found, invalid_words = mdx2html(...)
    
    # 再转换为 PDF
    pdfkit.from_file(temp_file, str(output_file), 
                     configuration=config, options=pdf_options)
```

#### 图片转换
```python
# 第184-278行: mdx2img()
def mdx2img(mdx_file, input_file, output_file, img_options=None, ...):
    # 先生成 HTML
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        found, not_found, invalid_words = mdx2html(...)
    
    # 根据格式转换为图片
    if suffix == '.webp':
        # 先转 PNG，再转 WEBP
    elif suffix == '.png':
        # 优化 PNG
    elif suffix in ('.jpg', '.jpeg'):
        # 直接转换
```

- **职责**: 执行实际的 MDX 到目标格式的转换
- **关键功能**:
  - 加载 MDX 字典
  - 解析输入文件
  - 查找单词定义
  - 生成 HTML 结构
  - 应用样式和嵌入图片
  - 转换为目标格式

### 7. 信号回调处理

**文件**: `src/mdxscraper/coordinators/conversion_coordinator.py`

```python
# 第43-65行: 信号回调处理
def on_finished(self, mw, message: str) -> None:
    mw.command_panel.btn_scrape.setEnabled(True)
    mw.command_panel.setProgress(100)
    mw.command_panel.setProgressText("Conversion completed!")
    mw.log_panel.appendLog(f"✅ {message}")

def on_error(self, mw, message: str) -> None:
    mw.command_panel.btn_scrape.setEnabled(True)
    mw.command_panel.setProgress(0)
    mw.command_panel.setProgressText("Conversion failed")
    mw.log_panel.appendLog(f"❌ Error: {message}")

def on_progress(self, mw, progress: int, text: str) -> None:
    mw.command_panel.setProgress(progress)
    mw.command_panel.setProgressText(text)

def on_log(self, mw, text: str) -> None:
    if not text.startswith("Progress:"):
        mw.log_panel.appendLog(text)
```

- **职责**: 处理工作线程发出的各种信号
- **关键功能**:
  - 更新进度条
  - 添加日志信息
  - 重新启用按钮
  - 显示完成或错误状态

## 关键文件总结

| 层级 | 文件 | 职责 |
|------|------|------|
| **UI 层** | `gui/components/command_panel.py` | 按钮定义和信号发射 |
| **主窗口** | `gui/main_window.py` | 信号连接和委托 |
| **协调器** | `coordinators/conversion_coordinator.py` | 流程协调和状态管理 |
| **工作线程** | `workers/conversion_worker.py` | 后台执行和进度报告 |
| **导出服务** | `services/export_service.py` | 转换类型选择和参数构建 |
| **核心转换** | `core/converter.py` | 实际的 MDX 到目标格式转换 |

## 架构特点

1. **分层设计**: 每层都有明确的职责，便于维护和测试
2. **信号机制**: 使用 Qt 信号槽机制实现松耦合的组件通信
3. **异步处理**: 使用工作线程避免 UI 阻塞
4. **模块化**: 各个功能模块独立，便于扩展和修改
5. **错误处理**: 完善的异常处理和用户反馈机制
6. **服务化**: 通过 Services 层统一管理配置、预设和导出逻辑
7. **协调器模式**: 使用 Coordinators 协调不同服务之间的交互
8. **进度回调**: 支持细粒度的进度报告和状态更新

## 扩展点

- **新增输出格式**: 在 `ExportService.execute_export()` 中添加新的格式支持
- **自定义转换逻辑**: 在 `core/converter.py` 中添加新的转换函数
- **UI 增强**: 在 `gui/components/command_panel.py` 中添加新的控制元素
- **进度报告**: 在 `workers/conversion_worker.py` 中自定义进度回调
- **服务扩展**: 在 `services/` 目录下添加新的服务类
- **协调器扩展**: 在 `coordinators/` 目录下添加新的协调器
- **预设管理**: 通过 `PresetsService` 扩展预设功能
- **配置管理**: 通过 `SettingsService` 扩展配置选项

这种架构设计使得程序具有良好的可维护性和可扩展性，每个模块都可以独立开发和测试。
