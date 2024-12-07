import string

n = "fucd you bit, you mf fd you"
p = n.split(maxsplit=-1)

for i in p:
    if i == "you":
        print(i)