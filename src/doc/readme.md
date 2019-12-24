# 架构说明

## Plugins模块
存在以下依赖项：
* g.get("canvas"): 用于获取图像和设值图像
* DialogPlugin，由于已经设计图像的preview和cancel()操作，故需要canvas支持撤销操作。框架通过ImageManager实现。
