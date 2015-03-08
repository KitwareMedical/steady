import sys

f = open(sys.argv[1], 'r')
content = f.readlines()

f = open(sys.argv[2], 'w')
f.write('helloworld\n')
