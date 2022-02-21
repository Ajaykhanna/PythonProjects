# Title: Combining Assembly Language Powered PyTorch MatMul with Strassen MatMul Method
# Author: Ajay Khanna |Git: Ajaykhanna|Twitter: @samdig| LinkedIn: ajay-khanna|
# Date: Feb.20.2020
# Place: UC Merced
# Lab: Dr. Isborn
# Architecture: Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz/32.0GB
# OS: Windows 11 21H2
# Python: 3.9.7
#------------------------------------------------------
# Importing Time & PyTorch
import time
import torch
import numpy as np
#------------------------------------------------------
#
# Method #1: Using Pure Python
# Matrix Multiplication in Pure Python but with PyTorch
# Function for Matrix Multiplication
def matmul(a,b):
    a_rows, a_cols = a.shape
    b_rows, b_cols = b.shape
    assert a_cols == b_rows
    c = torch.zeros(a_rows, b_cols)    
    # For loop for Element-wise Operation
    # 
    for i in range(a_rows):
        for j in range(b_cols):
            for k in range(a_cols):
                c[i, j] += a[i, k] * b[k, j]
    return c
#------------------------------------------------------
#
def matmul_pytorch(a, b):
    c = a.matmul(b)
    return c
#------------------------------------------------------ 
#
# Building Strassen Algorithm
# Currently Applicable to Only Square Matrices
# With Total Matrix Elements = 2^n, n >=1
# To Apply This Method to Non-Square Pad Each
# Row and Column with Zeros and Convert them
# to Square Martices

# Split Square Matrix into Even Number of Sub-Square Matrices
def split(matrix):
    n = len(matrix)
    return matrix[:n//2, :n//2], matrix[:n//2, n//2:], matrix[n//2:, :n//2], matrix[n//2:, n//2:]
#------------------------------------------------------
#   
# Stressen Alogrithm with Standard Matrix Multiplication Method
def standard_stressen(A, B):
    if len(A) <= 2:
        return matmul(A, B)
    a, b, c, d = split(A)
    e, f, g, h = split(B)
    p1 = standard_stressen(a+d, e+h)
    p2 = standard_stressen(d, g-e)
    p3 = standard_stressen(a+b, h)
    p4 = standard_stressen(b-d, g+h)
    p5 = standard_stressen(a, f-h)
    p6 = standard_stressen(c+d, e)
    p7 = standard_stressen(a-c, e+f)
    C11 = p1 + p2 - p3 + p4
    C12 = p5 + p3
    C21 = p6 + p2
    C22 = p5 + p1 - p6 - p7
    C = np.vstack((np.hstack((C11, C12)), np.hstack((C21, C22))))
    return C
#------------------------------------------------------  
#
# Pytorched Strassen Algorithm
def pytorched_strassen(A, B):
    if len(A) <= 2:
        return matmul_pytorch(A, B)   
    a, b, c, d = split(A)
    e, f, g, h = split(B)
    p1 = pytorched_strassen(a+d, e+h)
    p2 = pytorched_strassen(d, g-e)
    p3 = pytorched_strassen(a+b, h)
    p4 = pytorched_strassen(b-d, g+h)
    p5 = pytorched_strassen(a, f-h)
    p6 = pytorched_strassen(c+d, e)
    p7 = pytorched_strassen(a-c, e+f)
    C11 = p1 + p2 - p3 + p4
    C12 = p5 + p3
    C21 = p6 + p2
    C22 = p5 + p1 - p6 - p7
    C = np.vstack((np.hstack((C11, C12)), np.hstack((C21, C22))))
    return C
#------------------------------------------------------  
#
# Generating Random Matrix    
# Matrix Elements should be = 2^n, n >= 1
n = 10 # Power: To Create Matrix Elements
a_matrix = torch.rand(2**n,  2**n)
b_matrix = torch.rand(2**n,  2**n)
#
# Printing the Result of Random Matrix Multiplication
tic = time.perf_counter()
print('Matrix Multiplication with Standard Method: \n',
       matmul(a_matrix, b_matrix), '\n')
toc = time.perf_counter()
print(f"Standard Method Took {toc - tic:0.4e} seconds")
#
tic = time.perf_counter()
print('Matrix Multiplication with Standard Strassen Method: \n',
       standard_stressen(a_matrix, b_matrix), '\n')
toc = time.perf_counter()
print(f"Standard Stressen Method Took {toc - tic:0.4e} seconds")
#
tic = time.perf_counter()
print('Matrix Multiplication with PyTorced Strassen Method \n',
       pytorched_strassen(a_matrix, b_matrix), '\n')
toc = time.perf_counter()
print(f"PyTorched Stressen Method took {toc - tic:0.4e} seconds")

tic = time.perf_counter()
print('Matrix Multiplication with PyTorced MatMul Method \n',
       matmul_pytorch(a_matrix, b_matrix), '\n')
toc = time.perf_counter()
print(f"PyTorch MatMul Method took {toc - tic:0.4e} seconds")
#------------------------------------------------------   
# Results
# Method #1: Standard Method took:               301.77 seconds
# Method #2: Standard Method with Stressen took: 151.33 seconds
# Method #3: PyTorched Stressen Method took:      21.222 seconds
# Method #4: PyTorched MatMul Method took:      

# Conclusion