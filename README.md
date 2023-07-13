# NPDTMC
  集群由一个主节点和两个从节点组成的小集群上完成的，主节点有两个CPU内核，内存为6G，每个从节点有2个CPU内核，内存为3G。虚拟机操作系统为Ubuntu16.04，软件栈由Spark2.1.0，Hadoop2.7.3，python3.5.2和Java1.8.0_292组成。本机系统为Windows11，CPU频率为2.30GHz，内存为16G。

  1.实验代码在DPMCConformanceExtension中。
  基于选择结点优先级的分布式调用在DDPMC的distributedtesting.py中，根据层次分解的分布式调用在distributedhrdla.py中，选择结点优先级策略在Node_priority文件夹中，轨迹匹配机制在trace_allocate文件夹中，流程模型分解方法在decompose_conformance_method文件夹中。
  非分布式调用在DPMCConformanceExtension的nodistributedtesting.py中。

2.spark平台提交示例如下： bin/spark-submit --master spark://master:7077 --executor-memory 1G /home/hadoop/Projects/DPMConformanceExtension/DDPMC/distributedtesting.py prAm6 hdfs://master:9000/prAm6.txt 2 4 1
其中，/home/hadoop/Projects/DPMConformanceExtension/DDPMC/distributedtesting.py是运行的代码文件，prAm6是本地流程模型文件名，hdfs://master:9000/prAm6.txt是事件日志，2是分解参数，4是Partition参数，1是实验次数（由于进行三次实验取平均，所以范围为1-3）。

3.实验数据在data文件夹中，实验结果在result文件夹中
