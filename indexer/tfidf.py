import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse

def build_tfidf(corpus_tokens, vocab_path, matrix_path):
    """
    corpus_tokens: list of list of tokens [['t1', 't2'], ...]
    vocab_path: path to save vocab mapping
    matrix_path: path to save sparse matrix (.npz)
    """
    # Vì dữ liệu đầu vào đã được tokenize, ta dùng analyzer='identity' hoặc join thành chuỗi
    # Ở đây join lại bằng khoảng trắng để TfidfVectorizer xử lý dễ hơn
    corpus_strings = [" ".join(tokens) for tokens in corpus_tokens]
    
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2), # Hỗ trợ bigram như README yêu cầu
        sublinear_tf=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus_strings)
    
    # Lưu vocab: term -> index
    vocab = vectorizer.vocabulary_
    # Chuyển index sang kiểu int của python để serialize được JSON
    vocab = {k: int(v) for k, v in vocab.items()}
    
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
        
    # Lưu ma trận sparse
    sparse.save_npz(matrix_path, tfidf_matrix)
    
    return tfidf_matrix, vocab

def load_tfidf(vocab_path, matrix_path):
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    matrix = sparse.load_npz(matrix_path)
    return vocab, matrix
