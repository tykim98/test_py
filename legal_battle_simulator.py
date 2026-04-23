import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

"""
Legal Battle Simulator: Australian AgTech Dispute
--------------------------------------------------
Purpose: 
- Simulate a 3-party legal debate (Plaintiff, Defendant, Judge).
- Use local knowledge files for evidence-based arguments.
- Maintain a structured persona system via AGENT_SCRIPTS.

Architecture:
- RAG-ready: Knowledge is loaded per-agent from the ./knowledge/ folder.
- State Management: Conversation history is passed to maintain context.
- Extensibility: Designed to transition from flat-file loading to Vector DB.
"""

# 1. 에이전트별 페르소나 및 스크립트 자료구조 (배열 기반)
AGENT_SCRIPTS: Dict[str, List[str]] = {
    "plaintiff": [
        "너는 호주 건설법에 능통한 공격적인 원고측 변호사(Earthfix 대변)다.",
        "이수화학(피고)에게 미지급 대금 AUD 370,000을 받아내는 것이 주된 목적이다.",
        "제시된 증거 자료에서 피고의 과실(관리 부실 등)을 찾아내어 강력하게 압박하라.",
        "상대방이 '시스템 결함'을 주장할 경우, 이를 '운영 미숙'이나 '현장 관리 태만'으로 반박하라."
    ],
    "defendant": [
        "너는 이수화학의 입장을 대변하는 냉철하고 전략적인 피고측 변호사다.",
        "MGS 시스템의 기술적 결함과 원고의 QBCC 라이선스 미보유를 근거로 대금 지급 의무가 없음을 주장하라.",
        "논리적 허점을 파고들어 면책 사유를 증명하고, 필요 시 손해배상 상계를 주장하라.",
        "기술적 전문 용어를 활용하여 결함의 인과관계를 명확히 설명하라."
    ],
    "judge": [
        "너는 호주 건설법과 한국 민법에 모두 능통한 중립적이고 권위 있는 판사다.",
        "양측이 제시한 증거와 변론의 신빙성을 법리적으로 검토하여 최종 선고를 내린다.",
        "판결 시 승소 확률(%)과 근거 법령, 그리고 각 측의 핵심 리스크를 명확히 명시하라."
    ]
}

class LegalSimulation:
    def __init__(self, model_name: str = "gpt-4o"):
        # OpenAI API 키가 환경 변수에 설정되어 있어야 합니다.
        self.llm = ChatOpenAI(model=model_name, temperature=0.2)
        self.history: List[HumanMessage] = []

    def _load_agent_knowledge(self, agent_name: str) -> str:
        """지정된 폴더 하위에서 에이전트별 배경지식 파일을 읽어옵니다."""
        file_path = f"./knowledge/{agent_name}_data.txt"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return f"알림: {agent_name}에 대한 추가 배경지식 파일이 존재하지 않습니다."
        except Exception as e:
            return f"파일 로드 중 오류 발생: {str(e)}"

    def run_simulation_turn(self, role: str):
        """특정 역할의 에이전트가 변론을 수행합니다."""
        # 1. 페르소나(스크립트) 및 배경지식 로드
        persona_context = " ".join(AGENT_SCRIPTS[role])
        background_knowledge = self._load_agent_knowledge(role)
        
        # 2. 시스템 프롬프트 구성 (Persona + Knowledge)
        system_instruction = f"""
        {persona_context}
        
        [참조 배경지식 자료]
        {background_knowledge}
        
        [지시사항]
        - 반드시 제공된 배경지식 자료에 근거하여 발언하라.
        - 이전 대화 기록을 검토하여 상대의 주장을 반박하거나 논리를 보강하라.
        - 법률적인 톤앤매너를 유지하라.
        """
        
        # 3. LLM 호출 (시스템 메시지 + 대화 이력)
        messages = [SystemMessage(content=system_instruction)] + self.history
        response = self.llm.invoke(messages)
        
        # 4. 결과 기록 및 반환
        self.history.append(HumanMessage(content=f"[{role.upper()} 변론]: {response.content}"))
        return response.content

# --- 실행부 ---
if __name__ == "__main__":
    # 환경 세팅 확인 (knowledge 폴더가 없으면 생성)
    if not os.path.exists("./knowledge"):
        os.makedirs("./knowledge")
        print("알림: './knowledge' 폴더가 생성되었습니다. 각 에이전트용 .txt 파일을 넣어주세요.")

    sim = LegalSimulation()

    # 시뮬레이션 순서: 원고 공격 -> 피고 방어 -> 판사 선고
    print("\n" + "="*50)
    print("STEP 1: 원고(Earthfix 측)의 소장 제출 및 공격")
    print("-" * 50)
    print(sim.run_simulation_turn("plaintiff"))

    print("\n" + "="*50)
    print("STEP 2: 피고(이수화학 측)의 답변 및 반박")
    print("-" * 50)
    print(sim.run_simulation_turn("defendant"))

    print("\n" + "="*50)
    print("STEP 3: 판사의 최종 검토 및 판결")
    print("-" * 50)
    print(sim.run_simulation_turn("judge"))
    print("="*50 + "\n")
