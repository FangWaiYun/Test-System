from datetime import datetime
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from domain.qclass import Question, QuestionSet
def score(question):
    # 防御性检查：确保 last_indexed 存在且非空
    if not hasattr(question, 'last_indexed') or not question.last_indexed:
        return 0
    
    # 直接使用 datetime 对象（无需转换）
    last_time = question.last_indexed[-1]
    
    now = datetime.now()
    time_diff = (now - last_time).total_seconds()
    revisit_penalty = len(question.last_indexed)
    
    # 分数策略：越久未访问 + 访问次数少 -> 分越高
    return time_diff - revisit_penalty * 1000
def rank(questions):#embedder?
    m = [[score(q), q] for q in questions]  # 列表推导式更简洁
    m.sort(reverse=True, key=lambda x: x[0])  # 按得分从高到低排序
    return [q for _, q in m]  # 只返回排序后的题目列表
def show(paper):
    """
    for i in range(len(paper)):
        print(f"题目{i+1}: {paper[i].topic}")
        
        if paper[i].choice_format:
            for key, value in paper[i].choice_format.items():
                print(f"{key}: {value}")
                """
    print("题目列表：")
    for i in range(len(paper)):
        print(f"题目{i+1}: {paper[i].question}")
    
    return
def show_ans(paper):
    print("题目答案：")
    for i in range(len(paper)):
        print(f"题目{i+1}: {paper[i].question}")
        
        print(f"题目{i+1}答案: {paper[i].answer}")

        print(f"题目{i+1}解释: {paper[i].explanation}")
    return
def test_ai_generate(questionsets):
    prompt=input("请输入需要测试的内容：")
    k=int(input("请输入需要生成的题目数量："))
    if k <= 0:
        print("⚠️ 题目数量必须大于 0。")
        return
    if len(questionsets) == 0:
        print("⚠️ 没有可用的题目集。")
        return
    paper=[]
    themes= [q.theme for q in questionsets]
    new_themes=get_themes(prompt,themes)
    new_set=[]
    for i in range(len(questionsets)):
        if questionsets[i].theme in new_themes:
            for j in range(len(questionsets[i].questions)):
                new_set.append(questionsets[i].questions[j])
    new_set=rank(new_set)
    if len(new_set) < k:
        print(f"⚠️ 题目数量不足，只有 {len(new_set)} 个题目可用。")
        k = len(new_set)
    paper=new_set[:k]
    show(paper)
    input("按回车键继续...3")
    input("按回车键继续...2")
    input("按回车键继续...1")
    show_ans(paper)
def test_paper(paper):#ai改试卷
    for i in range(len(paper)):
        print(f"题目{i+1}: {paper[i].question}")
    return


def get_themes(prompt: str,themes: list[str]) -> list[str]:
    """
    获取与prompt相关的k个主题
    :param prompt: 用户输入的提示信息
    :param k: 需要的主题数量
    :param themes: 可供选择的主题列表（可选，若为空则不使用）
    :return: 新的主题列表（长度为k）
    """
    system_prompt = "你是一个善于主题提取的助手，根据给定提示，从中总结出多个相关主题，返回一个Python列表。"
    
    # 构造完整的Prompt
    user_prompt = f"""
根据以下提示信息，生成多个相关主题，要求紧密相关、语言简洁明确。

提示信息：
{prompt}

已有主题（只能从这些主题中选择，避免重复）：
{themes if themes else "None"}

请只返回Python格式的字符串列表，例如：["theme1", "theme2", "theme3"]，可以多返回几个主题，至少返回一个主题，主题必须选自已有主题列表
"""

    payload = {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    try:
        res = requests.post("http://localhost:11434/api/chat", json=payload)
        res.raise_for_status()
        content = res.json()["message"]["content"]
        print("🎯 GPT回应：", content)
        # 安全地解析为列表
        return eval(content.strip())
    except Exception as e:
        print(f"❌ 调用GPT失败: {e}")
        return []   
    


