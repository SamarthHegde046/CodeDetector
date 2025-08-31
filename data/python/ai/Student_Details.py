# Student Marks Calculation Program

# Input student details
name = input("Enter the name: ")
usn = input("Enter the USN: ")

# Input marks
print("Enter marks for 3 subjects:")
marks = []
for i in range(1, 4):
    mark = int(input(f"Subject {i}: "))
    marks.append(mark)

# Calculations
total = sum(marks)
percentage = total / len(marks)

# Output
print("\n--- Student Report ---")
print("Name        :", name)
print("USN         :", usn)
print("Total Marks :", total)
print("Percentage  :", round(percentage, 2))
