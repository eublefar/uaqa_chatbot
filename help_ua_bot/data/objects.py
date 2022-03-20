import logging
import time


from help_ua_bot.config import (
    QNA_SUBSCRIPTION_KEY,
    QNA_MAKER_ENDPOINT,
    KNOWLEDGEBASE_ID,
    ENDPOINT,
)

import requests


class Unverified:
    """
    Class for storing unverified messages
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(Unverified, "unverified"):
            Unverified.unverified = []

    @classmethod
    def pop(cls):
        """
        Removes and returns the first message from the list
        :return: Message object
        """
        if len(cls.unverified) > 0:
            return cls.unverified.pop()
        else:
            return None


class URL(Unverified):
    """
    Class for storing unverified URLs
    """

    def __init__(self, url):
        super().__init__()
        self.url = url

    def save(self):
        """
        Saves the URL to the database
        :return: None
        """
        self.__class__.__bases__[0].unverified.append(self)

    def to_string(self):
        """
        Returns the URL as a string
        :return: String
        """
        return self.url

    def verify(self):
        """
        Verifies the URL
        :return: None
        """

        headers = {
            "Ocp-Apim-Subscription-Key": f"{QNA_SUBSCRIPTION_KEY}",
            # Already added when you pass json= but not when you pass data=
            # 'Content-Type': 'application/json',
        }

        params = {
            "api-version": "2021-10-01",
        }
        json_data = [
            {
                "op": "add",
                "value": {
                    "displayName": f"source {self.url}",
                    "sourceKind": "url",
                    "sourceUri": self.url,
                    "sourceContentStructureKind": "auto",
                },
            },
        ]
        response = requests.patch(
            f"https://{ENDPOINT}.api.cognitive.microsoft.com/language/query-knowledgebases/projects/{KNOWLEDGEBASE_ID}/sources",
            headers=headers,
            params=params,
            json=json_data,
        )

        print("Updated knowledge base.")
        print(response.__dict__)


class Question(Unverified):
    """
    Class for storing unverified questions
    """

    def __init__(self, question, answer):
        super().__init__()
        self.question = question
        self.answer = answer

    def save(self):
        """
        Saves the question to the database
        :return: None
        """
        self.__class__.__bases__[0].unverified.append(self)

    def to_string(self):
        """
        Returns the question as a string
        :return: String
        """
        return f"Question: {self.question}\nAnswer: {self.answer}"

    def verify(self):
        """
        Verifies the question
        :return: None
        """
        headers = {
            "Ocp-Apim-Subscription-Key": f"{QNA_SUBSCRIPTION_KEY}",
            # Already added when you pass json= but not when you pass data=
            # 'Content-Type': 'application/json',
        }

        params = {
            "api-version": "2021-10-01",
        }

        json_data = [
            {
                "op": "add",
                "value": {
                    "id": 1,
                    "answer": self.answer,
                    "source": "source1",
                    "questions": [self.question,],
                    "metadata": {},
                    "dialog": {"isContextOnly": False, "prompts": [],},
                },
            },
        ]

        response = requests.patch(
            f"https://{ENDPOINT}.api.cognitive.microsoft.com/language/query-knowledgebases/projects/{KNOWLEDGEBASE_ID}/qnas",
            headers=headers,
            params=params,
            json=json_data,
        )
        print("Updated knowledge base.")
        print(response.__dict__)
