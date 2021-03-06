#!/usr/bin python
# _*_ coding:utf-8 _*_

import sys,os,subprocess,plistlib
import uuid
'''
List the floder profile's name \ appid \ team
'''
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

def createTempKeychain():
	'''
	创建临时keychian，成功则返回临时keychian路径
	'''
	tempKeychainName = str(uuid.uuid1()).replace('-','_').upper()
	tempKeychainPath = os.path.expanduser("~/Library/Keychains/%s" % tempKeychainName)
	tempKeychainPwd = '123'
	if os.path.exists(tempKeychainPath):
		deleteKeychain(tempKeychainPath)
	cmd = 'security create-keychain -p %s %s' % (tempKeychainPwd, tempKeychainPath)
	feedback = execute_cmd(cmd)
	if len(feedback) == 0:
		return tempKeychainPath
	else:
		print("Create temp keychain failed:%s" % feedback)
		raise Exception("Create temp keychain failed")

def deleteKeychain(path):
	cmd = 'security delete-keychain %s' % path
	feedback = execute_cmd(cmd)
	if len(feedback) == 0:
		pass
	else:
		print("Delete temp keychain failed:%s" % feedback)
		raise Exception("Delete temp keychain failed")

def getProfileInfo(profilePath):
		'''
		@brief 获取描述文件中的信息：使用security命令将profile中的cms信息转为plist
		'''
		# cmd = 'security cms -D -k %s -i %s' % (tempKeychainPath, profilePath)
		tempKeychainPath = createTempKeychain()

		cmd = 'security cms -D -k %s -i \"%s\"' % (tempKeychainPath, profilePath)
		feedback = execute_cmd(cmd)
		deleteKeychain(tempKeychainPath)
		rep = 'security: SecPolicySetValue: One or more parameters passed to a function were not valid.\n'
		if rep in feedback:
			feedback = feedback.replace(rep,'')

		try:
			resultPlist = plistlib.readPlistFromString(feedback)
			return resultPlist
		except Exception as e:
			print(feedback)
			print('Get Plist Exception:%s' % e)
			raise
			


def listNames(floder):
	# ProvisionedDevices
	floder = os.path.expanduser(floder)
	if not os.path.exists(floder) or not os.path.isdir(floder):
		raise Exception('%s not exists' % floder)

	fileNames = os.listdir(floder)
	fileNames = filter(lambda s: s.endswith('.mobileprovision'), fileNames)
	resultPaths = []
	i = 1
	tab = '\t\t'
	print('No.%sProfileName%sAppId%sTeamName' % (tab, tab, tab))
	for file in fileNames:
		filePath = os.path.join(floder, file)
		info = getProfileInfo(filePath)
		name = info.get('Name')
		teamName = info.get('TeamName')
		appId = info.get('Entitlements').get('application-identifier')
		print("%s%s%s%s%s%s%s" % (i, tab, name, tab, appId, tab, teamName))
		i+=1


if __name__ == '__main__':
	try:
		floder = sys.argv[1]
	except Exception as e:
		floder = os.path.expanduser('~/Library/MobileDevice/Provisioning Profiles/')
		print('Use Default floder:%s' % floder)
	listNames(floder)


	

