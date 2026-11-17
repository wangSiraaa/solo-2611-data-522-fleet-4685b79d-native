# 分区加工的协作锁与子进程执行

Python 3.11，仅标准库。现有三个文件可独立运行；LockService 使用真正的 SQLite，JobRuntime 启动实际子进程。普通、不竞争的加工可以成功。待增加的是会话/事务分离、持久排队和作业取消时的真实所有权交接，题面列出目标。

worker.py 是用于控制启动、终止确认与退出之间间隔的任务设施，不是锁或调度的实现。control_dir/ready 表示该子进程已装好 TERM 处理器；创建 finish 文件才允许它继续。收到 TERM 会记 signal-seen，随后退出而不写产品。正常分支读取 input_rows(value) 并写 products；这些表位于调用者提供的专用 result_db。控制文件不属于客户API，可以换等价的管道/事件屏障；不能通过删掉延迟退出行为掩盖释放时机问题。
