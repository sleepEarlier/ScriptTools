#!/usr/bin python
# _*_ coding:utf-8 _*_
'''
Check that whether the ADHoc Provisioning profile include the specified UDID
param1, floder path which contain profiles
param2, target UDIDs, seperate mutilple by comma e.g. "UDID1,UDID2"
'''
import sys,os,subprocess,plistlib

def execute_cmd(cmd):
	process = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	process.wait()
	if process.stderr:
		raise Exception(process.stderr)

	lines = process.stdout.readlines()
	feedback = ''
	for line in lines:
		if not isinstance(line, str):
			line = str(line)
		feedback += line
	return feedback

		
def __checkProfileMatchParam(self, isDevelopment, isADHocProfile, isInHouse, profileInfo):
	logTool.getLogger().info('Checking Profile with PHP Params...')
	if isDevelopment:
		# Development 描述文件的get-task-allow = YES
		if profileInfo.get('Entitlements').get('get-task-allow') != True:
			print profileInfo
			logTool.getLogger().critical('Expect a Development profile, profile info:%s' % str(profileInfo))
			raise PackException(pack_exception.PROFILE_DISMATCH_PARAMS, 'Profile at \"%s\" was not a Development Profile' % self.profilePath)
	else:
		if isADHocProfile:
			notDevelopment = profileInfo.get('Entitlements').get('get-task-allow') != True
			notDistribution = profileInfo.get('Entitlements').get('beta-reports-active') != True
			if not (notDevelopment and notDistribution):
				raise PackException(pack_exception.PROFILE_DISMATCH_PARAMS, 'Profile at \"%s\" was not a ADHoc profile' % self.profilePath)
		else:
			# App store描述文件必须含有 beta-reports-active = YES
			if profileInfo.get('Entitlements').get('beta-reports-active') != True and not isInHouse:
				raise PackException(pack_exception.PROFILE_DISMATCH_PARAMS, 'Profile at \"%s\" was not a Distribution Profile' % self.profilePath)

			if isInHouse and profileInfo.get('ProvisionsAllDevices') != True:
				logTool.getLogger().critical('Expect a Enterprice Distribution profile, profile info:%s' % str(profileInfo))
				raise PackException(pack_exception.PROFILE_DISMATCH_PARAMS, 'Profile at \"%s\" was not a Enterprice Distribution Profile' % self.profilePath)
	logTool.getLogger().info('Result: Profile match PHP param')

def getProfileInfo(profilePath):
		'''
		@brief 获取描述文件中的信息：使用security命令将profile中的cms信息转为plist
		'''
		dir_path = os.path.dirname(profilePath)
		plistPath = os.path.join(dir_path,'result.plist')
		cmd = 'security cms -D -i %s > %s' %(profilePath, plistPath)
		feedback = execute_cmd(cmd)
		if not os.path.exists(plistPath):
			print('Generate plist from profile:\'%s\' fail' % os.path.basename(profilePath))
			print(feedback)
			return None
		else:
			try:
				resultPlist = plistlib.readPlist(plistPath)
				os.remove(plistPath)
				return resultPlist
			except :
				if os.path.exists(plistPath):
					os.remove(plistPath)
				raise


def checkUDID(floder, targetUDIDS):
	# ProvisionedDevices
	if not os.path.exists(floder) or not os.path.isdir(floder):
		raise Exception('%s not exists' % floder)

	fileNames = os.listdir(floder)
	fileNames = filter(lambda s: s.endswith('_ADHOC.mobileprovision'), fileNames)
	invalid_results = []
	for file in fileNames:
		filePath = os.path.join(floder, file)
		info = getProfileInfo(filePath)
		containedDevices = info.get('ProvisionedDevices')
		if not containedDevices:
			invalid_results.append({file:targetUDIDS})
		else:
			exclude_targets = []
			for one_udis in targetUDIDS:
				if not one_udis in containedDevices:
					exclude_targets.append(one_udis)
			if len(exclude_targets) > 0:
				invalid_results.append({file:exclude_targets})

	if len(invalid_results) > 0:
		print('*** Invalid Profiles:%s ***' % len(invalid_results))

		for d in invalid_results:
			for item in d.items():
				print("%s : %s" % item)
	else:
		print('*** All ADHOC Profile Include target UDIDs ***')





if __name__ == '__main__':
	# For BY Use
	# Check that whether the ADHoc Provisioning profile include the specified UDID
	try:
		floder = sys.argv[1]
		udids = sys.argv[2]
	except Exception as e:
		print('This script needs two arguments:\n1.directory thar contain mobileprovision files\n2.target UDID to check, seperate mutible UDID by \',\'')
	else:
		targetUDIDS = filter(lambda s: s.strip(), udids.split(','))
		if len(targetUDIDS):
			checkUDID(floder, targetUDIDS)
		else:
			print('No UDID to check')


	

