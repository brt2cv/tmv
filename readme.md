
目前仓库仅用于MVTool项目。但框架是以通用的python项目构建的。如果需要在框架中新增子项目，将项目放在app/目录下即可。

**注意：为了Git仓库对的整洁性，app/.gitignore忽略了其他项目的git管理**

## utils/mvlib等子模块
使用submodules.sh脚本进行管理。直接使用命令 `sh submodules.sh pull` 即可更新子模块。

## Sublime Text 配置

### path

`"path": "X:\\workspace\\tmv\\src"`

需要指定到src目录，否则，无法正常跳转utils、mvlib的库
