#read question and save as a .json file
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from datetime import datetime
from pathlib import Path
def save_question():
    """
    将题目保存到 asset 目录下的指定 theme.json 文件中：
    - 若已存在 theme.json，则将题目追加进去；
    - 若不存在，则新建文件并写入。
    """
    question_data = {}
    question_data["theme"] = input("请输入题目主题：")
    
    question_data["type"] = input("请输入题目类型（0，选择题/1，简答题）：")
    if question_data["type"] not in ["0", "1"]:
        print("⚠️ 题目类型输入错误，仅支持 0（选择题）或 1（简答题）。")
        return
    else:
        if question_data["type"] == "0":
            question_data["question"] = input("请输入题目内容（如选择： 是一 是二 是三 是四?）：").split()
        else:
            question_data["question"] = input("请输入题目内容（如什么是昼夜节律？）：")
    
    question_data["answer"] = input("请输入题目答案：")
    question_data["explanation"] = [input("请输入题目解释：")]
    question_data["comment"] = []
    question_data["last_indexed"] = [datetime.now().isoformat()]

    theme=question_data["theme"]
    asset_dir = Path(__file__).resolve().parent.parent / "asset"
    asset_dir.mkdir(parents=True, exist_ok=True)

    # 目标文件路径
    target_file = asset_dir / f"{theme}.json"

    if target_file.exists():
        # 已存在文件：读取旧内容（必须是 list），追加题目
        try:
            with target_file.open("r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    raise ValueError(f"{theme}.json 内容不是 list。")
        except json.JSONDecodeError:
            print(f"⚠️ {theme}.json 内容无法解析，将重写。")
            existing_data = []
    else:
        # 不存在文件：新建一个
        existing_data = []

    # 追加题目
    existing_data.append(question_data)

    # 回写到文件
    with target_file.open("w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到 {target_file}")
    return