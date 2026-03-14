def build_context(top_results, max_tokens=1500):
    """
    Constructs a context string from the top search results to be fed into the LLM.
    Args:
        top_results: List of dictionaries representing the retrieved documents.
                     Expected keys: 'title', 'url', 'category', 'snippet'.
        max_tokens: Approximate limit to avoid exceeding LLM context windows.
    Returns:
        A formatted string containing the combined context.
    """
    if not top_results:
        return "Không tìm thấy tài liệu tham khảo nào."

    context_parts = []
    
    for i, res in enumerate(top_results):
        title = res.get('title', 'Không có tiêu đề')
        url = res.get('url', 'Không có link')
        category = res.get('category', 'Chung')
        snippet = res.get('snippet', '')
        
        doc_str = f"[Tài liệu {i+1}]\n"
        doc_str += f"Tiêu đề: {title}\n"
        doc_str += f"Chuyên mục: {category}\n"
        doc_str += f"Trích xuất nội dung: {snippet}...\n"
        doc_str += f"Nguồn: {url}\n"
        
        context_parts.append(doc_str)
        
    final_context = "\n---\n".join(context_parts)
    
    # Basic truncation to ensure we don't blow up the prompt size
    # Assuming ~4 chars per token on average for basic truncation guard
    max_chars = max_tokens * 4
    if len(final_context) > max_chars:
        final_context = final_context[:max_chars] + "\n...[Nội dung đã được cắt bớt do quá dài]"
        
    return final_context
