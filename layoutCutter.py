import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import shutil
import os, sys
import time
#import autoedit_main as am

sys.path.append('//PAROVOZ-FRM01//Shotgun//utils2')
sys.path.append(r'//parovoz-frm01//tank//shared_core//studio//install//core//python//tank_vendor')
import helpers
from shotgun_api3 import Shotgun

SERVER_PATH = 'https://parovoz.shotgunstudio.com' # make sure to change this to https if your studio uses it.
SCRIPT_NAME = 'dmityscripts'
SCRIPT_KEY = 'd8337d21a847a212b98e6f012737eee6d12dff7b74ed71fba7771d278370b585'

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

PRJ_ID = int(os.environ['PRVZ_PROJECT_ID'])
PRJ_NAME = helpers.get_project_name(PRJ_ID)

TYPE_ONE = 'locs'
if PRJ_ID == 134: TYPE_ONE = 'loc'

SCENE_FULLPATH = cmds.file(q=1, expandName=1)
SCENE_PATH, SEPARATOR, FILENAME = SCENE_FULLPATH.rpartition("/")
EP = FILENAME.split('_')[0]

def get_loc():
	loc_list = sg.find('Asset', [['project.Project.id', 'is', PRJ_ID], ['custom_entity01_sg_assets_custom_entity01s.CustomEntity01.code', 'is', EP], ['sg_type_one.CustomEntity04.code', 'is', TYPE_ONE]], ['code', 'sg_reference'])
	print loc_list
	loc_paths = [os.path.abspath(i['sg_reference']['local_path']+'3d\\'+i['sg_reference']['name']+'_rig.ma') for i in loc_list]
	print '\n'.join(loc_paths)
	return '\n'.join(loc_paths)

def get_prj_id(prj_name):
	project_id = prj_name + '_id'
	#print 'DEBUG project_id', project_id
	#print 'helpers.ProjectHelper.' + project_id
	return eval('helpers.ProjectHelper.' + project_id)

def alShotChopOn():

	if cmds.window('LAYOUTCUTTER', exists=True) == True:
		cmds.deleteUI('LAYOUTCUTTER')
	window = cmds.window('LAYOUTCUTTER', title="Let's get some wood..")
	cmds.columnLayout()

	cmds.text( label='Step 1: Remove imageplanes from "ep" shots and set absolute paths. Set camera attributes.' )
	cmds.separator()
	cmds.button( label='Step 1', command=set_step1 )
	cmds.separator( height=5, style='singleDash' )

	cmds.text( label='Step 2: Location assembly . Remove "chars" references, remove shots and cameras.' )
	cmds.separator()
	cmds.button( label='Step 2', command=set_step2 )
	cmds.separator( height=5, style='singleDash' )

	cmds.text( label='Step 3: cut 3D animatic' )
	cmds.separator()
	cmds.checkBoxGrp('serv_shots_grp', numberOfCheckBoxes=2, label='Include Shots:    ', labelArray2=['sh0001', 'ID'])

	cmds.text('progress', label='start/end', visible=False)
	progressControl = cmds.progressBar('progress_control',width=600, visible=False)
	cmds.scrollField('LOC', editable=True, wordWrap=False, w=600, h=60, text=get_loc())
	cmds.checkBox('copy_flag',label='Copy to 2_prod', value=True)
	cmds.checkBox('copyftp_flag',label='Copy to FTP', value=False)

	cmds.textFieldButtonGrp('NAMEFIELD', text="cutscene", bc=lambda *args: start_cutting(progressControl), buttonLabel="CUT",
						  label="Cut Scenes Name Prefix:")
	cmds.text( label='Exclude List' )
	cmds.scrollField('EX', editable=True, wordWrap=False, w=250, h=250, text='chars\nlocs\nloc')

	cmds.button( label='DEBUG', command=lambda *args: debug(args))
	cmds.showWindow(window)

def debug(args):
	print 'DEBUG func'
	shot = pm.ls(sl=True)[0]
	get_shot_paths(shot)

def create_folder(dst_path):
	if not os.path.exists(dst_path):
		print 'MAKING DIR ---> %s' % dst_path
		os.makedirs(dst_path)

def copy_it(src, dst):
	print src, '---->', dst
	print '###'*15+'\n'
	shutil.copy2(src, dst)

def get_shot_paths(shot):
	print 'FUNC get_shot_paths, shot type:', type(shot)
	prefix = str(pm.textFieldButtonGrp('NAMEFIELD', q=1, text=1))
	if '_' in str(shot):
		print 'Renaming shot %s' %str(shot)
		shot.rename(str(shot).split('_')[1])
	unresolved_PATH = SCENE_PATH.replace('//omega/'+PRJ_NAME, '%root%')
	shot_cut_path_unr = unresolved_PATH.rsplit('/', 2)[0] + '/' + shot.name() + '/' + 'cut/'
	shot_work_path_unr = shot_cut_path_unr.replace('cut/','work/')
	shot_work_path_res = shot_work_path_unr.replace('%root%', '//omega/'+PRJ_NAME)
	shot_work_path_ftp = shot_work_path_unr.replace('%root%', '//gamma/homes/ftp'+PRJ_NAME)
	shot_cut_filename_path_unr = shot_cut_path_unr + EP + '_' + shot.name() +'_cut_v001.mov'
	audio_filename_path_unr = shot_cut_path_unr + EP + '_' + shot.name() + '_cut_v001.wav'
	shot_path_res = SCENE_PATH + '/' + prefix + '/'
	#shot_save_noextpath = shot_path_res + EP + '_' + shot.name() + '_layout_v001'
	shot_filename = EP + '_' + shot.name() + '_layout_v001.ma'
	shot_filename_path_res = shot_path_res + shot_filename
	shot_filename_work_path_res = shot_work_path_res + shot_filename
	shot_filename_work_path_ftp = shot_work_path_ftp + shot_filename
	#print 'shot:', shot.name()
	#print 'shot_cut_path_unr:', shot_cut_path_unr
	#print 'shot_work_path_unr:', shot_work_path_unr
	#print 'shot_work_path_res:', shot_work_path_res
	#print 'shot_work_path_ftp:', shot_work_path_ftp
	#print 'shot_filename:', shot_filename
	#print 'shot_filename_work_path_res:', shot_filename_work_path_res
	#print 'shot_filename_work_path_ftp:', shot_filename_work_path_ftp
	#print 'shot_cut_filename_path_unr:', shot_cut_filename_path_unr
	#print 'audio_filename_path_unr:', audio_filename_path_unr
	#print 'shot_path_res:', shot_path_res
	#print 'shot_filename_path_res:', shot_filename_path_res

	shot_paths = {	'shot_cut_path_unr': shot_cut_path_unr,
					'shot_work_path_unr': shot_work_path_unr,
					'shot_work_path_res': shot_work_path_res,
					'shot_work_path_ftp': shot_work_path_ftp,
					'shot_filename': shot_filename,
					'shot_filename_work_path_res': shot_filename_work_path_res,
					'shot_filename_work_path_ftp': shot_filename_work_path_ftp,
					'shot_cut_filename_path_unr': shot_cut_filename_path_unr,
					'audio_filename_path_unr': audio_filename_path_unr,
					'shot_path_res': shot_path_res,
					'shot_filename_path_res': shot_filename_path_res,
					}
	for i in shot_paths.items()
		print i

	return shot_paths

def service_shots_status():
	print 'START service_shots_status'
	opt_sh0001 = cmds.checkBoxGrp('serv_shots_grp', q=1, value1=1)
	opt_id = cmds.checkBoxGrp('serv_shots_grp', q=1, value2=1)
	if not opt_sh0001:
		opt_sh0001 = '0001'
	else:
		opt_sh0001 = ' '
	if not opt_id:
		opt_id = 'id'
	else:
		opt_id = ' '
	return [opt_sh0001, opt_id]

def set_step1(checkBoxOpt):
	#get excluded shots
	exclude_shots = service_shots_status()

	#remove imageplanes from "ep" shots
	shots = cmds.ls(type="shot")
	print 'DEBUG shots', shots
	for s in shots[:]:
		for e in exclude_shots:
			if e not in s:
				pass
			else:
				shots.remove(s)
				print 'remove: ', s
	#print 'DEBUG shots', shots
	#for i in shots:
		#result = 'OK'

        #check shots sequence coherence
		cur_ind = shots.index(i)
		if cur_ind > 0:
		#if cur_ind > 0 and opt_id not in i or opt_sh0001 not in i:
			print 'DEBUG cur_ind', cur_ind
			print 'DEBUG shot:', i
			prw_ind = shots.index(i) - 1
			#print 'DEBUG i8', i[8:]
			#print 'DEBUG i8-1', shots[prw_ind][8:]
			if int(i[8:]) - int(shots[prw_ind][8:]) != 1:
				result = cmds.promptDialog(
						title='Naming Error',
						message='Shots: '+ shots[prw_ind] + ' and ' + i,
						button=['OK', 'Cancel'],
						defaultButton='OK',
						cancelButton='Cancel',
						dismissString='Cancel')

		if result == 'OK':

			ip = cmds.connectionInfo(i + '.clip', sourceFromDestination = True)
			if ip:
				ipp = ip.split('.')[0].split('>')[1]
				if 'id' not in i:
					print 'shot:', i, 'imagePlane:', ipp
					cmds.delete(ipp)
#replace paths in imageplanes
	if result == 'OK':
		ips = cmds.ls(type='imagePlane')
		for i in ips:
			p1 = cmds.getAttr(i + '.imageName')
			p2 = p1.replace('omega/'+PRJ_NAME, '%root%')
			cmds.setAttr(i + '.imageName', p2, type='string')
			print i, p1, '-->', p2, '\n'
	 
		cams =  getCameras()
		for i in cams:
			cmds.setAttr(i + '.farClipPlane', 100000)
			cmds.setAttr(i + '.horizontalFilmAperture', 1.679)

def set_step2(args):
	all_scene_refs = pm.listReferences()
	for ref in all_scene_refs:
		ref_path = str(ref.path)
		if 'chars' in ref_path:
			print 'unload', str(ref)
			ref.remove()
	
	#remove shots, cameras and audio
	shots = pm.ls(type="shot")
	cams =  getCameras()
	audio = pm.ls(type='audio')
	for i in shots+cams+audio:
		pm.delete(i)
		print 'delete node: %s' %i

def get_exclude_asset_list():
	exclude_list = pm.scrollField('EX', q=1, text=True)
	return exclude_list.split('\n')

#def alRunChop(progressControl):
	#prefix = str(pm.textFieldButtonGrp('NAMEFIELD', q=1, text=1))
	#start_cutting(prefix, progressControl)

def start_cutting(progressControl):
	#prefix = str(pm.textFieldButtonGrp('NAMEFIELD', q=1, text=1))
# Kill all jobs
	cmds.scriptJob(ka=True)

	exclude_shots = service_shots_status()

# Get shots
	shots = pm.ls(type="shot", sl=1)
	allShots = pm.ls(type="shot")
	allCams = pm.ls(type="camera")
	if not shots: shots = allShots

	location_path = str(pm.scrollField('LOC', q=1, text=1).replace('\\\\omega\\'+PRJ_NAME, '%root%'))
	cmds.progressBar('progress_control', edit=True, progress=0, maxValue=len(shots), visible=True)

	for count, shot in enumerate(shots):
		cmds.text('progress', edit=True, label=shot+'/'+shots[-1], visible=True)
		if cmds.progressBar(progressControl, query=True, isCancelled=True):
			break
		if exclude_shots[0] not in str(shot) and exclude_shots[1] not in str(shot):
			print 'SHOT:', shot
			print 'SHOT type:', type(shot)
			shot_paths = get_shot_paths(shot)
			#if count != 0:
			cmds.file(SCENE_FULLPATH, prompt=False, force=1, open=1, resetError=1)

			#remove audio
			audio = pm.ls(type='audio')
			for i in audio:
				pm.delete(i)

			#fix ref paths, remove all refs except exclude list and load location ref
			all_scene_refs = pm.listReferences()
			fix_ref_paths(all_scene_refs)
			replace_location(location_path, all_scene_refs, shot_paths['shot_filename'])

			# Get camera for this shot
			cam = pm.listConnections(shot, type="shape")
			camShape = cmds.listRelatives(str(cam[0]), shapes=True)[0]

			if str(shot) in str(cam[0]) and 'Camera1' in str(cam[0]):
				camName = 'cam_' + str(cam[0]).split('_')[1].replace('Camera1', '')
				print 'CAMERA OK\n'
				cmds.rename(str(cam[0]), camName)
			elif str(cam[0]) == 'cam_'+str(shot):
				print 'NEW CAMERA OK\n'
				pass
			else:
				print 'create CAMERA for shot', shot, '\n'
				cloneCamera(cam, camShape, str(shot))

			#create image plane for shot camera
			im_plane = create_imagePlane(cam[0], shot, shot_paths['shot_cut_filename_path_unr'])

			#cleanup cameras
			tmp =  getCameras()
			tmp.remove(str(cam[0]))
			print 'delete cam',str(cam[0]),  tmp
			cmds.delete(tmp)#delete unused cameras

			#create sound
			createSound(shot_paths['audio_filename_path_unr'])

			# get out shot's range and move all animation of it to 1st frame
			sf = int(shot.getStartTime())
			ef = int(shot.getEndTime())
			alMoveACsegment(sf, ef)
			pm.playbackOptions(max=(1 + ef - sf), ast=1, aet=(1 + ef - sf), min=1)
			pm.lockNode(allShots, lock=False)
			pm.delete(allShots)
			
			#create destination folder for saving scene
			create_folder(shot_paths['shot_path_res'])

			#rename and save maya scene
			cmds.file(rename=(shot_paths['shot_filename_path_res']))
			cmds.file(save=1, type="mayaAscii", options="v=0;", f=1)

			#copy scene to work path and ftp
			if cmds.checkBox('copy_flag', query=True, value=True) == True:
				copy_it(shot_paths['shot_filename_path_res'], shot_paths['shot_filename_work_path_res'])

			if cmds.checkBox('copyftp_flag', query=True, value=True) == True:
				create_folder(shot_paths['shot_work_path_ftp'])
				copy_it(shot_paths['shot_filename_path_res'], shot_paths['shot_filename_work_path_ftp'])

		cmds.progressBar(progressControl, edit=True, step=1)

def createSound(sound_file_path):
	#pm.sound(offset=1, file=sound_file_path)
	sound_node = cmds.createNode('audio')
	cmds.setAttr(sound_node+'.offset', 1)
	cmds.setAttr(sound_node+'.filename', sound_file_path, type='string')

def create_imagePlane(cam, shot, shot_cut_filename_path_unr):

	cam_shape = cam.getShape()
	print '@cam_shape:', cam_shape
	if not pm.listConnections(cam_shape+'.imagePlane[0]', sh=True):
		mel.eval('source AEcameraImagePlaneNew')
		mel.eval('AEcameraImagePlaneCommand ' + str(cam_shape) + '.imagePlane ' + str(cam_shape) + '.horizontalFilmAperture ' + str(cam_shape) + '.verticalFilmAperture;')
		print 'Creating Image Plane --->'
	im_plane = pm.listConnections(cam_shape+'.imagePlane[0]', sh=True)[0].split('->')[1]
	print 'Setting Image Plane --->', im_plane
	pm.setAttr(im_plane+'.imageName', shot_cut_filename_path_unr)
	#print 'DEBUG shot_cut_filename_path_unr', shot_cut_filename_path_unr
	pm.setAttr(im_plane+'.type', 2)
	#disconnect image plane from shot
	pm.disconnectAttr(shot+'.clip')
	return im_plane

def fix_ref_paths(all_scene_refs):
	for i in all_scene_refs:
		path_unr = i.unresolvedPath()
		if '%root%' not in path_unr:
			path_fix = path_unr.replace('//','/').split('/',3)[-1]
			print 'replace for: ' + str(i) + 'with: ' + '%root%'+'/' + path_fix
			i.replaceWith('%root%'+'/'+path_fix)

def replace_location(location_path, all_scene_refs, shot_filename):
	if location_path:
		location_path = location_path.split('\n')
		exclude_list = get_exclude_asset_list()
		for ref in all_scene_refs:
			ref_path = str(ref.path)
			ref_namespace = str(ref.namespace)
			if [True for i in exclude_list if i in ref_path or i in ref_namespace]:
				print 'LEAVE REF:', str(ref)
			else:
				print 'REMOVE REF:', str(ref)
				ref.remove()
		for loc in location_path:
			print loc
			shot_filename_no_ext = shot_filename.split('.')[0]
			print 'LOCATION', loc, shot_filename_no_ext
			pm.createReference(loc, namespace=shot_filename_no_ext)
		else:
			print 'NO LOCATION PROVIDED'

def getCameras():
# Get all cameras first
	cameras = pm.ls(type=('camera'), l=True)

# Let's filter all startup / default cameras
	startup_cameras = [camera for camera in cameras if pm.camera(camera.parent(0), startupCamera=True, q=True)]

# non-default cameras are easy to find now. Please note that these are all PyNodes
	non_startup_cameras_pynodes = list(set(cameras) - set(startup_cameras))

# Let's get their respective transform names, just in-case
	non_startup_cameras_transform_pynodes = map(lambda x: x.parent(0), non_startup_cameras_pynodes)

# Now we can have a non-PyNode, regular string names list of them
	non_startup_cameras = map(str, non_startup_cameras_pynodes)
	non_startup_cameras_transforms = map(str, non_startup_cameras_transform_pynodes)
	return non_startup_cameras_transforms

def cloneCamera(cam1, camShape1, shot1):
	cm = str(pm.duplicate(cam1, name='DUPLICATE')[0])
	cmShape = cmds.listRelatives(cm, shapes=True)[0]
	cmds.connectAttr(cmShape + '.message', shot1 + '.currentCamera', force=True)

def alMoveACsegment(startFrame, endFrame):
    lastFrame = 0.0
    preRange = "0:" + str((startFrame - 1))
    allaCurves = pm.ls(type="animCurve")
    refCurves = pm.ls(type="animCurve", referencedNodes=1)
    animCurves = [x for x in allaCurves if x not in refCurves]
    for aCurve in animCurves:
        if (pm.objectType(aCurve) == "animCurveTU") or (pm.objectType(aCurve) == "animCurveTA") or (pm.objectType(aCurve) == "animCurveTL"):
            pm.setAttr((str(aCurve) + ".ktv"),
                       l=1)
            pm.setAttr((str(aCurve) + ".ktv"),
                       l=0)
            lastFrame = float(pm.findKeyframe(aCurve, which="last"))
            if lastFrame <= endFrame:
                lastFrame = float(endFrame + 2)

            postRange = str((endFrame + 1)) + ":" + str(lastFrame)
            if (pm.getAttr(str(aCurve) + ".pre") == 0) and (pm.getAttr(str(aCurve) + ".pst") == 0):
                pm.setKeyframe(aCurve, insert=1, time=startFrame)
                pm.setKeyframe(aCurve, insert=1, time=endFrame)
                pm.cutKey(aCurve, time=preRange)
                pm.cutKey(aCurve, time=postRange)

			#print "\nanimCurve: " + str(aCurve)
            pm.keyframe(aCurve, e=1, iub=True, o='over', r=1, time=(str(startFrame) + ":" + str(endFrame)),
                        tc=(-(startFrame - 1)))

if '__main__' == __name__:
	alShotChopOn()
