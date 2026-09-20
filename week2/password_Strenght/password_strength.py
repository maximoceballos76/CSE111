from turtle import st


LOWER=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
UPPER=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
DIGITS=["0","1","2","3","4","5","6","7","8","9"]
SPECIAL=["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "]", "{", "}", "|", ";", ":", "'", "\"", ",", ".", "<", ">", "?", "/", "\\","`", "~"]

def main ():
  user_password = input("Password check: ")
  while user_password.lower() != "q":
    user_password = input("Password check: ")
    if user_password.lower() == "q":
      break
    strength = password_strength(user_password)
    print(f"Password strength score: {strength}")

def word_complexity (word):
  has_lower = word_has_character(word, LOWER)
  has_upper = word_has_character(word, UPPER)
  has_digit = word_has_character(word, DIGITS)
  has_special = word_has_character(word, SPECIAL)
  total = sum([has_lower, has_upper, has_digit, has_special])
  return total


def word_has_character (word, character_list):
  has_character = False
  for character in word:
    if character in character_list:
      has_character = True
      break
  return has_character

def word_in_file(word, filename, case_sensitive = False):
  with open(filename, "r", encoding="utf-8") as file:
    for line in file:
      if case_sensitive:
        if word == line.strip():
          return True
      else:
        if word.lower() == line.strip().lower():
          return True
  return False

def password_strength(password, min_length = 10, strong_length = 16):

  check1 = word_in_file(password, "toppasswords.txt")
  check2 = word_in_file(password, "wordlist.txt")

  if check1 or check2:
    if check1:
      print("Password is in the top passwords list.")
    if check2:
      print("Password is in the word list.")
    return 0

  length = len(password)
  length_strength = 0

  if length < min_length:
    print("Password is too short.")
    return 0
  if length >= strong_length:
    length_strength = 1


  complexity = word_complexity(password)
  total_strength = length_strength + complexity
  return total_strength

main()
