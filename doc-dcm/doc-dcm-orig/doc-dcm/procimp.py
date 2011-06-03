# -*- coding: utf-8 -*-
# модуль конвертации файла растрововой графики в dicom файл
import os, sys, getopt
import glob
import subprocess
import logging
import dicom

#def ConvertAndUpload(filename,dic,logging,cfg):
def ConvertAndUpload(filename,dic,cfg,aSeriesDescription):
	
	emptyv=('','','','')
    #filenamedcm=cfg.workdir+filename+".dcm" #test for russian language!
	filenamedcm=cfg.workdir+os.path.basename(filename)+".dcm" #test for russian language!
	logging.info('\nConvertAndUpload, begin processing: '+filename )

    # gdcmimg для обработки джпег 2к.
	cstr="./bin/gdcmimg -V "+filename+" "+filenamedcm
    #cstr="./gdcmimg -V --depth 8 "+filename+" "+filenamedcm

	if Run([cstr]):
		logging.error("Conversion gdcmimg:"+filename+" failed. The reason above.")
		return False, emptyv
	else:
		logging.info("Coversion gdcmimg:"+filename+"  OK.") 

	ds=dicom.read_file(filenamedcm)
  
	if not dic['SeriesStudy']:
                                                    #if(len(dic['SeriesStudy']) < 1):
		dic['SeriesStudy']=ds.SeriesInstanceUID+'0'
    
                                                    #ds.SeriesInstanceUID=StydiesSer+ds.SeriesInstanceUID[ds.SeriesInstanceUID.rfind('.'):]
    
    # для группировки по исследованию
	ds.SeriesDate=ds.StudyDate=dic['DateCreationStudy']
	ds.StudyInstanceUID=dic['SeriesStudy'] #StudyInstanceUID должно быть одинаковым для всей серии иссл.
    
    #tmpstr='%s %s %s' %(dic['pat_ln'],dic['pat_fn'],dic['pat_mn'])
    #ds.PatientsName=tmpstr.encode('ISO_IR 144')
    
	ds.PatientsName=dic['pat_fio'].encode('ISO_IR 144')
	ds.PatientID=dic['pat_reg'].encode('ISO_IR 144')
	
	ds.StudyDescription = aSeriesDescription.encode('ISO_IR 144')
	
	ds.SpecificCharacterSet='ISO_IR 144'
	ds.InstitutionName='IOOD'
	ds.Modality=dic['Modality'].encode('ISO_IR 144')
	ds.PatientsBirthDate=dic['pat_bdate'].encode('ISO_IR 144')
	ds.InstanceCreationDate=dic['DateCreationStudy']  #??
	ds.StationName=dic['usr_comp'].encode('ISO_IR 144')
	ds.OperatorsName=dic['pat_login'].encode('ISO_IR 144')
	ds.AcquisitionDate=dic['DateImportStudy']
	ds.PhotometricInterpretation='RGB' #dirty hack for 07 server . wtf???
	ds.SaveAs(filenamedcm)

##############################################################################
# для загрузки джпег2к использовать перебор параметров стореску j2klossy,j2klossless если все попытки не удались - значит ошибка загрузки на дайкомсервер

  ## пробуем разместить полученный файл в хранилище
	cstr="./bin/storescu  --propose-jpeg8 -aec "+ cfg.dcmaetitle +" "+\
    " "+cfg.dcmhost+" "+ cfg.dcmport +" "+filenamedcm

    #print 'DBG cstr',cstr

	if Run([cstr]):
		logging.error("Storage "+str(filenamedcm)+" failed. The reason above.")
		return False, emptyv
	else:
		logging.info(filenamedcm+" Stored OK.")

	try:
		os.remove(filenamedcm)
		os.remove(filename)
		pass
	except IOError, err:
		logging.error("Error delete file:"+filenamedcm)
		pass
        #return False,stydiesser
        #print "cannot delete exsist dicom file, quit"
        #sys.exit(-2) #!
###################################################################################
  
    #all ok
	# нужно ли проверять: ds.StudyInstanceUID+' ' +ds.SeriesInstanceUID+' '+ds.SOPInstanceUID ?
	#logging.debug("3 uids:"+ds.StudyInstanceUID+' ' +ds.SeriesInstanceUID+' '+ds.SOPInstanceUID)
	return True, str(ds.StudyInstanceUID), str(ds.SeriesInstanceUID), str(ds.SOPInstanceUID)

  
""" old comment
функция конвертирует вх.джпег файл в дайком посредством программы gdcmimg
вх.параметр - наименование джпег файла, выходящий - успешное выполнение операции конвертирования (0) или при неудаче - код ошибки  
ловятся ошибки отсутствия конвертера, отстутствия входного файла, битый входной файл
для джпег файлов синтаксис вызова: gdcmimg infile.jpg outfile.dcm 
в полученном дайком-файле заполняются поля:
    """	
def Run(cmd):	
    p = subprocess.Popen(\
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
	env={"DCMDICTPATH": "./bin/dicom.dic"} )
    (stdout, stderr) = p.communicate()
    rv = p.returncode
    if (rv <> 0):
        logging.debug("module Run,  RETURN CODE: %s" % str(rv))
        #raise Exception, "execute failed with error output:\n%s" % stderr
        if (len(stdout.strip()) > 0):
            logging.debug("module Run,  STDOUT:\n%s" % stdout)
        if (len(stderr.strip()) > 0):
            logging.debug("module Run,  STDERR:\n%s" % stderr)
        return rv
