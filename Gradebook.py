#List for organize my subjects and grades
last_semester_gradebook = [["politics", 80], ["latin", 96], ["dance", 97], ["architecture", 65]]

#My code below: 
gradebook = [["physics", 98], ["calculus", 97], ["poetry", 85], ["history", 88]]

#Add a list with new values
gradebook.append(["computer science", 100])
gradebook.append(["visual arts", 93])

#Rewarding an extra 5 points for our visual arts class
gradebook[5][1] += 5

#Switch from numerical grade value to a Pass/Fail option for my poetry class
gradebook[2].remove(gradebook[2][1])
gradebook[2].append("Pass")

#New variable to combine both lists
full_semester_gradebook = last_semester_gradebook + gradebook

print(full_semester_gradebook)