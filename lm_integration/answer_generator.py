""" 
Nhận context + query gốc → gọi LLM (Gemini API hoặc model local) để sinh câu trả lời tiếng Việt mượt. Thêm source links vào cuối câu trả lời. Fallback: nếu LLM không available thì trả về snippet của top-1 result.
"""
