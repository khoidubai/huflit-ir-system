import os
from pathlib import Path
from .prompt_templates import RAG_PROMPT_TEMPLATE

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class AnswerGenerator:
    """
    Takes the built context and query to generate an answer using a local GGUF model via llama.cpp.
    By default, it uses the models/Qwen2.5-7B-Instruct-Q4_K_M.gguf file.
    """
    def __init__(self, use_llm=False):
        self.use_llm = use_llm
        self.model_path = os.getenv("LLM_MODEL", "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
        self.llm = None
        
        if self.use_llm:
            if Llama is None:
                print("Warning: llama-cpp-python not found. Please run `pip install llama-cpp-python`.")
                self.use_llm = False
            elif not os.path.exists(self.model_path):
                print(f"Warning: Local model not found at {self.model_path}. Please download it.")
                self.use_llm = False
            else:
                print(f"Đang nạp model LLM từ: {self.model_path}")
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=4096, # 4K Context window cho RAG
                    n_gpu_layers=-1, # Dùng card đồ hoạ nếu có
                    verbose=False # Tắt log quá trình chạy
                )

    def generate(self, query: str, context: str) -> str:
        """
        Generate answer based on context and query using local llama.cpp
        """
        if not self.use_llm or not self.llm:
            return self._fallback_answer()
            
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)
        
        # Format theo ChatML của Qwen Instruct
        formatted_prompt = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            response = self.llm(
                formatted_prompt,
                max_tokens=1024,
                temperature=0.1,
                stop=["<|im_end|>"],
                echo=False
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Error generating answer with local LLM (llama.cpp): {e}")
            return self._fallback_answer()
            
    def _fallback_answer(self):
        return "Xin lỗi, hiện tại tính năng Tư Vấn Viên AI đang bảo trì do chưa load được LLM Local. Bạn vui lòng xem các link gợi ý bên dưới nhé!"
