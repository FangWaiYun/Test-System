
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from domain.qclass import Question, QuestionSet
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
def test_generate(questions):
    require=input("请输入需要测试的内容：")
    paper=[]
    for i in range(len(questions)):
        if questions[i].theme==require:
            for j in range(len(questions[i].questions)):
                paper.append(questions[i].questions[j])
    show(paper)
    input("按回车键继续...3")
    input("按回车键继续...2")
    input("按回车键继续...1")
    show_ans(paper)
def test_paper(paper):#ai改试卷
    for i in range(len(paper)):
        print(f"题目{i+1}: {paper[i].question}")
    return
        
    


