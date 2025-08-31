# Input array elements
arr = []
for i in range(5):
    ele = int(input(f"Input element {i+1}: "))
    arr.append(ele)

# Input key to search
key = int(input("Enter key to search: "))

# Linear search
found_index = -1
for i in range(len(arr)):
    if arr[i] == key:
        found_index = i
        break

# Output results
print("Array:", arr)
if found_index != -1:
    print(f"Key found at index {found_index}")
else:
    print("Key not found")