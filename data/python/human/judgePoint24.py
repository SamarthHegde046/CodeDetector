class Solution:
    def judgePoint24(self, cards: List[int]) -> bool:
        def dfs(nums):
            if len(nums)==1:
                return abs(nums[0]-24)<1e-6
            
            for i in range(len(nums)):
                for j in range(len(nums)):
                    if i!=j:
                        next=[nums[k] for k in range(len(nums)) if k!=i and k!=j]
                        for val in {nums[i]+nums[j],
                            nums[i]-nums[j],
                            nums[j]-nums[i],
                            nums[i]*nums[j]}:
                            if dfs(next+[val]):
                                return True
                        if nums[j]!=0 and dfs(next+[nums[i]/nums[j]]):
                            return True
                        if nums[i]!=0 and dfs(next+[nums[j]/nums[i]]):
                            return True
            return False
        return dfs(cards)