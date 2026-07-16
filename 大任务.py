#!/usr/bin/env python
# coding: utf-8

# ## AI推理任务指挥官

# In[1]:


# 在此基础上操作，达到最终结果
import time
import threading
from datetime import datetime 

#1.模型类
class AIModel:   #给AI定义一个类,所有AI的抽象基类
    def __init__(self, name, model_type):  #初始化操作 name：模型名称 ； model_type：模型类别
        self.name = name
        self.model_type = model_type

    def predict(self, input_data):  #执行推理
        raise NotImplementedError("子类必须实现predict方法")        

class TextModel(AIModel):  #文本模型的类，继承AIMode
    def predict(self, input_data):  #还是执行推理，模拟文本生成
        start = datetime.now()
        time.sleep(1)
        end = datetime.now()
        return {
            "output": f"{input_data} 的识别结果为：冷笑话",
            "cost": (end - start).total_seconds()
        }
        #删除return死代码
class ImageModel(AIModel):     #图像模型的类，继承AIMode
    def predict(self, input_data):  #模拟图像生成
        start = datetime.now()
        #print(f"[{self.name}]正在识别图像：{input_data}")
        time.sleep(2)  #休眠时间错误——已修正
        end = datetime.now()
        return {
            "output": f"{input_data} 的识别结果为：猫咪",
            "cost": (end - start).total_seconds()
        }





# In[ ]:





# In[2]:


#2. 调度器 Scheduler

# 属性：任务记录表`records`、线程锁`lock`
# `_run_one`：执行单任务，加锁写入记录
# `run_serial`：串行依次执行所有任务
# `run_concurrent`：多线程并发执行，start+join 等待全部结束
#`report`：格式化打印每条任务详情

#制作Scheduler调度器，只能手搓了


class Scheduler:
    def __init__(self, tasks):
        self.tasks = tasks   #让Scheduler自己管理records和lock，__init__只接受tasks列表，内部初始化self.records=[] 和 self.lock = threading.Lock()
        self.records = []
        self.lock = threading.Lock()
    def _run_one(self, user, model, input_data): #执行单行任务，加锁写入记录
        #1.执行推理，不锁
        result = model.predict(input_data) #predict是模型方法
        #2.构建字典
        record = {
        "user": user,
        "model": model.name,
        "cost": result['cost'],
        "result": result['output']}
        #3.加锁写入
        with self.lock:
            self.records.append(record)
    
    def run_serial(self): #串行依次执行所有任务，依次调用嘛，初始化时整个任务列表，再用前一个一个一个调用
        for user, model, input_data in self.tasks:
            self._run_one(user, model, input_data)
        
    
    def run_concurrent(self): #多线程并发执行，start+join等待全面结束
        #多线程
        #创建空线程列表(将那些线程放到一个列表里面统一执行)
        threads = []
        for user, model ,input_data in self.tasks:
            t = threading.Thread(target = self._run_one, args=(user, model, input_data))
            threads.append(t)
            t.start()
        for t in threads:  #用循环变量
            t.join()

    def report(self):  #格式化打印每条任务详情
        #用户: 用户A, 模型: GPT小助手, 耗时: 1.02秒, 结果: 《写首诗》的生成结果
        print("\n=====任务执行明细=====")
        for r in self.records:
            print(f"用户:{r['user']}, 模型:{r['model']}, 耗时:{r['cost']}, 结果:{r['result']} ")


# In[ ]:





#  #定义主程序
#  #1. 创建文本、图像模型，构造≥6 条混合用户任务
#  #2. 分别运行串行、并发，用 datetime 统计全局总耗时
#  #3. 输出对比报表：串行总耗时、并发总耗时、节省时长、加速比、当前系统时间
# def main(): 
#     

# In[3]:


#3主程序的制作：
def main():
    #1.创建模型实例
    text_model = TextModel("GPT小助手","文本生成")
    image_model = ImageModel("图片识别器","图像识别")

    #2.构造任务列表
    tasks = [
        ("用户A", text_model, "写一首诗"),
        ("用户B", image_model, "cat.jpg"),
        ("用户C", text_model, "讲一个笑话"),
        ("用户D", image_model, "dog.png"),
        ("用户E", text_model, "写一篇短文"),
        ("用户F", image_model, "flower.jpg"),
    ]
    #3.串行执行
    print("===串行开始执行===")
    serial_start = datetime.now()
    scheduler_serial = Scheduler(tasks) #创建调度器，也可以叫调度器的初始化,同时在内部维护自己的records和锁
    scheduler_serial.run_serial() #串行执行
    serial_end = datetime.now()
    serial_total = (serial_end - serial_start).total_seconds()
    scheduler_serial.report()  #打印明细

   #4.并发执行
    print("===并发执行开始===")
    concurrent_start = datetime.now()
    scheduler_concurrent = Scheduler(tasks) #重新创建一个调度器(避免记录干扰)
    scheduler_concurrent.run_concurrent()
    concurrent_end = datetime.now()
    concurrent_total = (concurrent_end - concurrent_start).total_seconds()
    scheduler_concurrent.report()

    #5.输出对比报表
    speedup = serial_total / concurrent_total #加速比
    saved = serial_total - concurrent_total #节省时间
    print("\n========== 性能对比 ==========")
    print(f"串行总耗时: {serial_total:.2f} 秒")
    print(f"并发总耗时: {concurrent_total:.2f} 秒")
    print(f"节省时间: {saved:.2f} 秒")
    print(f"加速比: {speedup:.2f}x")
    print(f"当前系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# In[4]:


#程序入口
if __name__ == "__main__":
    main()


# 思考题（5 分，必写）
# 1. 多线程写入 records 为什么要加 Lock？不加锁会出现什么问题？
# 
# ## 回答：多线程写入records之所以加上Lock是为了防止多线程发生冲突造成后面的覆盖前面的混乱局面————防止产生数据竞争，导致数据泄露或者损坏

# 2. 本案例多线程能提速，纯 CPU 计算场景还能加速吗？为什么？
# 
# ## 回答：纯 CPU 计算场景在 Python 中不能加速，根本原因是 Python 的 GIL（全局解释器锁）——限制了同一时刻只有一个线程执行 Python 代码

# 3. 父类抛出 NotImplementedError 是什么设计思想，作用是什么？
# ## 回答:体现了 “面向接口编程” 的设计思想，父类定义规范(必须按照父类的规矩)，子类必须实现(子类必须按照执行)，它的作用是强制子类重写方法

# In[ ]:




