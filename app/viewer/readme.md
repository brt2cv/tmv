# Todo list
1. Grabber包含Trans，那么能否直接控制Trans::pyqtSignal呢？而非再注册一个信号，仅仅对Trans的信号做了一层转发？
2. 当前Client的数据监听是异步的，但在查询regester list等操作时，需要同步处理，怎么调整架构？
3. Grabber对象实现connBreak信号，并反馈给UI。
4. UI文件编译后，只能识别Ui_Form，无法识别Ui_Dialog的对象，utils.uic模块待优化。

# Release
v1.0
1. 实现了对图像的补帧，用于恶劣的网络环境传输
2. 注意：当前配置的服务器：111.67.199.27，并非持久服务器。
3. 持久服务器：103.72.167.230，但带宽较低，传输极不稳定。
