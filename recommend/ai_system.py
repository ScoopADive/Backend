import aiohttp
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

# 동기 처리
class CustomPrompt():
    def __init__(self, user):
        self.user = user
        self.preferences = None
        if user is not None:
            self.preferences = Preferences.objects.filter(user=user).first()

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

    def openai_request(self):
        response = client.responses.parse(
            model="gpt-4o-mini-2024-07-18",
            input=[
                {
                    "role": "system",
                    "content": "You are a diving spot recommend assistant. Return exactly three diving spots in JSON format with fields: region, country, intro. Do not add extra text or explanation.",
                },
                {"role": "user", "content": self.prompt},
            ],
            text_format=SpotsExtractionList,
        )
        return response.output_parsed.spots


# 비동기 처리
class AsyncCustomPrompt(CustomPrompt):
    async def async_openai_request(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini-2024-07-18",
                    "input": [
                        {"role": "system", "content": "*."},
                        {"role": "user", "content": self.prompt},
                    ],
                },
            ) as resp:
                data = await resp.json()

        # 결과 파싱
        # OpenAI API의 response 형식에 따라 조정 필요
        try:
            output = data["output"][0]["content"][0]["text"]
            parsed = SpotsExtractionList.model_validate_json(output)
            return parsed.spots
        except Exception as e:
            print("Parsing error:", e)
            return []




