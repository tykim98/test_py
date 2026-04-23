import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

"""
Legal Battle Simulator: Australian AgTech Dispute
--------------------------------------------------
- Engine: Google Gemini 1.5 Pro
- API Key: Applied (AIzaSyDDX9iV7BVCQUezJMY28htBxU_sv4TZ5ZE)
- Knowledge Path: ./knowledge/
- Logic: Sequential Multi-Agent Simulation
"""

# 1. 에이전트별 페르소나 및 스크립트 (배열 자료구조)
AGENT_SCRIPTS: Dict[str, List[str]] = {
    "plaintiff": [
        "너는 호주 건설법에 능통한 공격적인 원고측 변호사(Earthfix 대변)다.",
        "이수화학(피고)에게 미지급 대금 AUD 370,000 및 이자를 청구하는 것이 목표다.",
        "현장 공사가 완료되었음을 입증하는 인보이스와 사진 증거를 강조하라.",
        "상대의 '시스템 결함' 주장은 근거 없는 책임 회피이며, 피고의 운영 미숙임을 주장하라."
    ],
    "defendant": [
        "너는 이수화학의 입장을 대변하는 냉철하고 전략적인 피고측 변호사다.",
        "MGS 시스템의 기술적 하자와 원고의 QBCC 라이선스 미보유를 근거로 대금 지급 의무가 없음을 주장하라.",
        "원고의 기술적 준비 부족으로 인한 프로젝트 지연 및 손실을 상계 처리할 것을 요구하라.",
        "호주 현지 법규 미준수(라이선스)가 계약의 효력에 미치는 치명적 결함을 파고들어라."
    ],
    "judge": [
        "너는 호주 건설법과 한국 민법에 능통한 중립적이고 권위 있는 판사다.",
        "양측의 주장과 ./knowledge/ 폴더에서 로드된 증거 자료를 법리적으로 검토하라.",
        "판결 시 [승소 확률(%)], [법적 근거], [양측이 보완해야 할 증거]를 명확히 포함하여 선고하라."
    ]
}

class LegalSimulation:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        # 제공해주신 API 키를 환경 변수에 즉시 적용합니다.
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDDX9iV7BVCQUezJMY28htBxU_sv4TZ5ZE"
        
        # Gemini 1.5 Pro 모델 설정
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0.2, # 법률적 추론을 위해 낮은 온도(일관성) 유지
            max_output_tokens=2048,
            top_p=0.9
        )
        self.history: List[HumanMessage] = []

    def _load_agent_knowledge(self, agent_name: str) -> str:
        """./knowledge/ 폴더 내 에이전트별 배경지식 파일을 로드합니다."""
        file_path = f"./knowledge/{agent_name}_data.txt"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    return f"\n--- {agent_name.upper()} DATA START ---\n{content}\n--- DATA END ---\n"
            else:
                return f"\n(알림: {agent_name}에 대한 개별 증거 파일이 없습니다. 공통 지식으로 진행합니다.)\n"
        except Exception as e:
            return f"파일 로드 오류: {str(e)}"

    def run_simulation_turn(self, role: str):
        """특정 에이전트의 차례를 수행합니다."""
        # 페르소나와 배경지식 결합
        persona_context = " ".join(AGENT_SCRIPTS[role])
        knowledge = self._load_agent_knowledge(role)
        
        # 제미나이 전용 시스템 인스트럭션 구성
        instruction = f"""
        [YOUR ROLE]
        {persona_context}
        
        [EVIDENCE & KNOWLEDGE]
        {knowledge}
        
        [INSTRUCTIONS]
        - 당신은 실제 재판에 임하는 변호사 또는 판사입니다.
        - 반드시 제공된 'EVIDENCE & KNOWLEDGE'와 이전 대화 기록을 바탕으로 논리를 전개하세요.
        - 사실 관계가 불분명한 경우 상대에게 입증 책임을 물으세요.
        - 전문적이고 단호한 법률 용어를 사용하세요.
        """
        
        # 메시지 구성: 지침 + 대화 이력
        messages = [SystemMessage(content=instruction)] + self.history
        
        # 호출 및 결과 처리
        response = self.llm.invoke(messages)
        
        # 히스토리에 기록 (전체 맥락 유지를 위함)
        formatted_turn = f"[{role.upper()}]: {response.content}"
        self.history.append(HumanMessage(content=formatted_turn))
        
        return formatted_turn

# --- 실행 메인 루프 ---
if __name__ == "__main__":
    # 1. 지식 저장용 폴더 자동 생성 확인
    if not os.path.exists("./knowledge"):
        os.makedirs("./knowledge")
        # 테스트용 빈 파일 생성 (파일이 없을 경우 대비)
        for agent in ["plaintiff", "defendant", "judge"]:
            open(f"./knowledge/{agent}_data.txt", 'a').close()

    sim = LegalSimulation()

    print("\n" + "⚖️ " * 20)
    print("  디지털 모의재판 시뮬레이션: 호주 스마트팜 분쟁  ")
    print("⚖️ " * 20 + "\n")

    # 2. 재판 진행 (원고 -> 피고 -> 판사)
    steps = [
        ("plaintiff", "원고(Earthfix) 측 소장 진술"),
        ("defendant", "피고(이수화학) 측 답변 및 반박"),
        ("judge", "판사 최종 법리 검토 및 판결 선고")
    ]

    for role, description in steps:
        print(f"\n[{description}]")
        print("-" * 60)
        output = sim.run_simulation_turn(role)
        print(output)
        print("-" * 60)

    print("\n[재판 종료] 모든 공방 및 판결이 완료되었습니다.")
