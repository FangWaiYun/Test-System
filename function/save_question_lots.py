#read question and save as a .json file
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from datetime import datetime
from pathlib import Path
def save_question_lots():
    """
    将题目保存到 asset 目录下的指定 theme.json 文件中：
    - 若已存在 theme.json，则将题目追加进去；
    - 若不存在，则新建文件并写入。
    """
    theme = input("请输入题目主题：")
    num_questions = int(input("请输入需要保存的题目数量："))

    if num_questions <= 0:
        print("⚠️ 题目数量必须大于 0。")
        return
    while num_questions > 0:
        num_questions -= 1
        question_data = {}
        a=input()
        b=input()
        c=input()
        d=input()
        question_data["theme"] = theme
    
        question_data["type"] = a
        if question_data["type"] not in ["0", "1"]:
            print("⚠️ 题目类型输入错误，仅支持 0（选择题）或 1（简答题）。")
            return
        else:
            if question_data["type"] == "0":
                question_data["question"] = b.split()
            else:
                question_data["question"] = b
        
        question_data["answer"] = c
        question_data["explanation"] = d
        question_data["comment"] = []
        question_data["last_indexed"] = [datetime.now().isoformat()]

        
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