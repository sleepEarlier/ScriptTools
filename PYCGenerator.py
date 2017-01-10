#!/usr/bin/env python
# _*_ coding:utf-8 _*_

'''
created on 2016-12-28
@author: kimilin
'''

import os, sys
import py_compile
import subprocess

def execute_cmd(cmd, getfeedback = False, inlistformate = False):
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
		path = sys.argv[1]
	except Exception, e:
		print('此脚本需要输入文件或文件夹路径')
	else:
		if os.path.exists(path):
			if os.path.isfile(path):
				if path.endswith('.py'):
					py_compile.compile(path)
			else:
				import compileall
				compileall.compile_dir(path)
		else:
			print('%s不存在' % os.path.basename(path))

