#	********    @wardocardoso(.com)?	*********
# 	*********************************************
#	python script to deobfuscate php scripts that
#	use a seed to obfuscate the functions they use
#	*********************************************

import re

def prepare(fname):
	fullcontents = []
	try:
		with open(fname, 'r') as f:
			for ln in f.readlines():
				if len(f.readlines()) < 3:
					if ln == '<?php': continue #ignore first line if it is a php opening
					ln = re.sub(';', ';\n', ln).split('\n')
					fullcontents = ln
				else:
					fullcontents.append(n)
		f.close()
	except FileNotFoundError:
		print("File not found!")
	except IOError as err:
		print("I/O Error: {}".format(err))
	return fullcontents

# function getSeed()
# returns a string containing the seed used to deobfuscate the file

def getSeed(fcontents):
	return re.search('\'(.*)\'', fcontents[0]).group(0)[1:-1].replace("\\", '')

# function getMatches()
# returns every line that matches the pattern "$var[] ="
def getMatches(fcontents):
	base = []
	for line in fcontents:
		rmatch = re.findall('^\$[\w]{3,8}\[\] =.*', line.strip())
		if rmatch: base.append(rmatch)
	return base

# function reiterate()
# @arrVars is a list containing every word made with the seed
# @dicVars uses the arrVars list and returns a dictionary matching 
#every $var[num] with their respective word

def reiterate(base, seed):
	arrVars = []
	dicVars = {}
	for line in base:
		nameVar = re.match('^\$[\w]{3,8}\[\]', line[0]).group(0)
		reg = re.findall('\$[\w]{3,8}\[[\d]{1,2}\]', line[0])
		if reg:
			arrVars.append(''.join([seed[int(''.join([l for l in v if l.isdigit()]))] for v in reg]))
	for idx in range(len(arrVars)):
		dicVars[nameVar[:-2]+'['+str(idx)+']'] = arrVars[idx]
	return dicVars

def newfile(contents, dicVars):
	newFile = []
	if contents[0] != '<?php': contents.insert(0, '<?php')
	translatedSeed = ', '.join([v for v in dicVars.values()])
	for line in contents:
		for key, value in dicVars.items():
			match = re.findall('\$'+key[1:-3]+'\['+key[len(key)-2:-1]+'\]', line)
			if match:
				line = line.replace(match[0], value)
			else:
				match = re.match(re.escape(key[:-3])+'\[\]', line)
				if match: line = '{} = \'{}\';'.format(key[:-3], translatedSeed)
				continue
		if line not in newFile: newFile.append(line.rstrip())
	return newFile

def reformat(newf):
	reformatedFile = []
	newf[0] = re.sub('<\?php', '<?php\n', newf[0])
	for line in newf:
		line = re.sub(';', ';\n', line)
		line = re.sub('\}\}', '}\n}', line)
		line = re.sub('(\)| )\{', ') {\n', line)
		reformatedFile.append(line)
	return reformatedFile

def writeTo(fname, contents):
	try:
		with open(fname, 'w') as f:
			for line in contents:
				f.write(line)
		f.close()
	except FileExistsError:
		print("File already exists!")
	except IOError as err:
		print("I/O Error: {}".format(err))

if __name__	== "__main__":
	print("********************\n")
	phpfile = input("Input the php filename: ")
	print("*******************\n")
	if phpfile[len(phpfile)-4:] != '.php':
		exit("Not a php file, apparently")
	contents = prepare(phpfile)
	base = getMatches(contents)
	getDic = reiterate(base, getSeed(contents))
	reFile = newfile(contents, getDic)
	correctFile = reformat(reFile)
	if correctFile != []:
		newFile = input("Input the new filename: ")
		writeTo(newFile, correctFile)
	print("********************\n")
