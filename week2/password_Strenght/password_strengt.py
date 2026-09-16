LOWER=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
UPPER=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
DIGITS=["0","1","2","3","4","5","6","7","8","9"]
SPECIAL=["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "]", "{", "}", "|", ";", ":", "'", "\"", ",", ".", "<", ">", "?", "/", "\\","`", "~"]

def main ():
  user_password = input("Password check: ")
  word_complex = word_complexity(user_password)
  print(word_complex)

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

main()