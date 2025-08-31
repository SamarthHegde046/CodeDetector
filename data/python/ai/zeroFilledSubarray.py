def zero_filled_subarrays(nums):
    total = 0
    zeros = 0
    
    for num in nums:
        if num == 0:
            zeros += 1
            total += zeros   # add contribution directly
        else:
            zeros = 0
    
    return total

# Example
nums = [1,3,0,0,2,0,0,4]
print(zero_filled_subarrays(nums))  # Output: 6
