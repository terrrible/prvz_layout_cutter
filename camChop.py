import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import shutil
import os, sys
#import autoedit_main as am

sys.path.append('//PAROVOZ-FRM01//Shotgun//utils2')
sys.path.append(r'//parovoz-frm01//tank//shared_core//studio//install//core//python//tank_vendor')
import helpers
from shotgun_api3 import Shotgun

SERVER_PATH = 'https://parovoz.shotgunstudio.com' # make sure to change this to https if your studio uses it.
SCRIPT_NAME = 'dmityscripts'
SCRIPT_KEY = 'd8337d21a847a212b98e6f012737eee6d12dff7b74ed71fba7771d278370b585'

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

#PRJ = os.environ['root']
PRJ = 'woowoo'
PRJ_ID = int(os.environ['PRVZ_PROJECT_ID'])
TYPE_ONE = 'locs'
if PRJ_ID == 134: TYPE_ONE = 'loc'
#location = '%root%\\0_assets\\locs\\environment_ground\\lawn_tree_little\\3d\\lawn_tree_little_rig.ma'
scene_path = cmds.file(q=1, expandName=1)
path, separator, filename = scene_path.rpartition("/")
ep = filename.split('_')[0]

def get_loc():
	#project = get_prj_id('woody')
	#prj_id = 127 #woody
	loc_list = sg.find('Asset', [['project.Project.id', 'is', PRJ_ID], ['custom_entity01_sg_assets_custom_entity01s.CustomEntity01.code', 'is', ep], ['sg_type_one.CustomEntity04.code', 'is', TYPE_ONE]], ['code', 'sg_reference'])
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

	if cmds.window('CHOPOUTWIN', exists=True) == True:
		cmds.deleteUI('CHOPOUTWIN')

	window = cmds.window('CHOPOUTWIN', title="animania Shot Choppa")
	cmds.columnLayout()

	cmds.text( label='Step 1: Remove imageplanes from "ep" shots and set absolute paths. Set camera attributes.' )
	cmds.separator()
	cmds.button( label='Step 1', command=set_step1 )
	cmds.separator( height=5, style='singleDash' )

	cmds.text( label='Step 2: Location assembly (Woody) . Remove "chars" references, remove shots and cameras.' )
	cmds.separator()
	cmds.button( label='Step 2', command=set_step2 )
	cmds.separator( height=5, style='singleDash' )

	cmds.text( label='Step 3: cut 3D animatic' )
	cmds.separator()
	checkBoxOpt = cmds.checkBoxGrp(numberOfCheckBoxes=2, label='Cut Options:    ', labelArray2=['Include sh0001', 'Include ID shots'])

	progressControl = cmds.progressBar(width=600, visible=False)
	cmds.scrollField('LOC', editable=True, wordWrap=False, w=600, h=60, text=get_loc())
	#cmds.textFieldButtonGrp('NAMEFIELD', text="cutscene", bc=lambda *args: alRunChop(), buttonLabel="Chop On!",
						  #label="Cut Scenes Name Prefix:")
	cmds.textFieldButtonGrp('NAMEFIELD', text="cutscene", bc=lambda *args: alRunChop(progressControl, checkBoxOpt), buttonLabel="CUT",
						  label="Cut Scenes Name Prefix:")
	cmds.text( label='Exclude List' )
	cmds.scrollField('EX', editable=True, wordWrap=False, w=250, h=250, text='chars\nlocs\nloc')

	cmds.button( label='DEBUG', command=lambda *args: debug(checkBoxOpt))
	cmds.showWindow(window)

def debug(checkBoxOpt):
	print 'START DEBUG'
	opt_sh0000 = cmds.checkBoxGrp(checkBoxOpt, q=1, value1=1)
	opt_id = cmds.checkBoxGrp(checkBoxOpt, q=1, value2=1)
	if opt_sh0000:
		opt_sh0000 = 'sh0000'
	else:
		opt_sh0000 = ''
	if opt_id:
		opt_id = 'id'
	else:
		opt_id = ''
	print opt_sh0000, opt_id

def set_step1(args):
#remove imageplanes from "ep" shots
	shots = cmds.ls(type="shot")
	print 'DEBUG shots', shots
	for i in shots:

#check shots sequence coherence
		cur_ind = shots.index(i)
		print 'DEBUG cur_ind', cur_ind
		if cur_ind > 0 and 'id' not in i and '0001' not in i:
			prw_ind = shots.index(i) - 1
			print 'DEBUG i8', i[8:]
			print 'DEBUG i8-1', shots[prw_ind][8:]
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
			p2 = p1.replace('omega/woody', '%root%')
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

def get_exclude_list():
	exclude_list = pm.scrollField('EX', q=1, text=True)
	return exclude_list.split('\n')

def alRunChop(progressControl, checkBoxOpt):
    prefix = str(pm.textFieldButtonGrp('NAMEFIELD', q=1, text=1))
    alChopEmAll(prefix, progressControl, checkBoxOpt)

def alChopEmAll(prefix, progressControl, checkBoxOpt):
# Kill all jobs
	cmds.scriptJob(ka=True)

# Get filename and path
	#fileName = cmds.file(q=1, expandName=1)
	#path, separator, filename = fileName.rpartition("/")
# Get shots
	shots = [i.getShotName() for i in pm.ls(type="shot", sl=1)]
	allShots = pm.ls(type="shot")
	allCams = pm.ls(type="camera")
	if not shots: shots = allShots

	print 'MAX VALUE', len(shots)
	cmds.progressBar(progressControl, edit=True, maxValue=len(shots), visible=True)
	cmds.progressBar(progressControl, edit=True, step=1)

	location_path = str(pm.scrollField('LOC', q=1, text=1).replace('\\\\omega\\woody', '%root%'))

	for shot in shots:
		if cmds.progressBar(progressControl, query=True, isCancelled=True):
			break
		cmds.progressBar(progressControl, edit=True, step=1)
		#print 'SHOT PRE:', shot
		#shot = shot.getShotName()
		print 'SHOT:', shot
		if opt_id not in str(shot) and opt_sh0000 not in str(shot):
		#if 'sh0001' not in str(shot):
			cmds.file(scene_path, prompt=False, force=1, open=1, resetError=1)
			if location_path: replace_location(location_path)

			# Get camera for this shot
			cam = pm.listConnections(shot, type="shape")
			camShape = cmds.listRelatives(str(cam[0]), shapes=True)[0]
			print camShape
			#print '@@3', shot, cam
			if str(shot) in str(cam[0]):
				camName = 'cam_' + str(cam[0]).split('_')[1].replace('Camera1', '')
				print 'CAMERA OK\n'
				cmds.rename(str(cam[0]), camName)
			else:
				print 'create CAMERA for shot', shot, '\n'
				cloneCamera(cam, camShape, str(shot))

			#cmds.setAttr(str(cam[0]) + '.horizontalFilmAperture', 1.679)

			#create image plane for shot camera
			cut_path = create_imagePlane(cam[0], shot, path)

			#cleanup cameras
			tmp =  getCameras()
			tmp.remove(str(cam[0]))
			print 'delete cam',str(cam[0]),  tmp
			cmds.delete(tmp)#delete unused cameras

			#create sound
			sound_file_path = cut_path + str(shot) + '_cut_v001.wav'
			createSound(sound_file_path)

			sf = int(pm.getAttr(str(shot) + ".startFrame"))
			# get out shot's range and move all animation of it to 1st frame
			ef = int(pm.getAttr(str(shot) + ".endFrame"))
			alMoveACsegment(sf, ef)
			pm.playbackOptions(max=(1 + ef - sf), ast=1, aet=(1 + ef - sf), min=1)
			pm.lockNode(allShots, lock=False)
			pm.delete(allShots)

			save_dir = path + '/' + prefix + '/'
			full_save_path = path + '/' + prefix + '/' + str(shot) + '_layout_v001'
			print 'DEBUG full_save_path', full_save_path
			print '###'*15
			if not os.path.exists(save_dir):
				print 'MAKING DIR ---> %s' % save_dir
				os.makedirs(save_dir)

			cmds.file(rename=(full_save_path))
			scene_filename_path = cmds.file(save=1, type="mayaAscii", options="v=0;", f=1)

			#copy scene to work path
			scene_filename_dest_path = scene_filename_path.rsplit('/',1)[1]
			scene_filename_workpath = cut_path.replace('cut/','work/')
			scene_filename_dest_filename_path = scene_filename_workpath.replace('%root%', '//omega/woody') + scene_filename_dest_path
			print scene_filename_path, '---->', scene_filename_dest_filename_path
			print '###'*15+'\n'
			shutil.copy2(scene_filename_path, scene_filename_dest_filename_path)

def createSound(sound_file_path):
	#pm.sound(offset=1, file=sound_file_path)
	sound_node = cmds.createNode('audio')
	cmds.setAttr(sound_node+'.offset', 1)
	cmds.setAttr(sound_node+'.filename', sound_file_path, type='string')

def create_imagePlane(cam, shot, path):

	#cam = pm.ls('camera1')[0]
	cam_shape = cam.getShape()
	sh_name = str(shot).split('_')[1]
	#print 'CAM', cam
	#print 'CAMS', cam_shape
	mel.eval('source AEcameraImagePlaneNew')
	mel.eval('AEcameraImagePlaneCommand ' + str(cam_shape) + '.imagePlane ' + str(cam_shape) + '.horizontalFilmAperture ' + str(cam_shape) + '.verticalFilmAperture;')
	im_plane = pm.listConnections(cam_shape+'.imagePlane[0]', sh=True)[0].split('->')[1]
	#print 'CAMC', pm.listConnections(cam_shape+'.imagePlane[0]', sh=True)
	cut_path = path.replace('//omega/woody', '%root%').rsplit('/', 2)[0] + '/' + sh_name + '/' + 'cut/'
	print 'DEBUG cut path', cut_path
	cut_filename_path = cut_path + str(shot)+'_cut_v001.mov'
	pm.setAttr(im_plane+'.imageName', cut_filename_path)
	print 'DEBUG cut_filename_path', cut_filename_path
	pm.setAttr(im_plane+'.type', 2)
	return cut_path

def replace_location(location_path):
	print 'DEBUG location_path', location_path
	location_path = location_path.split('\n')
	all_scene_refs = pm.listReferences()
	exclude_list = get_exclude_list()
	for ref in all_scene_refs:
		ref_path = str(ref.path)
		if [True for i in exclude_list if i in ref_path]:
			print 'LEAVE REF:', str(ref)
		else:
			print 'REMOVE REF:', str(ref)
			ref.remove()
	for loc in location_path:
		print loc
		scenename = loc.rsplit('\\', 1)[1].split('.')[0]
		print 'LOCATION', loc, scenename
		pm.createReference(loc, namespace=scenename)

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
