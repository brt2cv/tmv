# 架构说明

目前仓库仅用于MVTool项目。但框架是以通用的python项目构建的。如果需要在框架中新增子项目，将项目放在app/目录下即可。

*注意：为了Git仓库对的整洁性，app/.gitignore忽略了其他项目的git管理*

## Plugins模块
存在以下依赖项：
* g.get("canvas"): 用于获取图像和设值图像
* DialogPlugin，由于已经设计图像的preview和cancel()操作，故需要canvas支持撤销操作。框架通过ImageManager实现。

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
