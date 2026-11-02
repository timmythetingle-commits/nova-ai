"""A beginner-friendly, offline AI chatbot using a Naive Bayes intent classifier.

Run: python python_ai_chatbot.py
Commands: /help, /teach, /quit
No external packages or API keys required.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).with_name('chatbot_knowledge.json')
STARTER_DATA = {
    'greeting': {'examples': ['hello', 'hi', 'hey', 'good morning', 'howdy'],
                 'answer': 'Hello! What would you like to talk about?'},
    'farewell': {'examples': ['bye', 'goodbye', 'see you later', 'gotta go'],
                 'answer': 'Goodbye! Have a great day.'},
    'identity': {'examples': ['who are you', 'what is your name', 'are you an ai', 'tell me about yourself'],
                 'answer': 'I am a small Python AI chatbot. I classify your messages to choose responses.'},
    'coding': {'examples': ['help me code', 'what is python', 'how do i program', 'teach me programming', 'write code'],
               'answer': 'Python is a beginner-friendly programming language. What would you like to build?'},
    'study': {'examples': ['help me study', 'i have homework', 'how should i prepare for a test', 'study tips'],
              'answer': 'Try breaking your work into small tasks and testing yourself as you learn.'},
    'thanks': {'examples': ['thank you', 'thanks', 'thanks a lot', 'i appreciate it'],
               'answer': "You're welcome!"},
}


def tokenize(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def load_knowledge():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except (OSError, ValueError):
            print('Knowledge file could not be loaded; using starter knowledge.')
    return STARTER_DATA.copy()


def save_knowledge(knowledge):
    with DATA_FILE.open('w', encoding='utf-8') as f:
        json.dump(knowledge, f, indent=2, ensure_ascii=False)


class IntentAI:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        self.train()

    def train(self):
        self.word_counts = defaultdict(Counter)
        self.total_words = Counter()
        self.example_counts = Counter()
        self.vocabulary = set()
        for intent, item in self.knowledge.items():
            for example in item['examples']:
                words = tokenize(example)
                self.word_counts[intent].update(words)
                self.total_words[intent] += len(words)
                self.example_counts[intent] += 1
                self.vocabulary.update(words)

    def classify(self, text):
        words = tokenize(text)
        if not words or not any(w in self.vocabulary for w in words):
            return None, 0.0
        total_examples = sum(self.example_counts.values())
        vocabulary_size = max(len(self.vocabulary), 1)
        scores = {}
        for intent in self.knowledge:
            score = math.log(self.example_counts[intent] / total_examples)
            denominator = self.total_words[intent] + vocabulary_size
            for word in words:
                score += math.log((self.word_counts[intent][word] + 1) / denominator)
            scores[intent] = score
        best = max(scores, key=scores.get)
        # Avoid highly confident guesses when the message barely matches training data.
        matched = sum(word in self.word_counts[best] for word in words)
        if matched == 0:
            return None, 0.0
        shift = max(scores.values())
        exps = {name: math.exp(value - shift) for name, value in scores.items()}
        confidence = exps[best] / sum(exps.values())
        return best, confidence

    def reply(self, text):
        # Known training phrases should always receive their intended response.
        normalized = tokenize(text)
        for item in self.knowledge.values():
            if any(tokenize(example) == normalized for example in item["examples"]):
                return item["answer"]
        intent, confidence = self.classify(text)
        if intent is None or confidence < 0.35:
            return "I'm not sure how to answer that yet. Type /teach to teach me a new topic."
        return self.knowledge[intent]['answer']

    def teach(self):
        print('\nTeach me a new topic!')
        label = input('Topic name (e.g. music): ').strip().lower()
        if not re.fullmatch(r'[a-z0-9_-]{1,30}', label):
            print('Use 1–30 letters, numbers, underscores, or hyphens for a topic name.')
            return
        examples = input('Example messages, separated by | : ').split('|')
        examples = [x.strip() for x in examples if x.strip()]
        answer = input('Reply I should give: ').strip()
        if not examples or not answer:
            print('Please provide examples and a reply.')
            return
        if label in self.knowledge:
            self.knowledge[label]['examples'].extend(examples)
            self.knowledge[label]['answer'] = answer
        else:
            self.knowledge[label] = {'examples': examples, 'answer': answer}
        save_knowledge(self.knowledge)
        self.train()
        print('Learned! Your knowledge was saved to chatbot_knowledge.json.\n')


def main():
    bot = IntentAI(load_knowledge())
    print('Python AI Chatbot — offline and ready!')
    print('Type /teach to add a topic, /help for commands, or /quit to exit.\n')
    while True:
        try:
            message = input('You: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nAI: Goodbye!')
            break
        if not message:
            continue
        if message.lower() == '/quit':
            print('AI: Goodbye!')
            break
        if message.lower() == '/help':
            print('Commands: /teach (add knowledge), /quit (exit), /help (show commands)')
        elif message.lower() == '/teach':
            bot.teach()
        else:
            print('AI:', bot.reply(message))


if __name__ == '__main__':
    main()
