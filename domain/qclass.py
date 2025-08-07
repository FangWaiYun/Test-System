# class/question.py
from typing import Optional, List
from datetime import datetime

class Question:
    def __init__(
        self,
        question: str,
        answer: str,
        theme: str,
        type: str,
        explanation: Optional[str] = None,
        comment: Optional[str] = None,
        last_indexed: Optional[datetime] = None
    ):
        self.question = question  
        self.answer = answer 
        self.type = type 
        self.theme= theme
        self.comment = comment
        self.explanation = explanation  # 答案解释
        self.last_indexed = last_indexed or [datetime.now()]  # 上次访问时间

    def update_index(self, new_index: int):
        self.index = new_index
        self.last_indexed = datetime.now()
    def update_mark(self, comment: str):
        self.comment = comment
        self.last_indexed = datetime.now()
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "topic": self.topic,
            "choice_format": self.choice_format,
            "short_answer_format": self.short_answer_format,
            "explanation": self.explanation,
            "last_indexed": self.last_indexed.isoformat(),
        }


class QuestionSet:
    def __init__(self, theme: str, questions: Optional[List[Question]] = None, last_accessed: Optional[datetime] = None):
        self.theme = theme  # 大主题，如“概率论”
        self.questions = questions or []  # 包含的题目
        self.last_accessed = last_accessed or datetime.now()
        self.num_questions = len(self.questions)  # 题目数量

    def add_question(self, question: Question):
        self.questions.append(question)
        self.num_questions += 1
        self.last_accessed = datetime.now()

    def get_question_by_index(self, index: int) -> Optional[Question]:
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "theme": self.theme,
            "questions": [q.to_dict() for q in self.questions],
            "last_accessed": self.last_accessed.isoformat(),
        }