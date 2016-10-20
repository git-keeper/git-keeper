first_word = input('Enter a word: ')
second_word = input('Enter another word: ')

print(first_word)
print(second_word)
print(first_word.upper() + second_word.lower())
print(second_word * 3)
print(first_word[0] + second_word[-1])
print(first_word[:2] + second_word[:2])

for c in first_word:
    print(c, end=' ')

print()

