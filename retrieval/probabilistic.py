""" 
Language Model với Dirichlet smoothing. Tính log P(query|doc) = Σ log[(tf(t,d) + μ·P(t|C)) / (|d| + μ)] với μ=2000. P(t|C) là xác suất term trong toàn corpus (collection LM). Tránh zero probability cho terms không xuất hiện trong doc.
"""
