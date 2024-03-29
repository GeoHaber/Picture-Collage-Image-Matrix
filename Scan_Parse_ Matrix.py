# -*- coding: utf-8 -*-
#!/usr/bin/python3
__author__ = 'GeoHaZen'
'''
@author: 	  GeoHaZen
#XXX KISS
'''

import os
import re
import sys
import json
import cgitb
import shutil
import random
import datetime
import traceback
import subprocess
from   My_Utils  import *

DeBug		= False

Vi_Dur		= ''
Tot_Frms	= 0
Max_v_btr	= 2300000
Max_a_btr	= 380000
Max_frm_rt	= 35

Out_F_typ	= '.mkv'

Tmp_F_Ext	= '_XY_' + Out_F_typ

Excepto	= 'C:\\Users\\Geo\\Desktop\\Except'

Folder	= 'C:\\Users\\Geo\\Desktop\\downloads'
#Folder  = 'E:\\_Adlt'
Folder	= 'E:\\Media\\Movie'
#Folder	= 'E:\\Media\\TV'
#Folder = '\\\\NAS-Q\\Multimedia\Movie'
#Folder	= 'D:\\Media'
#Folder	= 'C:\\Users\\Geo\\Desktop\\Except'


VIDEO_EXTENSIONS = ['.avchd', '.avi', '.dat', '.divx', '.dv', '.flic', '.flv', '.flx', '.h264', '.m4v', '.mkv',
					'.moov', '.mov', '.movhd', '.movie', '.movx', '.mp4', '.mpe', '.mpeg', '.mpg', '.mpv', '.mpv2',
					'.ram', '.rm', '.rmvb', '.swf', '.ts', '.vfw', '.vid', '.video', '.viv', '.vivo',
					'.vro', '.wm', '.wmv', '.wmx', '.wrap', '.wvx', '.webm', '.x264', '.xvid']

This_File  = sys.argv[0].strip ('.py')
Log_File   = This_File + '_run.log'
Bad_Files  = This_File + '_bad.txt'
Good_Files = This_File + '_good.txt'

ffmpeg_bin  = 'C:\\Program Files\\ffmpeg\\bin'
ffmpeg_exe  = "ffmpeg.exe"
ffprobe_exe = "ffprobe.exe"
ffmpeg		= os.path.join( ffmpeg_bin, ffmpeg_exe  )
ffprobe		= os.path.join( ffmpeg_bin, ffprobe_exe )
##>>============-------------------<  End  >------------------==============<<##

def Move_Del_File (src, dst, DeBug=False ):
	'''
	If Debug then files are NOT deleted, only copied
	'''
	message = sys._getframe().f_code.co_name + '-:'

	try :
		if os.path.isdir(src) and os.path.isdir(dst) :
			shutil.copytree(src, dst)
		else:
			shutil.copy2(src, dst)
			if not DeBug :
				try :
					os.remove( src )
				except OSError as e:  ## if failed, report it back to the user ##
					message += f"\n!Error: {src}\n{e.filename}\n{e.strerror}\n"
					if DeBug : print( message )
					raise  Exception( message )
			else:
				print (f" ! Placebo did NOT delete: {src}")
				time.sleep ( 1 )
	except OSError as e:  ## if failed, report it back to the user ##
		message += f"\n!Error: Src {src} , Dst {dst}\n{e.filename}\n{e.strerror}\n"
		if DeBug : print( message )
		raise  Exception( message )
	else:
		return True
##>>============-------------------<  End  >------------------==============<<##

def Create_File (dst, msge= '', times=1, DeBug=False ):
#	DeBug = True
	message = sys._getframe().f_code.co_name + '-:'
	if DeBug :
		message += f"Dst {dst}\nMsg {msge} Times {times}\n Press Any Key to go on"
		input ( message )
		return  False
	else :
		try :
			Cre_lock = open( dst, "w",encoding="utf-8" )
			if Cre_lock :
				Cre_lock.write ( msge * times )
				Cre_lock.flush()
		except OSError as e:  ## if failed, report it back to the user ##
			message += f"\n!Error: {dst}\n{e.filename}\n{e.strerror}\n"
			if DeBug : print (message)
			raise Exception( message )
	return True
##>>============-------------------<  End  >------------------==============<<##

def Parse_year ( FileName ) :
#	DeBug = True
	message = sys._getframe().f_code.co_name + '-:'
	if DeBug :	print( message )
	try :
		yr	= re.findall( r'[\[\(]?((?:19[4-9]|20[0-1])[0-9])[\]\)]?', FileName )
		if yr :
			va	= sorted(yr, key=lambda pzd: int(pzd), reverse=True)
			za  = int(va[0])
			if za > 2019 or za < 1930 :
				za = 1954
			if DeBug : print ( FileName, yr, len(yr), va, za )
		else :
			za = 1890
	except :
		za = 1
	return za
##>>============-------------------<  End  >------------------==============<<##

def Sanitize_file ( root, one_file, extens ) :
	message    = sys._getframe().f_code.co_name + '-:'

	fi_path     = os.path.normpath( os.path.join( root, one_file ) )
	fi_size     = os.path.getsize( fi_path )
	fi_info     = os.stat( fi_path )
	year_made	= Parse_year( fi_path )
#XXX  |[0] Extension |[1] Full Path |[2] File Size |[3] File Info |[4] Year Made XXX
	return	extens, fi_path, fi_size, fi_info, year_made
##>>============-------------------<  End  >------------------==============<<##

""" =============== The real McCoy =========== """
def Build_List ( Top_dir, Ext_types, Sort_loc=2, Sort_ord=True  ) : # XXX: Sort_ord=True (Big First) Sort_loc = 2 => File Size: =4 => year_made
	'''
	Create the list of Files to be proccesed
	'''
#	DeBug = True
	message    = sys._getframe().f_code.co_name + '-:'

	cnt 		= 0
	queue_list 	= []

	print("=" * 60)
	start_time = datetime.datetime.now()
	value = HuSa (get_tree_size ( Top_dir ) )
	print ('Dir: {}\tis: {}'.format( Top_dir, value ) )
	print('Start: {:%H:%M:%S}'.format( start_time ))

	# a Directory ?
	if os.path.isdir ( Top_dir ) :
		message  += "\n Directory Scan :{}".format( Top_dir )
		print ( message )
		for root, dirs, files in os.walk( Top_dir ):
			for one_file in files:
				x, extens = os.path.splitext( one_file.lower() )
				if extens in Ext_types :
					Save_items	= Sanitize_file( root, one_file, extens )
					queue_list += [ Save_items ]
	# a File ?
	elif os.path.isfile ( Top_dir ) :
		message += f" -> Single File Not a Directory: {Top_dir}"
		print ( message )
		x,  extens  = os.path.splitext( Top_dir.lower() )
		if extens in Ext_types :
			Save_items	= Sanitize_file( root, one_file, extens )
			queue_list += [ Save_items ]

# XXX: https://wiki.python.org/moin/HowTo/Sorting
# XXX: Sort based in item [2] = filesize defined by Sort_loc :)
	queue_list = sorted( queue_list, key=lambda Item: Item[Sort_loc], reverse=Sort_ord ) ## XXX: sort defined by caller
	end_time    = datetime.datetime.now()
	Tot_time	= end_time - start_time
	Tot_time 	= Tot_time.total_seconds()
	print(f'End  : {end_time:%H:%M:%S}\tTotal: {Tot_time}')
	return queue_list
##>>============-------------------<  End  >------------------==============<<##

def Skip_Files ( File_dscrp, Min_fsize=10240 ) :
#	DeBug = True
	'''
	Returns True if lock file is NOT
	'''
	message = sys._getframe().f_code.co_name + '-:'
#XXX  |[0] Extension |[1] Full Path |[2] File Size |[3] File Info |[4] Year Made XXX
	The_file  = File_dscrp[1]
	Fname, ex = os.path.splitext( The_file )
	fi_size   = File_dscrp[2]

## XXX: File does not exist :(
	if not os.path.exists ( The_file ) :
		message += f"\n File Not Found {The_file}\n"
		print ( message )
		Exeptions_File.write(message)
		Exeptions_File.flush()
		sys.stdout.flush()
		if DeBug : input ("? Skip it ?")
		return False

# XXX Big enough to be video ?? # 256K should be One Mega byte 1048576
	elif fi_size < Min_fsize :
		message += f"\n To Small:| {HuSa(fi_size):9} | {The_file}\n"
		print ( message )
		Exeptions_File.write(message)
		Exeptions_File.flush()
		sys.stdout.flush()
		if DeBug : input ("? Skip it ?")
		return False

## XXX:  Ignore files that have been Locked (Procesed before)
	Lock_File = The_file + ".lock"
	Lock_File = Fname + ".png"

	if os.path.exists ( Lock_File ) :
		message += f"Locked {os.path.basename( Lock_File)}\n"
		print (message)
		Succesful_File.write( message )
		Succesful_File.flush()
		sys.stdout.flush()
		return False

	return Lock_File
##>>============-------------------<  End  >------------------==============<<##

def Do_it ( List_of_files, Excluded ='' ):
#	global DeBug
#	DeBug = True

	message = sys._getframe().f_code.co_name +'-:'
	print("=" * 60)
	print( message )
	print (' Total of {} Files to Procces'. format( len( List_of_files ) ) )

	if DeBug : print (f"Proccesing {List_of_files} one by one" )

	if not List_of_files :
		raise ValueError( message, 'No files to procces' )

	elif len( Excluded ) :
		message += " Excluding" + len( Excluded ) + Excluded
		raise ValueError( message, 'Not Implemented yet :( ' )

	queue_list 	=[]
	Fnum  		= 0
	Saving 		= 0
	cnt         = len(List_of_files)

	for File_dscrp in List_of_files:
		print("-" * 20)
		Fnum     += 1
#XXX  |[0] Extension |[1] Full Path |[2] File Size |[3] File Info |[4] Year Made XXX
		extens	  = File_dscrp[0]
		The_file  = File_dscrp[1]
		fi_size   = File_dscrp[2]
		year_made = File_dscrp[4]
		message = f': {ordinal(Fnum)} of {cnt}, {HuSa(fi_size)}, {extens}, Year {year_made}\n: {The_file}'
		print ( message )
		start_time = datetime.datetime.now()
		print ( f' Start: {start_time:%H:%M:%S}')
		Lock_File = Skip_Files( File_dscrp )
		if Lock_File :
			try:
				if DeBug : print ("\nDo> FFProbe_run")
				all_good = FFProbe_run( The_file )
				if  all_good :
					if DeBug : print ("\nDo> FFZa_Brain")
					all_good = FFZa_Brain( The_file, all_good )
					if  all_good :
						if DeBug : print ("\nDo> FFMpeg_run")
						all_good = FFMpeg_run( The_file, all_good )
						if  all_good :
							cnt -= 1
							queue_list += [The_file]
							message = f' File {The_file} _Run_ {all_good}\n'
							Succesful_File.write( message )
							Succesful_File.flush()
	#						all_good = Create_File ( Lock_File, message, DeBug=True )
# XXX: Someting is Fish :O
						else:
							message +=  '\n FFMpeg_run  ErRor :'
							message += f'\n Copy & Delete {The_file}\n'
							print (message)
							Exeptions_File.write(message)
#							Create_File   ( Lock_File, message, 10, DeBug=True )
							Move_Del_File ( The_file, Excepto, DeBug=True )
					else :
						message +=  '\n FFZa_Brain  ErRor :'
						message += f'\n Copy & Delete {The_file}\n'
						print (message)
						Exeptions_File.write(message)
#						Create_File   ( Lock_File, message, 10, DeBug=True )
						Move_Del_File ( The_file, Excepto, DeBug=True )
				else :
					message +=  '\n FFProb   ErRor :'
					message += f'\n Copy & Delete {The_file}'
					print (message)
					Exeptions_File.write(message)
#					Create_File   ( Lock_File, message, 10 )
					Move_Del_File ( The_file, Excepto, DeBug=True )
			except ValueError as err:
				message += f"\n\n ValueError Exception {err.args}"
				if '_Skip_it :' in message :
					print('_Skip_it :')
#					time.sleep(3)
					Succesful_File.write( message )
#					Create_File ( Lock_File, message )
				else:
					Exeptions_File.write( message )
					message += f'\n Copy & Delete {The_file}'
					print (message)
#					Create_File   ( Lock_File, message, 10, DeBug=True )
					Move_Del_File ( The_file, Excepto, DeBug=True )
			except Exception as e:
				message += f" WTF? General Exception {e}"
				print ( "\n", "-+" *20)
				print (message)
				print( f"Stack:\n{traceback.print_stack( limit=5 )}\n" )
				print( f"Exec:\n{ traceback.print_exc( limit=5 ) }\n" )
				print ( "\n", "=" *40)
#				Create_File   ( Lock_File, message, 100, DeBug=True )
				Move_Del_File ( The_file, Excepto, DeBug=True )
				Exeptions_File.flush()
				Succesful_File.flush()
				sys.stdout.flush()
				input ("## Bad Error :")
			else:
				pass
			Exeptions_File.flush()
			Succesful_File.flush()
			sys.stdout.flush()
		else :
			cnt -= 1
			queue_list += [The_file]
			Exeptions_File.flush()
			Succesful_File.flush()

		sys.stdout.flush()
		end_time    = datetime.datetime.now()
		Tot_time	= end_time - start_time
		Tot_time 	= Tot_time.total_seconds()
		print(f' End  : {end_time:%H:%M:%S}\tTotal: {Tot_time}')
		print('='*20)
	return queue_list
##>>============-------------------<  End  >------------------==============<<##

def FFProbe_run (File_in, Execute= ffprobe ):
#	global DeBug
#	DeBug = True

	start_time	= datetime.datetime.now()
	message 	= sys._getframe().f_code.co_name + '|:'
	print(f"  {message}\t\tStart: {start_time:%H:%M:%S}")

	if os.path.exists (File_in) :
		file_size = os.path.getsize(File_in)
		message = f"\n{File_in}\t{HuSa(file_size)}\n"
		if DeBug :	print ( message )
	else :
		message += f"No Input file:( \n {File_in}"
		print (message)
		if DeBug : input ('Now WTF?')
		return False

	Comand = [ Execute ,
		'-analyzeduration', '2000000000',
		'-probesize',       '2000000000',
		'-i', File_in,
		'-v', 'verbose',		# XXX quiet, panic, fatal, error, warning, info, verbose, debug, trace
		'-of', 'json',			# XXX default, csv, xml, flat, ini
		'-hide_banner',
		'-show_format',
		'-show_error',
		'-show_streams' ]

	try :
		ff_out = subprocess.run( Comand,
				stdout	= subprocess.PIPE,
				stderr	= subprocess.PIPE,
				universal_newlines = True,
				encoding='utf-8')
	except subprocess.CalledProcessError as err:	# XXX: TBD Fix error in some rare cases
		message += f" FFProbe: CalledProcessError {err}"
		if DeBug : print( message ), input ('Next')
		raise  Exception( message )
	else:
		out	= ff_out.stdout
		err = ff_out.stderr
		bad = ff_out.returncode
		if bad  :
			message += f"Oy vey {bad}\nIst mir {err}\n"
			if DeBug : print( message ), input("Bad")
			raise ValueError( message )
		else:
			jlist = json.loads( out )
			if len (jlist) < 2 :
				message += f"Json out to small\n{File_in}\n{jlist}"
				if DeBug : print( message ), input(" Jlist to small ")
				raise  Exception( message )
		end_time    = datetime.datetime.now()
		Tot_time	= end_time - start_time
		Tot_time 	= Tot_time.total_seconds()
		print(f'   End  : {end_time:%H:%M:%S}\tTotal: {Tot_time}' )
		return jlist
##===============================   End   ====================================##

def FFZa_Brain ( Ini_file, Meta_dta, verbose=False ) :
	global Vi_Dur	# make it global so we can reuse for fmpeg check ...
	global Tot_Frms
#	global DeBug
#	DeBug = True

	start_time	= datetime.datetime.now()
	message 	= sys._getframe().f_code.co_name + '/:'
	print(f"  {message}\t\tStart: {start_time:%H:%M:%S}" )

	frm_rate = 0

	Prst_all = []
	Au_strms = []
	Vi_strms = []
	Su_strms = []
	Dt_strms = []
	Xt_strms = []

	ff_subtl = []
	ff_audio = []
	ff_video = []

# TODO Parse Format
	try :
		_mtdta = dict(	nb_streams		= int(0),
						duration		= float(0),
						bit_rate		= int(0),
						size 			= float(0) )
		Parse_from_to ( Meta_dta['format'], _mtdta)
		Prst_all.append (_mtdta)
		if 'Pu_la' in _mtdta.values() :
			message += f":O: Meta_dta has Pu_la\n{json.dumps( Meta_dta, indent=2 )}\n{_mtdta }"
			print (message)
			if DeBug : input ('Meta WTF')
			raise ValueError( message )
		_kdat = dict(	codec_type 		=''	)
		for rg in range ( _mtdta['nb_streams'] ) :
			Strm_X = Meta_dta['streams'][ rg ]
			key    = Parse_from_to ( Strm_X, _kdat )
# XXX: Is Video
			if key == 'video' 		:
				_vdata = dict(  index			= int(0),
								codec_name		= '',
								width			= int(0),
								height			= int(0),
								coded_width		= int(0),
								coded_height	= int(0),
								bit_rate 		= int(0),
								avg_frame_rate	= '',
								r_frame_rate	= '')
				Parse_from_to  (Strm_X, _vdata)
				Prst_all.append(_vdata)
				Vi_strms.append(_vdata)	# procces all before building command
# XXX: Is Audio
			elif key == 'audio' 	:
				_adata = dict(	index			= int(0),
								codec_name		='',
								channels		=int(0),
								sample_rate 	=float(0),
								bit_rate		=int(0),
								disposition 	= '',
								tags 			= '')
				Parse_from_to  (Strm_X, _adata)
				Prst_all.append(_adata)
				Au_strms.append(_adata)	# procces all before building command
# XXX: Is subtitle
			elif key == 'subtitle'	:
				_sdata	= dict(	index				= int(0),
								codec_name			= '',
								codec_type			= '',
								duration 			= float(0),
								disposition 		= '',
								tags 				= '' )
				Parse_from_to  (Strm_X, _sdata)
				Prst_all.append(_sdata)
				Su_strms.append(_sdata)
## XXX: Is Data
			elif key == 'data'		:
				_ddata	= dict(	index				= int(0),
								codec_name			= '',
								codec_type			= '',
								duration 			= float(0),
								disposition 		= '',
								tags 				= '' )
				Parse_from_to  (Strm_X, _ddata)
				Prst_all.append(_ddata)
				Dt_strms.append(_ddata)
## XXX: Is attachment
			elif key =='attachment'	:
				_atach	= dict(	index				= int(0),
								codec_name			= '',
								codec_type			= '',
								duration 			= float(0),
								disposition 		= '',
								tags 				= '' )
				Parse_from_to  (Strm_X, _atach)
				Prst_all.append(_atach)
				Xt_strms.append(_atach)
## XXX: Is WTF ?
			else :
				print ("Key:\n",	  json.dumps(key,      indent=2, sort_keys=False))
				print ("Strm_X:\n",	  json.dumps(Strm_X,   indent=2, sort_keys=False))
				print ("Meta_dta:\n", json.dumps(Meta_dta, indent=2, sort_keys=False))
				message += f' Cant Parse Streams WTF? \n{Ini_file}\n'
				print( message )
				input( 'Next ' )
				raise ValueError( message )

# XXX: Check it :)
		if len( Vi_strms ) == 0 :
			message = f'File \n{Ini_file}\n Has no Video => Can\'t convert\n'
			if DeBug : print( message ), input ('Next ?')
			raise ValueError( message )
		if len( Au_strms ) == 0 :
			message = f'File:\n{Ini_file}\n Has no Audio => Can\'t convert\n'
			if DeBug : print( message ), input ('Next ?')
			raise  ValueError( message )

# XXX: Let's print
		mins,  secs = divmod(int(_mtdta['duration']), 60)
		hours, mins = divmod(mins, 60)
		Vi_Dur = f'{hours:02d}:{mins:02d}:{secs:02d}'
		frm_rate = float( Util_str_calc  (_vdata['avg_frame_rate']) )
		Tot_Frms = round( frm_rate * int (_mtdta['duration']) )
		message = f"    |< CT >|{Vi_Dur}| {_vdata['width']:^5}x{_vdata['height']:^5} | {Tot_Frms:>6,} Tfrms| {len(Vi_strms)} Vid| {len(Au_strms)} Aud| {len(Su_strms)} Sub |"
		print (message)

# XXX: Video
		if DeBug : input ("VID !!")
		NB_Vstr = 0
		extra = ''
		for _vid in Vi_strms :
			if DeBug >1 :  print (f'Vid : {NB_Vstr}\n{_vid}' )
			if _vid['codec_name'] == 'mjpeg' :
				continue
			if 'Pu_la' in _vid.values() :
				if DeBug > 1 : print ( json.dumps( _vid, indent=2, sort_keys=False)), input ('ZZ')
				extra = 'has Pu_la'
				if  _vid['bit_rate'] == 'Pu_la':
					if DeBug: print ( _vid.items() ),	time.sleep(1)
					_vid['bit_rate'] = round( _mtdta['bit_rate'] * 0.85 )	# XXX approximation 80% video
				else:
					print ( json.dumps( _vid, indent=2, sort_keys=True ) )
					input("Pu_la is here")
			message = f"    |<V:{_vid['index']:2}>| {_vid['codec_name']:^6} |Br: {HuSa(_vid['bit_rate']):>9}|Fps: {frm_rate:>6}| {extra}"
			print (message)

			zzz = '0:' + str(_vid['index'])
			ff_video.extend( [ '-map', zzz ] )

			if   _vid['height'] > 1090 :	# Scale to 1080p
				ff_video.extend( [ '-vf', 'scale = -1:1080', '-c:v', 'libx265', '-crf', '25', '-preset', 'slow' ] )
			elif _vid['codec_name'] == 'hevc' :
				if _vid['bit_rate'] > Max_v_btr :
					ff_video.extend( [ '-c:v', 'libx265', '-preset', 'slow',   '-b:v', str(Max_v_btr) ])
				else:
					ff_video.extend( [ '-c:v', 'copy'])
			else :
				if   _vid['height'] > 620 :
					ff_video.extend( [ '-c:v', 'libx265', '-crf', '25', '-preset', 'medium' ] )
				elif _vid['height'] > 300 :
					ff_video.extend( [ '-c:v', 'libx265', '-crf', '27', '-preset', 'medium' ] )
				else :
					ff_video.extend( [ '-c:v', 'libx265',                '-preset', 'fast'  ] )
			if frm_rate > Max_frm_rt :
#				ff_video.extend( = [ '-r', '25' ] )
				message = f"    FYI Could conv Frame rate from {frm_rate} to 25"
				print (message)
			NB_Vstr += 1
		if DeBug : message = f"    {ff_video}", print( message )

# XXX: audio
		_disp = dict(	default = int(0),
						dub 	= int(0),
						comment = 0,
						lyrics	= 0,
						karaoke	= 0,
						forced  = int(0),
						hearing_impaired= 0,
						visual_impaired	= 0,
						clean_effects	= 0 )
		if DeBug > 1 : print ( json.dumps( Au_strms, indent=3, sort_keys=False ) )
		if DeBug : input ("AUD !!")
		NB_Astr = 0
		extra = ''
		for _aud in Au_strms :
			if DeBug  > 1 : print ( json.dumps( _aud, indent=3, sort_keys=False ) )
			Parse_from_to ( _aud['disposition'], _disp )
			if 'Pu_la' in _aud.values() :
				if DeBug > 1 : print (json.dumps( _aud, indent=2, sort_keys=False)), input ('ZZ')
				extra = 'has Pu_la'
				if  _aud['bit_rate'] == 'Pu_la':
					if DeBug: print ( _aud.items() ), time.sleep(1)
					_aud['bit_rate'] = round( _mtdta['bit_rate'] * 0.15 / _aud['channels'] )	## XXX:  aproximation
				else:
					pass
			_lng = dict ( language = '' )
			if  _aud['tags'] == 'Pu_la':
				_lng['language'] = 'wtf'
			else:
				Parse_from_to ( _aud['tags'], _lng )
			message = f"    |<A:{_aud['index']:2}>| {_aud['codec_name']:^6} |Br: {HuSa(_aud['bit_rate']):>9}|Fq: {HuSa(_aud['sample_rate']):>5}|Ch: {_aud['channels']}|{_lng['language']}|{_disp['default']}| {extra}"

			zzz = '0:'+ str( _aud['index'] )
			if NB_Astr == 0 :
				ff_audio = [ '-map', zzz ]
			else :
				ff_audio.extend([ '-map', zzz ])

			zzz = '-c:a:' + str( _aud['index'] )
			if  'aac' or 'opus' or 'vorbis' in _aud['codec_name'] :
#			if  _aud['codec_name'] == 'aac' or _aud['codec_name'] == 'opus' or _aud['codec_name'] == 'vorbis' :
				if _aud['bit_rate'] <= Max_a_btr : # and _aud['channels'] < 3 :
					ff_audio.extend( [ zzz, 'copy'] )
				else:
					ff_audio.extend( [ zzz, 'libvorbis', '-q:a', '6'] )
			else :
				ff_audio.extend( [ zzz, 'libvorbis', '-q:a', '7'] )
		if _lng['language'] == 'eng' and _disp['default'] == 1 :
			message += " * Yey *"
		print (message)

		NB_Astr += 1
		if DeBug : message = f"    {ff_audio}", print (message)

#XXX subtitle
		if DeBug : input ("SUB !!")
		NB_Sstr = 0
		if len( Su_strms ) == 0 :
			print ('    |<S:No> Subtitle|' )
			if DeBug : input ('Next ?')
		else:
			extra = ''
			for _sub in Su_strms :
				if DeBug >1 : print (f'Sub : {NB_Sstr}\n{_sub}' )
				if 'Pu_la' in _sub.values() :
					if DeBug > 1 : print ( json.dumps( _sub, indent=2, sort_keys=False)), input ('ZZ')
					extra = 'has Pu_la'

				_lng = dict ( language = '' )
				Parse_from_to ( _sub['tags'], _lng )
				if 'Pu_la' in _lng['language'] :
					_lng['language'] = 'wtf'
				message = f"    |<S:{_sub['index']:2}>|{_sub['codec_name']:^6}|{_sub['codec_type']:^10}|{_lng['language']:3}| {extra}"
	## XXX:
				if 'hdmv_pgs_subtitle' or 'dvd_subtitle' in  _sub['codec_name']:
#				if _sub['codec_name'] == 'hdmv_pgs_subtitle' or _sub['codec_name'] == 'dvd_subtitle' :
					message += f" : Skip : {_sub['codec_name']}"
					print (message)
					if DeBug :
						input ('Next Sub ?')
						continue
				else:
					if 'eng' or 'rum' or 'fre' or 'wtf' in _lng['language'] :
#					if _lng['language'] == 'eng' or _lng['language'] == 'rum' or  _lng['language'] == 'fre' or _lng['language'] == 'wtf':
						print (message)
						zzz = '0:' + str(_sub['index'])
						ff_subtl.extend( ['-map', zzz ])
						zzz = '-c:s:' + str(_sub['index'])
						ff_subtl.extend( [ zzz, 'copy' ] )
					else :
						message += f"Skipo :( {_sub['codec_name']}"
						print ( message )
						if DeBug : input ('Next Sub ?')
				NB_Sstr += 1
	except Exception as e:
		message += f"FFZa_Brain: Exception => {e}\n"
#		message += f":O: Meta_dta:\n{json.dumps( Meta_dta, indent=2 )}\n{_mtdta }"
		print( f"Stack:\n{traceback.print_stack( limit=5 )}\n" )
		if DeBug : print( message ), input ('Next')
		raise  Exception( message )
	else :
		FFM_cmnd = ff_video + ff_audio + ff_subtl

		if  _vid['codec_name'] == 'hevc' and ( 'aac' or 'opus' or 'vorbis' in aud['codec_name'] ) :
			if _vid['bit_rate'] <= Max_v_btr and _vid['height'] <= 1090 and _aud['bit_rate'] <= Max_a_btr :
				message = f"   <|V= {_vid['codec_name']} |A= {_aud['codec_name']}| _Skip_it : Nothing to Do { os.path.basename(Ini_file)}\n"
				print( message )
## XXX: Not the case				raise ValueError( message )

		for pu in Prst_all :
			if 'Pu_la' in pu.values() :
				print ('   <|Had some Pu_la ¯\_(ツ)_/¯')
				break

		if _vid['codec_name'] != 'hevc'  :
				message = f"   <| Vid= {_vid['codec_name']} |Aud= {_aud['codec_name']}| Should Be Converted {Ini_file}\n"
				print( message )
				time.sleep(1)
				raise ValueError( message )

		end_time    = datetime.datetime.now()
		Tot_time	= end_time - start_time
		Tot_time 	= Tot_time.total_seconds()
		print(f'   End  : {end_time:%H:%M:%S}\tTotal: {Tot_time}' )
		return FFM_cmnd
##===============================   End   ====================================##

def FFMpeg_run ( Fmpg_in_file, Za_br_com, Execute= ffmpeg ) :
#	global DeBug
#	DeBug = True
	global Tot_Frms

	start_time	= datetime.datetime.now()
	message 	= sys._getframe().f_code.co_name + '-:'
	print(f"  {message}\t\tStart: {start_time:%H:%M:%S}" )

#XXX FileName for the Title ...
	Sh_fil_name, xt = os.path.splitext( Fmpg_in_file )
	Sh_fil_name   += '.png'

	Fmpg_ou_file  = '__' + Tmp_F_Ext

	Title         = 'title=\" ' +Sh_fil_name + " (x265-aac) Encoded By: " + __author__ + " Master "

	ff_head  = [Execute, '-i', Fmpg_in_file, '-hide_banner' ]
	ff_tail  = [ '-metadata', Title, '-movflags', '+faststart', '-fflags', 'genpts', '-y', Fmpg_ou_file ]

	Cmd      = ff_head + Za_br_com + ff_tail
	'''
	To make multiple screenshots and place them into a single image file (creating tiles), you can use FFmpeg's tile video filter, like this:
https://ffmpeg.org/ffmpeg-filters.html#Examples-129
FFMPEG_CMD="ffmpeg -loglevel panic -i \"$MOVIE\" -y -frames 1 -q:v 1 -vf \"select=not(mod(n\,$NTH_FRAME)),scale=-1:${HEIGHT},tile=${COLS}x${ROWS}\" \"$OUT_FILEPATH\""
# `-loglevel panic` We don’t want to see any output. You can remove this option if you’re having any problem to see what went wrong
# `-i "$MOVIE"` Input file
# `-y` Override any existing output file
# `-frames 1` Tell `ffmpeg` that output from this command is just a single image (one frame).
# `-q:v 3` Output quality where `0` is the best.
# `-vf \"select=` That's where all the magic happens. Selector function for [video filter](https://trac.ffmpeg.org/wiki/FilteringGuide).
# # `not(mod(n\,58))` Select one frame every `58` frames [see the documentation](https://www.ffmpeg.org/ffmpeg-filters.html#Examples-34).
# # `scale=-1:120` Resize to fit `120px` height, width is adjusted automatically to keep correct aspect ration.
# # `tile=${COLS}x${ROWS}` Layout captured frames into this grid

Produce 8x8 PNG tiles of all keyframes (-skip_frame nokey) in a movie:
	ffmpeg -skip_frame nokey -i file.avi -vf 'scale=128:72,tile=8x8' -an -vsync 0 keyframes%03d.png
The -vsync 0 is necessary to prevent ffmpeg from duplicating each output frame to accommodate the originally detected frame rate.

Display 5 pictures in an area of 3x2 frames, with 7 pixels between them, and 2 pixels of initial margin, using mixed flat and named options:
	tile=3x2:nb_frames=5:padding=7:margin=2

	ffmpeg -ss 00:00:10 -i movie.avi -frames 1 -vf "select=not(mod(n\,1000)),scale=320:240,tile=2x3" out.png
	That will seek 10 seconds into the movie, select every 1000th frame, scale it to 320x240 pixels and create 2x3 tiles in the output image out.png, which will look like this:

	-frames 1 -vf "select=not(mod(n\,400)),scale=160:120,tile=4x3" tile.png
	-vf select='gt(scene\,0.4)', scale=160:120, tile -frames:v 1 Yosemite_preview.png
	'-skip_frame', 'nokey', '-vsync', 'vfr',
	zzz   = "select=not(mod(n\,500)), scale=-1:240,  tile=4x4"
	'''

	slice = str( round( Tot_Frms / 16.1 ) ) # We have 16 tiles plus a bit more
	zzz   = "[0:v]select=not(mod(n\," + slice + ")), scale=-1:300, tile=4x4:nb_frames=16:padding=3:margin=3"

	Cmd   = [Execute, '-ss', '00:00:30', '-vsync', 'vfr', '-i', Fmpg_in_file, '-frames', '1', '-vf', zzz , '-y', Sh_fil_name ]
	if DeBug :
		print(f' Len :{b_sec} Div / 4 = {slice} hours = {b_sec/3600}')
		print( zzz )
#		print( Cmd )
		input('OK?')

	loc		= 0
	symbs	= '|/-+\\'
	try :
		if DeBug :
			print ("    |>-:", Cmd )
			input ("Ready to Do it? ")
			ff_out = subprocess.run( Cmd,
				universal_newlines=True,
				encoding='utf-8' )
			errcode  = ff_out.returncode
			if errcode :
				message += f" ErRor: ErRorde {errcode}"
				print( message )
				input('Next')
				raise Exception( '$hit ', message )
			input("Are we Done?")
			return Fmpg_ou_file
		else :
			print ("    |>-:", Cmd[9:-2] )	## XXX:  Skip First 4 and Last 6
			ff_out = subprocess.Popen( Cmd,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				universal_newlines=True,
				encoding='utf-8' )
	except subprocess.CalledProcessError as err:
		ff_out.kill()
		message += f" ErRor: {err} CalledProcessError :"
		if DeBug : print( message ) , input('Next')
		raise Exception( '$hit ', message )
	except Exception as e:
		ff_out.kill()
		message += f" ErRor: Exception {e}:"
		if DeBug : print( message ) , input('Next')
		raise Exception( '$hit ', message )
	else:
		while ff_out.poll() is None:
			lineo    = ff_out.stdout.readline()
			if DeBug : print(f"<{lineo}>")
			errcode  = ff_out.returncode
			stderri  = ff_out.stderr
			if errcode or stderri :
				message += f" ErRor: ErRorde {errcode} stderr {stderri}:"
				print( message )
				raise ValueError ( '$hit ', message )
			elif 'frame=' in lineo :
				Prog_cal ('', symbs[loc]) # XXX: Keep it
				loc += 1
				if loc == len(symbs) :
					loc = 0
			elif 'global headers:' and "muxing overhead:" in lineo :
				print(f'\n|>+<| {lineo}' )
	end_time    = datetime.datetime.now()
	Tot_time	= end_time - start_time
	Tot_time 	= Tot_time.total_seconds()
	print(f'   End  : {end_time:%H:%M:%S}\tTotal: {Tot_time}' )
	message +="   FFMpeg Done !!"
	print ( message )
	return Fmpg_ou_file
##===============================   End   ====================================##

def Prog_cal ( line_to, sy=False ) :
#	global DeBug
#	DeBug = True
	global Vi_Dur
	message  = sys._getframe().f_code.co_name + '-:'

	_P =''
	if DeBug : print ("\r", line_to, sy), input(message)
	if not line_to and sy :
		sy = f"\r    | {sy} |Working:"
		sys.stderr.write( sy )
		sys.stderr.flush
	elif 'frame=' and 'bitrate=' and not 'N/A' in line_to :
		try :
			fr	= re.search( r'frame=\s*([0-9]+)',		line_to ).group(1)
			fp	= re.search( r'fps=\s*([0-9]+)',		line_to ).group(1)
			sz	= re.search( r'size=\s*([0-9]+)',		line_to ).group(1)
			tm	= re.search( r'time=\S([0-9:]+)',		line_to ).group(1)
			br	= re.search( r'bitrate=\s*([0-9\.]+)',	line_to ).group(1)	#Can have value of N/A
			sp	= re.search( r'speed=\s*([0-9\.]+)',	line_to ).group(1)	#Can have value of N/A
			if int(fp) > 0 :
				a_sec = sum( int(x)*60**i for i, x in enumerate( reversed( tm.split(":"))) )
				b_sec = sum( int(x)*60**i for i, x in enumerate( reversed( Vi_Dur.split(":"))) )
				dif   = abs( b_sec - a_sec )
				eta  = round( dif / (float(sp) ))
				mins, secs  = divmod(int(eta), 60)
				hours, mins = divmod( mins, 60)
				_Dur = f'{hours:02d}:{mins:02d}:{secs:02d}'
				_P   = f'\r    | {sy} |Frame: {fr}|Fps: {fp}|Siz: {sz}|BitRate : {br}|Speed: {sp}|Time Left: {_Dur}| '

		except Exception as e:
			print (line_to)
			message += f" ErRor: in Procesing data {e}:"
			raise  Exception( message )
		else:
			sys.stderr.write( _P )
			sys.stderr.flush
	else :
		_P = '\r' + line_to
		sys.stderr.write( _P )
		sys.stderr.flush
	return True
##>>============-------------------<  End  >------------------==============<<##

if __name__=='__main__':
#	global DeBug
#	DeBug = False

	cgitb.enable(format='text')

	message = __file__ +'-:'
	print( message )

	start_time = datetime.datetime.now()
	print(f' Start: {start_time:%H:%M:%S}')

	sys.stdout 		= Tee( sys.stdout,	open( Log_File,   'w', encoding="utf-8" ) )
	Exeptions_File 	= 					open( Bad_Files,  'w', encoding="utf-8" )
	Succesful_File 	= 					open( Good_Files, 'w', encoding="utf-8" )

	if not Resource_Check( Folder ) :
		print ("Aborting Not Enough resources")
		exit()

#XXX  |[0] Extension |[1] Full Path |[2] File Size |[3] File Info |[4] Year Made Sort = True => Largest First XXX
	Qlist_of_Files  = Build_List( Folder, VIDEO_EXTENSIONS, Sort_loc=2, Sort_ord=False  )
	if DeBug > 2 :  print (Qlist_of_Files), input ("Next :")

	QExeption_ = Do_it( Qlist_of_Files )
	if DeBug or True :
		for filedesc in QExeption_ :
			print (filedesc.replace('\n',''))
		print ("Total files :", len (QExeption_) )

	Exeptions_File.close()
	Succesful_File.close()
	sys.stdout.flush()

	end_time = datetime.datetime.now()
	print(f' \tEnd  : {end_time:%H:%M:%S}\tTotal: {end_time-start_time}')
	input('All Done')
	exit()
##>>============-------------------<  End  >------------------==============<<##
