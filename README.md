# delete_objects_parallel

## 描述

多线程并行批量删除指定 S3 路径下的对象。

## 使用方式

1. 修改代码中的如下参数，
   - **bucket_name**，表示 S3 桶的名字；
   - **object_prefix**，表示删除某个路径下的 Object（其它路径的 Object 不会被删除），需要注意，
      - 如果您要删除桶下面的所有 Object，这个参数保持为空字符串（""）即可；
      - 如果您需要指定某一个目录，不要包含桶的名字，例如，您要删除路径 s3://bucket-1/a/b/c/ 下的 Object，这个参数应该为 a/b/c/；
   - **region_name**，表示 Region 名称，北京区为 cn-north-1，宁夏区为 cn-northwest-1;
   - **total_threads**，表示一共启动多少个线程，我们的脚本中采用的是线程池的方式实现并发；
   - **thread_name_prefix**，表示每个线程名字的前缀，便于在日志中识别，您可以自定义任何字符串；
   - **objects_per_batch**，表示每个线程、每次删除多少个 Object，不能超过1000。
2. 运行脚本，
   ```
   python delete_objects_parallel.py
   ```
