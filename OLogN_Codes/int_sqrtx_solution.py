def OLogN_SQRT(x: int) -> int:
	L, R = 1, x
	
	while L <= R:
		M = (L + R) // 2
		M_SQRD = M * M
		
		if M_SQRD == x:
			return M
		elif M_SQRD < x:
			L = M + 1
		else:
			R = M - 1
	return R


if __name__ == "__main__":
	x = int(input("Enter a number: "))
	print(f"The square root of {x} is: {OLogN_SQRT(x)}")