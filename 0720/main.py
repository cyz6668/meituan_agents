import os
import shutil
import base64
import requests
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from openai import OpenAI
import dashscope
import json
from dashscope import Generation
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
## 步骤1:定义工具函数

# 添加导入random模块
import random
from datetime import datetime
import uuid
import redis
# 模拟天气查询工具。返回结果示例：“北京今天是雨天。”
def get_current_weather(arguments):
    # 定义备选的天气条件列表
    weather_conditions = ["晴天", "多云", "雨天"]
    # 随机选择一个天气条件
    random_weather = random.choice(weather_conditions)
    # 从 JSON 中提取位置信息
    # location = arguments["location"]
    # 返回格式化的天气信息
    return f"今天是{random_weather}。"

# 查询当前时间的工具。返回结果示例：“当前时间：2024-04-15 17:15:18。“
def get_current_time():
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 格式化当前日期和时间
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # 返回格式化后的当前时间
    return f"当前时间：{formatted_time}。"

# 测试工具函数并输出结果，运行后续步骤时可以去掉以下四句测试代码
# print("测试工具输出：")
# print(get_current_weather({"location": "上海"}))
# print(get_current_time())
# print("\n")



tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"]
            }
        }
    }
]
tool_name = [tool["function"]["name"] for tool in tools]



# 读取API Key和Secret Key
# API_KEY = os.getenv("ERNIE_API_KEY", "你的API_KEY")
# SECRET_KEY = os.getenv("ERNIE_SECRET_KEY", "你的SECRET_KEY")

# # 获取access_token
# def get_access_token():
#     url = "https://aip.baidubce.com/oauth/2.0/token"
#     params = {
#         "grant_type": "client_credentials",
#         "client_id": API_KEY,
#         "client_secret": SECRET_KEY
#     }
#     res = requests.post(url, params=params)
#     return res.json().get("access_token")

# 图片转base64
def img2b64(path):
    if not path:
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 调用文心一言多模态API
def call_ernie_multimodal_judge(comment_text, comment_img_path, reply_text, reply_img_path,related_text):
    # client = OpenAI(
    # api_key="password",
    # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # )

    # prompt ="" # "请根据外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。"
    # if comment_text:
    #     prompt+="这是外卖评价："+comment_text+"\n"
    # if reply_text:
    #     prompt+="这是商家回复："+reply_text+"\n"
    # picture_contents = []
    # if comment_img_path:
    #     comment_img_b64 = img2b64(comment_img_path)
    #     if comment_img_b64:
    #         picture_contents.append({"type": "image_url","image_url": {"url": comment_img_b64},})
    # if reply_img_path:
    #     reply_img_b64 = img2b64(reply_img_path)
    #     if reply_img_b64:
    #         picture_contents.append({"type": "image_url","image_url": {"url": comment_img_b64},})
    # picture_contents.append({"type": "text", "text": prompt})
    
    # completion = client.chat.completions.create(
    # model="qwen-vl-plus", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    # messages=[
    #    {"role":"system","content":[{"type": "text", "text": "请根据外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。"}]},
    #    {"role": "user","content": picture_contents,},
    # ],
    # )

    prompt ="" # "请根据外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。"
    if related_text:
        prompt+="这是商家和外卖基本信息:"+related_text+"\n"
    if comment_text:
        prompt+="外卖评价:"+comment_text+"\n"
    if reply_text:
        prompt+="商家回复:"+reply_text+"\n"
    picture_contents = []
    if comment_img_path:
        comment_img_b64 = "file://D:/extra-codes/meituan_judge/"+comment_img_path
        if comment_img_b64:
            picture_contents.append({"image":  comment_img_b64})
    if reply_img_path:
        reply_img_b64 = "file://D:/extra-codes/meituan_judge/"+reply_img_path
        if reply_img_b64:
            picture_contents.append({"image":  reply_img_b64})
    picture_contents.append({ "text": prompt})

    response = dashscope.MultiModalConversation.call(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key="password",
    model='qwen-vl-max-latest', # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    messages=[
       {"role":"system","content":[{"type": "text", "text": "请根据商家和外卖产品基本信息，考虑商家要有利润空间，消费者权益不能被侵犯，查看外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。如果提问到关于天气的问题，请调用 ‘get_current_weather’ 函数;如果提问到关于时间的问题，请调用‘get_current_time’函数。请以友好的语气回答问题。"}]},
       {"role": "user","content": picture_contents,},
    ],
    tools=tools
    )
    # print(picture_contents)

    # completion = client.chat.completions.create(
    # model="qwen-vl-max-latest", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    # messages=[
    #    {"role":"system","content":[{"type": "text", "text": "请根据外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。"}]},
    #    {"role": "user","content": [
    #        # 第一张图像url，如果传入本地文件，请将url的值替换为图像的Base64编码格式
    #        {"type": "image_url","image_url": {"url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"},},
    #        # 第二张图像url，如果传入本地文件，请将url的值替换为图像的Base64编码格式
    #        {"type": "image_url","image_url": {"url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/tiger.png"},},
    #        {"type": "text", "text": "这些图描绘了什么内容？"},
    #         ],
    #     }
    # ],
    # )

    
    # res=completion.choices[0].message.content

    res=response.output.choices[0].message.content[0]["text"]
    if res:
        return res
    else:
        return "AI判断失败，请稍后重试。"
    
    
    # access_token = get_access_token()
    # url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
    # messages = []
    # if comment_text:
    #     messages.append({"role": "user", "content": comment_text})
    # if comment_img_path:
    #     comment_img_b64 = img2b64(comment_img_path)
    #     if comment_img_b64:
    #         messages.append({"role": "user", "content": [{"image": comment_img_b64}]})
    # if reply_text:
    #     messages.append({"role": "assistant", "content": reply_text})
    # if reply_img_path:
    #     reply_img_b64 = img2b64(reply_img_path)
    #     if reply_img_b64:
    #         messages.append({"role": "assistant", "content": [{"image": reply_img_b64}]})
    # prompt = "请根据外卖评价和商家回复的文本和图片，判断谁更占理，并说明理由。"
    # messages.append({"role": "system", "content": prompt})
    # headers = {"Content-Type": "application/json"}
    # data = {"messages": messages}
    # res = requests.post(url, headers=headers, json=data)
    # if res.status_code == 200 and "result" in res.json():
    #     return res.json()["result"]
    # else:
    #     return "AI判断失败，请稍后重试。"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)
from fastapi.responses import StreamingResponse
from fastapi import Request
import time


# 封装模型响应函数
def get_response(messages):
    response = Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="password",
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
        tools=tools,
        seed=random.randint(
            1, 10000
        ),  # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
        result_format="message",  # 将输出设置为message形式
    )
    return response
# 假设你有一个模型API调用函数
def call_knowledge_model_api(query):
    messages = [ #你是外卖推荐智能小助手，
    {"role": "system", "content": "请你根据用户问题回复。如果提问到关于天气的问题，请调用 ‘get_current_weather’ 函数;如果提问到关于时间的问题，请调用‘get_current_time’函数。请以友好的语气回答问题。如果问到上海推荐餐厅，请从以下表格查找餐厅并推荐。餐厅名称\t地址\t经营内容\t人均价位\n\n德兴馆\t广东路471号\t百年本帮经典，首创虾籽大乌参，浓油赤酱代表\t￥47\n\n上海老饭店\t福佑路242号（城隍庙）\t传统八宝鸭、红烧鮰鱼，老城厢文化体验\t￥170\n\n人和馆\t肇嘉浜路407号\t米其林+黑珍珠双料，民国风情环境，金牌红烧肉\t￥150\n\n兰心餐厅\t进贤路130号\t弄堂家常菜，红烧肉、草头圈子，王菲同款排队店\t￥100\n\n草庐酒家\t松江区人民北路54号\t松江非遗小吃，鲜肉油墩、猪油夹沙包（需现金支付）\t小吃¥2起\n\n甬府（虹口）\t北外滩来福士\t米其林一星，宁波海鲜江景餐厅，渔家白蟹骨酱\t¥800+\n\nLe Comptoir de Pierre Gagnaire\t建国西路480号（建业里）\t黑珍珠法餐，名厨主理，中西融合设计\t¥1200+\n\nThe Pine 松涧\t长乐路333号\t黑珍珠中式法餐，季节创意菜单\t¥900+\n\n大董（环贸iapm店）\t淮海中路999号环贸iapm 6楼\t黑珍珠意境菜，烤鸭与葱烧海参\t￥500\n\n上海老站\t漕溪北路201号\t花园火车车厢用餐，本帮菜+古董环境\t￥150\n\n鳗重\t愚园路580号\t专注现杀鳗鱼饭，仅8席位需预约\t￥100\n\nAMINO AMIGO\t淮海中路巴黎春天1楼\t仙人掌主题西餐，墨西哥烤鸡、冬阴功意面\t￥150\n\n9车间川香工坊\t天钥桥路666号\t工厂风沪式川菜，搪瓷碗怀旧体验\t￥90\n\n兴安餐厅\t兴安路145号\t淮海路白领食堂，松鼠鲈鱼、椒盐排条\t￥63\n\n桦堃本帮面馆\t闵行星悦荟1楼\t葱油拌面配素鸡/大排，老上海浇头\t¥25-40\n\n小狗面馆\t大沽路417号\t杭州拌川鼻祖，腰花拌川现炒锅气足\t￥32\n\n七婆串串香\t富国路393号（闵行）\t成都串串火锅，红油锅底配脆肚\t￥80\n\nStone Sal 言盐西餐厅\t东湖路9号\t干式熟成牛排，美式工业风酒吧餐厅\t￥600\n\nMaki House\t愚园路68号晶品4楼\t平价日料，厚切鳗鱼饭性价比之王\t￥45\n\n藤原料理\t国顺东路1003号（健身房内）\t工业风日式居酒屋，烤鳗鱼饭\t￥40\n\n\n\n这是上海餐厅表格，请根据用户的请求来为用户挑选餐厅"},
    {"role": "user", "content": query},
    ]
    first_response = get_response(messages)
    assistant_output = first_response.output.choices[0].message
    # print(f"\n大模型第一轮输出信息：{first_response}\n")
    messages.append(assistant_output)
    if (
        "tool_calls" not in assistant_output
    ):  # 如果模型判断无需调用工具，则将assistant的回复直接打印出来，无需进行模型的第二轮调用
        # print(f"最终答案：{assistant_output.content}")
        return assistant_output.content
    # 如果模型选择的工具是get_current_weather
    elif assistant_output.tool_calls[0]["function"]["name"] == "get_current_weather":
        tool_info = {"name": "get_current_weather", "role": "tool"}
        location = json.loads(assistant_output.tool_calls[0]["function"]["arguments"])[
            "location"
        ]
        tool_info["content"] = get_current_weather(location)
    # 如果模型选择的工具是get_current_time
    elif assistant_output.tool_calls[0]["function"]["name"] == "get_current_time":
        tool_info = {"name": "get_current_time", "role": "tool"}
        tool_info["content"] = get_current_time()
    print(f"工具输出信息：{tool_info['content']}\n")
    messages.append(tool_info)

    # 模型的第二轮调用，对工具的输出进行总结
    second_response = get_response(messages)
    # print(f"大模型第二轮输出信息：{second_response}\n")
    print(f"{second_response.output.choices[0].message['content']}")
    return second_response.output.choices[0].message['content']

    
    if response.status_code == 200:
        return response.output.choices[0].message.content
        # print(response.output.choices[0].message.content)
    else:
        print(f"HTTP返回码：{response.status_code}")
        print(f"错误码：{response.code}")
        print(f"错误信息：{response.message}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
    # 这里用qwen-vl举例，实际可替换为你的API调用
    # 你可以用qwen-vl的chat接口，或openai的接口
    # 这里只做简单模拟，实际请替换为真实API调用
    # return 调用大模型API的结果
    # 例如：
    # response = dashscope.MultiModalConversation.call(...)
    # return response.output.choices[0].message.content[0]["text"]
        return f"知识库AI的回答：你问了“{query}”"


# @app.post("/chat")
# async def chat(request: Request):
#     # data = await request.json()
#     raw_body = await request.body()
#     data = json.loads(raw_body.decode('utf-8', errors='ignore'))  # 忽略非法字符
#     user_input = data.get("message", "")

#     def event_stream():
#         answer = call_knowledge_model_api(user_input)
#         # return answer
#         # 流式输出
#         for ch in answer:
#             yield ch
#             # time.sleep(0.01)
#     # return user_input #call_knowledge_model_api(user_input)
#     return StreamingResponse(event_stream(), media_type="text/plain")

# 挂载静态文件目录，方便前端资源访问
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# 添加根路由，返回index.html
@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")



# 连接redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    task_id = str(uuid.uuid4())
    from celery_worker import ai_task
    result = ai_task.apply_async(args=[user_input], task_id=task_id)
    def event_stream(answer):
        answer = call_knowledge_model_api(user_input)
        # return answer
        # 流式输出
        for ch in answer:
            yield ch
            # time.sleep(0.01)
    # return user_input #call_knowledge_model_api(user_input)
    return StreamingResponse(event_stream(result), media_type="text/plain")
    return JSONResponse({"task_id": task_id})

@app.get("/chat_result/{task_id}")
async def chat_result(task_id: str):
    from celery_worker import celery_app
    result = celery_app.AsyncResult(task_id)
    if result.ready():
        return JSONResponse({"status": "done", "result": result.result})
    else:
        return JSONResponse({"status": "pending"})



@app.post("/judge")
async def judge(
    comment_text: str = Form(None),
    reply_text: str = Form(None),
    related_text: str =Form(None),
    comment_img: UploadFile = None,
    reply_img: UploadFile = None
):
    comment_img_path, reply_img_path = None, None
    if comment_img.filename:
        comment_img_path = os.path.join(UPLOAD_DIR, comment_img.filename)
        # shutil.copy(comment_img,comment_img_path)
        try:
            with open(comment_img_path, "wb") as f:
                shutil.copyfileobj(comment_img.file, f)
        except:
            pass
    if reply_img.filename:
        reply_img_path = os.path.join(UPLOAD_DIR, reply_img.filename)
        # shutil.copy(reply_img,reply_img_path)
        try:
            with open(reply_img_path, "wb") as f:
                shutil.copyfileobj(reply_img.file, f)
        except:
            pass
    print("comment_img_path",comment_img_path)
    print("reply_img_path",reply_img_path)
    result = call_ernie_multimodal_judge(comment_text, comment_img_path, reply_text, reply_img_path,related_text)
    return JSONResponse({
        "result": result,
        "comment_img_path": comment_img_path,
        "reply_img_path": reply_img_path
    })



if __name__ == "__main__":
    uvicorn.run(app, host="192.168.31.94", port=8000)
