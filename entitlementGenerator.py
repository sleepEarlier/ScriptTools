#!/usr/bin/python
# _*_ coding:utf-8 _*_

import sys
import os
import os.path as path
import subprocess
import plistlib

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
		logTool.getLogger().error(feedback)
		raise PackException(pack_exception.EXECUTE_CMD_ERROR, 'Execute cmd Error: %s' % cmd)
	else:
		lines = process.stdout.readlines()
		__clearProcess(process)
		if inlistformate:
			lines = map(lambda s: s.strip(), lines) # delete '\n'
			return EasyHelp.Easy_filter_empty(lines) # filter empty
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

def __clearProcess(process):
	'''
	@brief 清理process
	'''
	if process.stdin:
		process.stdin.close()
	if process.stdout:
	    process.stdout.close()
	if process.stderr:
	    process.stderr.close()
	try:
		process.kill()
	except OSError:
	    pass

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	try:
		filePath = sys.argv[1]
	except Exception as e:
		print('This script needs a argument')
	else:
		print('\n*** Begin Generating ***')
		print('* Decoding Profile...')
		tempPath = path.join(path.dirname(__file__), 'temp_decode_result.plist')
		cmd = 'security cms -D -i %s > %s' % (filePath, tempPath)
		feedback = execute_cmd(cmd)
		try:
			tempPlist = plistlib.readPlist(tempPath)
		except Exception as e:
			if path.exists(tempPath):
				os.remove(tempPath)
			raise e
		print('* Generating result...')
		ent = tempPlist['Entitlements']

		seps = path.basename(filePath).split('.')
		seps.pop()
		resultName = '.'.join(seps)
		resultPath = path.join(path.dirname(filePath), resultName+'.plist')
		try:
			plistlib.writePlist(ent, resultPath)
		except Exception as e:
			if path.exists(tempPath):
				os.remove(tempPath)
			raise e
		print('* Result at:%s' % resultPath)
		if path.exists(tempPath):
			os.remove(tempPath)
		



