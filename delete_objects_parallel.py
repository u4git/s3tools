import boto3
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import contextmanager
from datetime import datetime

bucket_name = "my-bucket-name"
object_prefix = ""  # 选填
region_name = "cn-north-1"

total_threads = 10  # 线程数
thread_name_prefix = f"{bucket_name}_worker"  # 线程名称前缀，每个线程会以该名称生成一个日志文件
objects_per_batch = 1000 # 最大 1000

# S3 客户端
s3_client = boto3.client('s3',region_name=region_name)

@contextmanager
def open_log_file():
    file_name = f"{threading.current_thread().name}.log"
    log_file = open(file_name, 'a')

    try:
        yield log_file
    finally:
        log_file.close()

def log(message):
    with open_log_file() as file:
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + " " + str(message) + "\n")
        file.flush()

# 删除一批 S3 Object
def batch_delete_objects(objects_to_delete):
    log("batch_delete_objects()...")

    log(f"{len(objects_to_delete)} objects from {objects_to_delete[0]} to {objects_to_delete[-1]} will be deleted...")

    response = s3_client.delete_objects(Bucket=bucket_name,Delete={"Objects":objects_to_delete})

    log(f"response: {response['ResponseMetadata']}")

    log("batch_delete_objects()...Done.")

def delete_objects_parallel():
    log("Running delete_objects_parallel()...")

    # 线程池
    thread_pool = ThreadPoolExecutor(max_workers=total_threads, thread_name_prefix=thread_name_prefix)

    NextContinuationToken = "start"

    while(NextContinuationToken!=""):
        objects_to_delete = []

        if NextContinuationToken == "start":
            result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_prefix, MaxKeys=objects_per_batch)
        else:
            result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_prefix, MaxKeys=objects_per_batch, ContinuationToken=NextContinuationToken)

        objects = result["Contents"]

        for object in objects:
            object_key = object["Key"]
            objects_to_delete.append({"Key":object_key})
        
        # 启动一个线程进行删除
        thread_pool.submit(batch_delete_objects, objects_to_delete)

        if result['IsTruncated']:
            NextContinuationToken = result["NextContinuationToken"]
        else:
            NextContinuationToken = ""
    
    thread_pool.shutdown(wait=True)

    log("Running delete_objects_parallel()...Done.")

if __name__=="__main__":
    delete_objects_parallel()