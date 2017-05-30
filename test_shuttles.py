import string
alpha = list(string.ascii_lowercase)
code = "pc/def/map.html"
de_code = ""

for letter in code:
	try:
		de_code += alpha[(alpha.index(letter)+2)%26]
	except ValueError:
		de_code += "/"

print(de_code)
