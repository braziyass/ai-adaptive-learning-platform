# Users

id

first_name

last_name

email

password

role

created_at

updated_at

-----------------------------------

# Student

id

user_id

current_level

placement_score

-----------------------------------

# Teacher

id

user_id

-----------------------------------

# Course

id

title

subject

-----------------------------------

# Chapter

id

course_id

title

order

-----------------------------------

# Lesson

id

chapter_id

title

content

-----------------------------------

# Quiz

id

lesson_id

-----------------------------------

# Question

id

quiz_id

question

type

-----------------------------------

# StudentProgress

student_id

lesson_id

completed

score

attempts