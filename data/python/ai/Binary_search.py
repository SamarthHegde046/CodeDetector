class MyClass:
    @staticmethod
    def binary_search():
        arr = []
        for i in range(5):
            ele = int(input("Input element: "))
            arr.append(ele)

        arr.sort()  # Binary search requires sorted array
        print("Sorted array:", arr)

        key = int(input("Key to search: "))
        left = 0
        right = len(arr) - 1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == key:
                return mid
            elif arr[mid] < key:
                left = mid + 1
            else:
                right = mid - 1

        return -1

# Run the search
result = MyClass.binary_search()
if result != -1:
    print("Key found at index", result)
else:
    print("Key not found")