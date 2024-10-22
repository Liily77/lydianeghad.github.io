#Student's Notes Sam

student_name = "Sam"
math_grade = 88
science_grade = 75
english_grade = 90
geology_grade = 69

#Calculation of all grades

total_grade = math_grade + science_grade + english_grade + geology_grade

#The maximum score to validate

max_grade = 400

#Percentage of total grades

total_percentage = total_grade / max_grade * 100

print(f"Sam's total percentage is {total_percentage}%")

total_percentage = int(total_percentage)

#Condition to validate the diploma

did_student_pass = total_percentage >= 50

#Sam's rating of his sporting activity

sporting_activities = bool(0)
print(f"Sam participated in sporting activities: {sporting_activities}")

#Printing the total percentage reached by Sam if he succeeded or not

print(f"Sam's total percentage as an integer is {total_percentage}%")
print(f"Sam passed to the next semester: {did_student_pass}")