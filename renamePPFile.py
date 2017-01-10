#!/usr/bin python
# _*_ coding:utf-8 _*_

import sys,os,subprocess,plistlib

nor_dev_count = 0
nor_adhoc_count = 0
nor_dis_count = 0
inHouse_dev_count = 0
inHouse_dis_count = 0


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

def getProfileInfoBundleId(profilePath):
		'''
		@brief 获取描述文件中的信息：使用security命令将profile中的cms信息转为plist
		'''
		dir_path = os.path.dirname(profilePath)
		plistPath = os.path.join(dir_path,'result.plist')
		cmd = 'security cms -D -i %s > %s' %(profilePath, plistPath)
		feedback = execute_cmd(cmd)
		if not os.path.exists(plistPath):
			print 'Generate plist from profile fail'
			print feedback
		try:
			resultPlist = plistlib.readPlist(plistPath)
			entitlements = resultPlist['Entitlements']

			# get bundleId
			result = entitlements['application-identifier'].replace(entitlements['com.apple.developer.team-identifier'] + '.','')

			# 开发描述文件 必有 get-task-allow 值为 YES
			if resultPlist.get('Entitlements').get('get-task-allow') == True:
				# 企业、非企业开发描述文件无区别，只能使用teamName区分 Shenzhen Dong Fang Boya Technology Co.Ltd
				teamName = resultPlist['TeamName']
				if teamName == 'Shenzhen Dong Fang Boya Technology Co.Ltd':
					global inHouse_dev_count
					inHouse_dev_count += 1
				else:
					global nor_dev_count
					nor_dev_count += 1
				result += '_Developer'
			else:
				# 非开发描述文件
				# ADHOC有ProvisionsAllDevices
				# 非ADHOC（含企业和非企业的Distribution描述文件）
				# 非企业发布描述文件含有beta-reports-active = YES
				# 企业发布描述文件含有
				if resultPlist.get('ProvisionedDevices') != None:
					result = result + '_ADHOC'
					global nor_adhoc_count
					nor_adhoc_count += 1
				else:
					result += '_Distribution'
					if resultPlist.get('ProvisionsAllDevices') != None:
						global inHouse_dis_count
						inHouse_dis_count += 1
					else:
						global nor_dis_count
						nor_dis_count += 1


			os.remove(plistPath)
			print result
			return result
		except :
			if os.path.exists(plistPath):
				os.remove(plistPath)
			raise
			


def renameProfiles(floder):
	if os.path.isdir(floder):
		for filename in os.listdir(floder):
			if filename.endswith('.mobileprovision'):
				source = os.path.join(floder, filename)
				target = os.path.join(floder, getProfileInfoBundleId(source) + '.mobileprovision')
				os.rename(source, target)

	else:
		raise Exception('Please enter a floder path')

	print '''
============= Results ======================
== Total: %s
== Developer: %s, (nonInHouse: %s, InHouse: %s)
== Distribution: %s, (nonInHouse: %s, InHouse: %s)
== ADHOC: %s
============================================
	''' % (nor_dev_count+inHouse_dev_count+nor_dis_count+inHouse_dis_count+nor_adhoc_count, nor_dev_count+inHouse_dev_count, nor_dev_count, inHouse_dev_count, nor_dis_count+inHouse_dis_count, nor_dis_count, inHouse_dis_count, nor_adhoc_count)
	

if __name__ == '__main__':
	# floder = sys.argv[1]
	floder = sys.argv[1]
	renameProfiles(floder)




