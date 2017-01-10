#!/usr/bin/env python
# _*_ coding:utf-8 _*_

'''
created on 2016-12-28
@author: kimilin
'''

import subprocess, tempfile, os, sys

def __handle_error_lines(process, cmd, inlistformate = False):
	'''
	@brief 处理命令行输出
	'''
	if not process:
		return None
	lines = process.stderr.readlines() if process.stderr else None
	if lines:
		feedback = ''
		for s in lines:
			feedback += s
		raise Exception('Execute cmd Error: %s' % cmd)
	else:
		lines = process.stdout.readlines()
		if inlistformate:
			lines = map(lambda s: s.strip(), lines) # delete '\n'
			lines = filter(lambda s: s, lines)
			return lines # filter empty
		else:
			feedback = ''
			for line in lines:
				if not isinstance(line, str):
					try:
						line = str(line)
					except :
						raise Exception('feedback line can not convert to str')
				feedback += line
			return feedback

def execute_cmd(cmd, getfeedback = True, inlistformate = False):
	'''
	@brief 执行普通的命令行指令
	@param cmd: 命令
	@param getfeedback 是否返回输出
	@param inlistformate False输出以str类型返回，True输出以list类型返回
	'''
	process = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	process.wait()
	feedback = __handle_error_lines(process, cmd, inlistformate)
	return feedback if getfeedback else process


def findPPWithoutAPNS(ppfloder):
	print '===== Begin ====='
	result = []
	for file in os.listdir(ppfloder):
		if file.endswith('.mobileprovision'):# and (not 'APPID' in file):
			cmd = 'security cms -D -i %s' % os.path.join(ppfloder,file)
			feedback = execute_cmd(cmd)
			if not 'aps-environment' in feedback:
				result.append(file)
	if len(result) > 0:
		for file in result:
			print file
	else:
		print 'All PPFile Contain APNS'
	print '===== Finish ====='
	

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	try:
		path = sys.argv[1]
	except Exception, e:
		print 'Please offer an floderPath contain PPFiles.'
		raise e
	else:
		findPPWithoutAPNS(path)



