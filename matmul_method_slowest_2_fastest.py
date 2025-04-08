# Title: Matrix Multiplication From Slowest to the Faster CPU based Method
# Author: Ajay Khanna |Git: Ajaykhanna|Twitter: @samdig| LinkedIn: ajay-khanna|
# Date: Feb.20.2020
# Place: UC Merced
# Lab: Dr. Isborn
# Architecture: Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz/32.0GB
# OS: Windows 11 21H2
# Python: 3.9.7

# Importing Time & PyTorch
import time
import torch


# ------------------------------------------------------
# Method #1: Using Pure Python
# Matrix Multiplication in Pure Python but with PyTorch
# Function for Matrix Multiplication
def matmul(a, b):
    tic = time.perf_counter()
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
    toc = time.perf_counter()
    print(f"Method #1: Brute Force took {toc - tic:0.4e} seconds")
    return c


# ------------------------------------------------------
# Using PyTorch Elementwise Operation
# This operation allows one inner loop
# to be elemenated
# I think it is aka Reduction in OpenMP
# Method #2: Using PyTorch Element-wise operation Method
def matmul_reduction(a, b):
    tic = time.perf_counter()
    a_rows, a_cols = a.shape
    b_rows, b_cols = b.shape
    assert a_cols == b_rows
    c = torch.zeros(a_rows, b_cols)
    #
    for i in range(a_rows):
        for j in range(b_cols):
            # Using PyTorch Element-wise operation
            c[i, j] = (a[i, :] * b[:, j]).sum()
    toc = time.perf_counter()
    print(f"Method #2: Reduction method took {toc - tic:0.4e} seconds")
    return c


# ------------------------------------------------------
# Method #3: Using PyTorch Broadcast Method
# Elemenating Another Inner Loop
def matmul_broadcasting(a, b):
    tic = time.perf_counter()
    a_rows, a_cols = a.shape
    b_rows, b_cols = b.shape
    assert a_cols == b_rows
    c = torch.zeros(a_rows, b_cols)
    for i in range(a_rows):
        # Using PyTorch Element-wise operation
        c[i] = (a[i].unsqueeze(-1) * b).sum(dim=0)
    toc = time.perf_counter()
    print(f"Method #3: Broadcasting method took {toc - tic:0.4e} seconds")
    return c


# ------------------------------------------------------
# Method #4: Using Einstein Method
def matmul_einstein(a, b):
    tic = time.perf_counter()
    c = torch.einsum("ik,kj->ij", a, b)
    toc = time.perf_counter()
    print(f"Method #4: Einstein method took {toc - tic:0.4e} seconds")
    return c


# ------------------------------------------------------
# Method #5: PyTorch MatMul Boosted by Assembly Language
def matmul_pytorch(a, b):
    tic = time.perf_counter()
    c = a.matmul(b)
    toc = time.perf_counter()
    print(f"Method #5: PyTorch method took {toc - tic:0.4e} seconds")
    return c


# ------------------------------------------------------
# Generating Random Matrix
a_matrix = torch.rand(100, 100)
b_matrix = torch.rand(100, 100)
#
# Printing the Result of Random Matrix Multiplication
print(
    "Method #1: Matrix Multiplication in Pure Python: \n",
    matmul(a_matrix, b_matrix),
    "\n",
)
print(
    "Method #2: Using PyTorch Element-wise operation Method: \n",
    matmul_reduction(a_matrix, b_matrix),
    "\n",
)
print(
    "Method #3: Using PyTorch Broadcast Method: \n",
    matmul_broadcasting(a_matrix, b_matrix),
    "\n",
)
print("Method #4: Using Einstein Method: \n", matmul_einstein(a_matrix, b_matrix), "\n")
print(
    "Method #5: PyTorch MatMul Boosted by Assembly Language: \n",
    matmul_pytorch(a_matrix, b_matrix),
    "\n",
)
# ------------------------------------------------------
# Results
# Method #1: Brute Force took 2.2534e+01 seconds
# Method #2: Reduction method took 2.7637e-01 seconds
# Method #3: Broadcasting method took 3.6313e-03 seconds
# Method #4: Einstein method took 1.5798e-03 seconds
# Method #5: PyTorch method took 1.7720e-04 seconds

# Inspired by this article: "https://towardsdatascience.com/matrix-multiplication-the-pytorch-way-c0ad724402ed"
