from google.generative_ai import ChatGoogleGenerativeAI

class LegalSimulation:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI("gemini-1.5-pro")

    def simulate_case(self, case_details):
        response = self.model.generate_text(case_details)
        return response['text']