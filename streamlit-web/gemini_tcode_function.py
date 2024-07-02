import streamlit as st 
from dotenv import load_dotenv
import os
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ClientConnectorError
from asyncio.exceptions import TimeoutError
import json

from google.cloud import aiplatform
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
TCODE_API_ENDPOINT = os.getenv('TCODE_API_ENDPOINT')
MODEL_NAME = "gemini-1.0-pro-001"
location = "asia-northeast3" # Seoul

aiplatform.init(project=PROJECT_ID, location = location)

async def fetch(session, url, data):
    headers = {'Content-Type': 'application/json'}
    async with session.post(url, data=json.dumps(data), headers=headers) as response:
        return await response.json()
    

async def get_tcode(old_menu_id: str, old_menu_name: str) -> str:
    """
    API 호출을 통해서 TCode 정보를 가져온다. 
    TCODE_API_ENDPOINT/menu_search
    params:
    {
        "old_menu_id": "1294"  # optional name 보다 우선 검색
        "old_menu_name": "통합거래처 일괄 업로드" # optional
    }
    response: 
    [
        {
            '__id': '46f5a4a8f1954bd0bfebe94f669dfaef'
            "menu_id": "1294",
            "tcode": "ZSDR1631",
            "corp_category": "공통법인",
            "menu_hier_kor": "ERP-영업-마케팅-기준정보-상세착지 관리-null-null"
        }
    ]
    error handling: https://speedsheet.io/s/aiohttp?q=errors-only#z4Gj
    """ 

    data = {}
    if old_menu_id:
        data["old_menu_id"] = old_menu_id
    if old_menu_name:
        data["old_menu_name"] = old_menu_name

    try:
        async with aiohttp.ClientSession() as session:
            url = f"{TCODE_API_ENDPOINT}/menu_search"
            response = await fetch(session, url, data)
            return response
    except ClientResponseError as exception:
        raise Exception(json.dumps({"error_code": "ClientResponseError", "error": exception.message}))
    except ClientConnectorError as exception:
        raise Exception(json.dumps({"error_code": "ClientConnectorError", "error": exception.message}))
    except TimeoutError as exception:
        raise Exception(json.dumps({"error_code": "TimeoutError", "error": exception.message}))

@st.cache_data(show_spinner=False)
def get_tcode_from_prompt(user_input: str) -> tuple:
    """
    참고: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling?hl=ko
    """
    prompt = f"""
    당신은 TCode API의 도움이 입니다. 
    입력을 보고 기존 시스템의 프로그램 이름이나 메뉴명으로 새로운 시스템 TCode를 찾도록 도와주세요. TCode의 예: ZFIE1080, ZSFR_2110A, ZSFR_APLIST. 만약 관련이 없는 입력이라면 None이라고 명확히 알려주세요. 
    
    입력: {user_input}
    """

    get_tcode_func = FunctionDeclaration(
            name="get_tcode",
            description="기존 사용하던 프로그램 ID 또는 기존 메뉴이름으로 새로운 ERP 시스템의 TCode를 가져오는 함수.",
            parameters={
                "type": "object",
                "properties": {
                    "old_menu_id": {
                        "type": "string",
                        "description": "숫자 4자리에서 5자리로 표현된 기존에 사용하던 프로그램 ID. 화면번호로 부르기도 한다. 이 파라미터는 선택사항.  예) 2524, 18018"
                    },
                    "old_menu_name": {
                        "type": "string",
                        "description": "기존 시스템에서 사용하던 메뉴이름. 이 파라미터는 선택사항."
                    }
                }
            }
        )

    # Define a tool that includes the get_tcode_func
    get_tcode_tool = Tool(
        function_declarations=[get_tcode_func],
    )

    # Define the user's prompt in a Content object that we can reuse in model calls
    user_prompt_content = Content(
        role="user",
        parts=[
            Part.from_text(prompt),
        ],
    )

    # Model Initialization
    model = GenerativeModel(MODEL_NAME)
    
    # Send the prompt and instruct the model to generate content using the Tool that you just created
    response = model.generate_content(
        user_prompt_content,
        generation_config=GenerationConfig(temperature=0),
        tools=[get_tcode_tool],
    )

    print(response)

    response_function_call_content = response.candidates[0].content

    function_call = response_function_call_content.parts[0].function_call

    function_handlers = {
      "get_tcode": get_tcode,
    }

    if function_call.name in function_handlers:
      function_name = function_call.name
      # Extract the arguments to use in your API call
      old_menu_id_arg = (function_call.args["old_menu_id"] if "old_menu_id" in function_call.args else None)
      old_menu_name_arg = (function_call.args["old_menu_name"] if "old_menu_name" in function_call.args else None)
      
      if old_menu_id_arg or old_menu_name_arg:
        function_response = asyncio.run(function_handlers[function_name](old_menu_id=old_menu_id_arg, old_menu_name=old_menu_name_arg))

        print(f"function_response: {function_response}")

        if function_response == "[]":
            return None, None

        # Return the API response to Gemini so it can generate a model response or request another function call
        summary_prompt = """
        당신은 기존 시스템의 프로그램 ID 또는 메뉴이름으로 새로운 시스템의 TCode에 대해서 설명해주는 도우미야. 
        함수 결과를 바탕으로 회사구분(corp_category), 기존 메뉴ID(menu_id), 기존 메뉴 구성(menu_hier_kor) 그리고 새로운 시스템의 TCode를 설명해주세요. 
        만약 TCode를 찾을 수 없으면 "없음"이라고 정확히 알려줘.
        """
        response = model.generate_content(
            [
                user_prompt_content,  # User prompt
                response_function_call_content,  # Function call response
                Content(
                    parts=[
                        Part.from_function_response(
                            name="get_tcode",
                            response={
                                "content": function_response,  # Return the API response to Gemini
                            },
                        )
                    ],
                ),
            ],
            tools=[get_tcode_tool],
        )

        # Get the model summary response
        summary = response.candidates[0].content.parts[0].text
        print(summary)
        return summary, function_response
      else:
          # args 가 없으면 호출해봤자 의미 없음. 
          return None, None
    else:
        # 원하는 Function이 찾아 지지 않음. 
        return None, None