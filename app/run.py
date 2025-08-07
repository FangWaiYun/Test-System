from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from domain.qclass import Question, QuestionSet
from function import test_generate,test_ai_generate,save_question,save_question_lots
from pathlib import Path
import json

def load_questions(asset_dir_path: str):
    asset_dir = Path("/Users/wuzhehao/Library/Mobile Documents/com~apple~CloudDocs/lab/Github/Test-System/asset")#不知道bug哪来的，暂时用文本
    questions = []
    for file in asset_dir.iterdir():
        print("🧾 文件名：", file.name, "| 是否文件？", file.is_file())
    print("开始查找 JSON 文件...")
    json_files = list(asset_dir.glob("*.json"))
    print(f"找到 {len(json_files)} 个 json 文件")
    ls=[]
    for file in asset_dir.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"⚠️ 文件 {file.name} 中的数据不是列表，跳过。")
                    continue
                qs=QuestionSet(data[0].get("theme","未知主题"))
                print("主题为",qs.theme)
                for item in data:
                    # 处理 last_indexed 字段
                    raw_time = item.get("last_indexed", [])
                    if isinstance(raw_time, list) and raw_time:
                        last_indexed = [datetime.fromisoformat(t) for t in raw_time]
                    else:
                        last_indexed = [datetime.now()]

                    q = Question(
                        question=item.get("question", ""),
                        answer=item.get("answer", ""),
                        theme=item.get("theme", ""),
                        type=item.get("type", ""),
                        explanation=item.get("explanation", None),
                        comment=item.get("comment", None),
                        last_indexed=last_indexed
                    )
                    print(f"加载题目：{q.question}，主题：{q.theme}")
                    questions.append(q)
                qs.questions=questions
                ls.append(qs)
        except Exception as e:
            print(f"❌ 读取文件 {file.name} 失败：{e}")
    print(f"总共加载 {len(ls)} 组题目")
    return ls
def run():
    asset_path = "/Users/wuzhehao/Library/Mobile Documents/com~apple~CloudDocs/lab/Github/text-manange-system/Text-Manage-System/asset"
    questions=load_questions(asset_path)
    while True:
        behavior = input("请输入行为（1:强筛选生成试卷，2:弱筛选生成试卷，3:ai读取生成题目(未实现)，4:自己保存题目，5:批量保存题目）：")
        if behavior == "stop" or behavior == "0" or behavior == "exit" or behavior == "退出" or behavior == "end":
            break
        elif behavior == "1":
            print("输入题目")
            print(len(questions[0].questions))
            test_generate(questions)#有问题，未解决
        elif behavior == "2":
            test_ai_generate(questions)
        elif behavior == "3":
            url = input("请输入文章URL：")
        elif behavior == "4":
            save_question()
        elif behavior == "5":
            save_question_lots()
        else:
            print("未知行为，请重试。")

