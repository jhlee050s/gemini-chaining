import streamlit as st
from google import genai

# --- 페이지 설정 ---
st.set_page_config(page_title="Gemini 프롬프트 체이너", page_icon="🚀")

st.title("🚀 프롬프트 자동 최적화 요약기")
st.markdown("""
사용자의 거친 입력을 **'고품질 프롬프트'**로 변환한 뒤, 
그 프롬프트를 다시 실행하여 **최상의 결과물**을 도출합니다.
""")

# --- 사이드바: API 설정 ---
with st.sidebar:
    st.header("설정")
    api_key = "AIzaSyC3TfyxoHOzxL83V2bdnDffavqv7Ocgx68"
    #api_key = st.text_input("Google API Key를 입력하세요", type="password")
    #st.info("[API Key 발급받기](https://aistudio.google.com/)")
    
    # 모델 선택
    model_name = st.selectbox("사용할 모델", [
    "gemini-2.5-flash", 
    "gemini-2.5-pro", 
])
# --- 메인 화면: 입력창 ---
user_input = st.text_area(
    "요청 사항을 입력하세요 (예: 논문 대본, 복잡한 지시 등)",
    height=200,
    placeholder="제미나이야ㅠㅠ 이 논문을 요약해줘ㅠㅠ\n\nHi everyone, I’m Juhyeong Lee from..."
)

# --- 로직 실행 ---
if st.button("자동 최적화 실행"):
    if not api_key:
        st.error("사이드바에 API Key를 입력해주세요!")
    elif not user_input:
        st.warning("내용을 입력해주세요.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Step 1: 프롬프트 생성 (프롬프트 엔지니어링 단계)
            with st.status("1단계: 고품질 프롬프트 생성 중...", expanded=True) as status:
                prompt_gen_instruction = '''
당신은 '프롬프트 엔지니어링 전문가'이자 '프롬프트 아키텍트'입니다.
당신의 목표는 사용자가 입력한 단순하고 불완전한 요청사항을 분석하여, LLM 성능을 극대화할 수 있는 [유니버설 마스터 프롬프트(Universal Master Prompt)] 형태로 변환하여 출력하는 것입니다.

사용자가 "이 논문 요약해 줘", "파이썬 코드 짜 줘"와 같이 단순하게 요청하더라도, 당신은 문맥을 추론하여 아래의 구조를 갖춘 완벽한 프롬프트를 생성해야 합니다.또한 생성물에는 부연설명 없이 오직 프롬포트만이 plain text로 있어야 합니다. 

### [프롬프트 생성 규칙]

1. **구조 준수**: 반드시 아래의 6단 구조를 따르십시오.
   - # 1. 역할 정의 (Persona): 주제에 맞는 최고 전문가 페르소나 부여
   - # 2. 작업 개요 (Top Instruction): 명확한 동사로 작업 정의
   - # 3. 배경 및 맥락 (Context): (사용자 입력에서 추론하거나 일반적인 목적 설정)
   - # 4. 데이터 입력 (Input Data): 데이터가 있다면 """ 기호로 감싸기, 없다면 빈칸
   - # 5. 세부 지침 (Constraints): 형식, 톤앤매너, 길이, CoT(단계별 사고) 포함
   - # 6. 핵심 지시 반복 (Bottom Instruction): 샌드위치 구조로 지시사항 재강조

2. **자동 추론 및 보완**:
   - 사용자가 구체적인 역할을 지정하지 않았다면, 해당 작업에 가장 적합한 전문가(예: "20년 경력의 시니어 개발자", "논리적인 데이터 분석가")를 자동으로 설정하세요.
   - '단계별로 생각하라(Chain of Thought)'는 지침을 항상 포함하세요.

3. **출력 형식**:
   - 생성된 프롬프트는 사용자가 바로 복사해서 쓸 수 있도록 **코드 블록(Code Block)** 안에 담아서 출력하세요.
   - 코드 블록 밖에는 해당 프롬프트의 의도나 수정 팁을 간략히 설명하세요.

### [마스터 프롬프트 템플릿]

(당신이 출력해야 할 결과물의 형태입니다)

```markdown
# 1. 역할 정의 (Persona)
당신은 [  주제  ] 분야의 세계적인 전문가이자, 논리적인 문제 해결사입니다.
전문적인 지식을 바탕으로 가장 정확하고 통찰력 있는 답변을 제공하세요.

# 2. 작업 개요 (Instruction)
당신의 핵심 임무는 [  작업 내용  ] 작업을 수행하는 것입니다.
(데이터가 있다면) 아래 제공된 """데이터"""를 바탕으로 작업을 진행하세요.

# 3. 배경 및 맥락 (Context)
이 작업의 목적은 [  목적  ] 입니다.
주된 독자(타겟)는 [  타겟 독자  ] 입니다.

# 4. 데이터 입력 (Input Data)
아래 삼중 따옴표(""")로 감싸진 텍스트/코드/데이터를 분석하세요:
"""
[여기에 사용자의 데이터/텍스트 붙여넣기]
"""

# 5. 세부 지침 및 제약조건 (Constraints)
작업을 수행할 때 다음 규칙을 엄격히 준수하세요:
1. 결과물은 반드시 [  형식  ] 으로 작성하세요.
2. 설명은 [  톤앤매너  ] 하게 작성하세요.
3. 답변을 내리기 전에 **단계별로 생각(Step-by-step)**하여 논리적 비약이 없도록 하세요.

# 6. 핵심 지시 반복 (Instruction)
다시 한번 강조합니다.
위의 데이터와 맥락을 고려하여, [  세부 지침  ]을 하나도 빠짐없이 지키며 [  작업 개요  ]를 완수하세요.
'''
                
                gen_response = client.models.generate_content(
                    model=model_name,
                    config={'system_instruction': prompt_gen_instruction},
                    contents=[user_input]
                )
                generated_prompt = gen_response.text
                st.write("✅ 프롬프트 최적화 완료")
                
                # 생성된 프롬프트 확인 (접기 메뉴)
                with st.expander("생성된 내부 프롬프트 보기"):
                    st.code(generated_prompt)

                # Step 2: 최종 결과 도출
                status.update(label="2단계: 최적화된 프롬프트로 작업 실행 중...")
                final_response = client.models.generate_content(
                    model=model_name,
                    contents=[generated_prompt]
                )
                status.update(label="✅ 모든 작업 완료!", state="complete")

            # 최종 결과 출력
            st.divider()
            st.subheader("🎯 최종 분석 결과")
            st.markdown(final_response.text)
            
            # 결과 복사 버튼 (간접 지원)
            st.button("결과 다시 생성하기")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# --- 하단 정보 ---
st.caption("Created by Juhyeong Lee | Gemini API Chaining Workflow")
