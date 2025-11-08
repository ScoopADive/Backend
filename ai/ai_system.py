from openai import OpenAI
from pydantic import BaseModel
from typing import List

from django.conf import settings

from settings.models import Preferences

OPENAI_API_KEY = settings.OPENAI_API_KEY

print('openaiapikey: ', OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

class SpotExtraction(BaseModel):
    region: str
    country: str
    intro: str

class SpotsExtractionList(BaseModel):
    spots: List[SpotExtraction]

class CustomPrompt():
    def __init__(self, user):
        self.user = user
        self.preferences = None
        if user is not None:
            self.preferences = Preferences.objects.filter(user=user).first()
        self.prompt = ""

    def run_prompt(self):
        # 유저 정보가 주어지지 않았을 때
        if self.user is None or self.preferences is None:
            self.prompt = "I am a beginner. Not experienced in Scuba Diving, so I need to start from the scratch."
        # 유저 정보가 주어지지 않았을 때
        else:
            self.prompt = f"""My personal info: 
                              Birthday: {self.preferences.birthday}. 
                              Residence: {self.preferences.residence}. 
                              Minimum Budget: {self.preferences.budget_min}. 
                              Maximum Budget: {self.preferences.budget_max}. 
                              Gender: {self.preferences.gender}. 
                              Preferred Activities: {self.preferences.preferred_activities}. 
                              Preferred Atmosphere: {self.preferences.preferred_atmosphere}. 
                              Last Dive Date: {self.preferences.last_dive_date}. 
                              Preferred Diving: {self.preferences.preferred_diving}. 
                              License: {self.user.license}. 
                              Introduction: {self.user.introduction}. """

        response = client.responses.parse(
            model="gpt-4o-mini-2024-07-18",
            input=[
                {
                    "role": "system",
                    "content": "You are a diving spot recommendation assistant. Return exactly three diving spots in JSON format with fields: region, country, intro. Do not add extra text or explanation.",
                },
                {"role": "user", "content": self.prompt},
            ],
            text_format=SpotsExtractionList,
        )
        return response.output_parsed.spots


class TestPrompt():
    def __init__(self):
        # User 정보가 없을 때.
        # self.prompt_obj = CustomPrompt(None)
        # User 정보가 주어졌을 때
        from auths.models import User

        # Begginer
        testuser = User.objects.get(id=1)
        # Germany 특화
        testuser2 = User.objects.get(id=2)

        # CustomPrompt 객체 생성
        self.prompt_obj = CustomPrompt(testuser2)

    def run_prompt(self):

        import json
        result = self.prompt_obj.run_prompt()
        return result
        #
        # # ✅ ParsedResponse 객체를 dict로 변환
        # if hasattr(result, "model_dump"):
        #     result = result.model_dump()
        #
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        # return result


