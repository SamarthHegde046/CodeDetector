class Solution:
    def judgePoint24(cards):
        def dfs(nums):
            if len(nums) == 1:
                return abs(nums[0] - 24) < 1e-6

            # try all pairs of numbers
            for i in range(len(nums)):
                for j in range(len(nums)):
                    if i != j:
                        # pick nums[i] and nums[j]
                        next_nums = [nums[k] for k in range(len(nums)) if k != i and k != j]
                        
                        # possible results from combining nums[i], nums[j]
                        for val in {nums[i] + nums[j],
                                    nums[i] - nums[j],
                                    nums[j] - nums[i],
                                    nums[i] * nums[j]}:
                            if dfs(next_nums + [val]):
                                return True
                        # division (avoid divide by zero)
                        if nums[j] != 0 and dfs(next_nums + [nums[i] / nums[j]]):
                            return True
                        if nums[i] != 0 and dfs(next_nums + [nums[j] / nums[i]]):
                            return True
            return False
        
        return dfs(cards)
