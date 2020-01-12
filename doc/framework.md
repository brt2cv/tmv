# 架构说明

目前仓库仅用于MVTool项目。但框架是以通用的python项目构建的。如果需要在框架中新增子项目，将项目放在app/目录下即可。

*注意：为了Git仓库对的整洁性，app/.gitignore忽略了其他项目的git管理*

## 架构目标
* 模块化和插件式：所有Menu都作为独立的插件载入，通过配置文件集成app的功能插件。
* 统一的core管理器：适配于通用项目的核心功能。
* app目录：用于用户交互和仅项目相关的逻辑控制。在子目录中但写法类似于顶层目录。方便项目的移植。

## Plugins模块
存在以下依赖项：

* g.get("canvas"): 用于获取图像和设值图像
* DialogPlugin，由于已经设计图像的preview和cancel()操作，故需要canvas支持撤销操作。框架通过ImageManager实现。

创建的模块级的全局对象：

* core.menu.plug_mgr = PluginManager()
* core.imgio.instance() = ImgIOManager()

### FilterBase
针对ndarray/ImagePlus进行操作，包括了以下功能：

* 处理图像: porcessing(im_arr)
* 获取、设置、更新图像
* 检查插件对图像的要求: check_format()
* 自动处理图像并更新至canvas: run()

### Filter
针对ImageContainer的对象进行操作。

* 增加了对操作的记录: self.scripts, parse_script().
* scripts属性的格式: str or list
  `{output} = mvlib.threshold({im}, {thresh}, {maxval})`
  其中，参数{thresh}可以自动关联到self.para["thresh"]属性，{maxval}同理（如scripts中的变量{xxx}未在self.para中找到，则原样输出）

### DialogFilterBase
显示Dialog，提供了参数设置的交互控件；包括两个主要按钮：

* 确定: accepted()
* 取消: rejected()

run(): 不再作为设定操作，而是延迟创建对话框、检查图像格式、显示Dialog。

增加了view成员属性，数据为dict，可选参数包括：

* type: str
* name: str, 用于控件前通过QLabel显示参数名称
* val_init: number
* val_rnage: list
* para: str, 关联到self.para[str]
* isCheckbox: bool, 是否可选启用与否
* isChecked: bool, 在isCheckbox==True是，默认是否启用

这个插件类型将self.view中的view["para"]与UI绑定，并且支持在processing()中调用self.para["xxx"]获取用户交互的参数值。

而这一过程是在setup_ui()方法中实现的，所以绑定工作必须通过Dialog的实例化实现。

关于self.para属性：

* 由Filter类定义，但Filter本身无法交互设置para值，所以可以认定为常量；
* 而在DialogFilterBase中，交互是通过self.view实现的，所以self.para中的属性都是self.view["para"]映射过来的。
* 结论：无需定义self.para，仅仅通过系统自动调用即可。

### DialogFilter
增加预览功能: preview()

## 错误处理
通过捕获异常的方式处理错误，异常处理总的来说存在于3个位置：
1. DialogFilter._preview()
1. DialogFilter.accept()
1. PluginManager.run()

    这里会调用每个插件的run()方法；之所以没有放在Plugin.run()中捕获异常时为了避免重写run()时的重复操作。

由于大部分操作和异常都是由于插件功能调用引起的，大部分错误均可以被捕获，显示在控制台，并避免软件崩溃。

而对于软件框架层引发的异常，则有必要让其正常显露，并进行代码修复。

## 运行时重载
通过reload的方式，在运行时重载Plugins模块，同时更新菜单栏和工具栏。
这个功能非常适合develop时的调试工作。

## utils/mvlib等子模块
使用submodules.sh脚本进行管理。直接使用命令 `sh submodules.sh pull` 即可更新子模块。

## UI
### Canvas
实现了基于QScrollArea的ScrollViewer基类（为避免与LabelImg::Canvas模块命名冲突）。在此基础上，通过类组合，提供了：

* TabViewer
* GridViewer

### 层叠UI
由于canvas需要响应右键功能，上层viewer无法使用右键菜单，采用层叠的图元，实现在canvas上悬浮控制按钮。



## Sublime Text 配置

### path

`"path": "X:\\workspace\\tmv\\src"`

需要指定到src目录，否则，无法正常跳转utils、mvlib的库
