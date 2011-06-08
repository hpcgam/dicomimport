# -*- coding: utf-8 -*-
# модуль конвертации файла растрововой графики в dicom файл
import os, sys, getopt
import glob
import subprocess
import logging
import dicom

#def ConvertAndUpload(filename,dic,logging,cfg):
def ConvertAndUpload(filename,dic,cfg,aSeriesDescription):
	
    #filenamedcm=cfg.workdir+filename+".dcm" #test for russian language!
	filenamedcm=filename+".dcm" #test for russian language!

	logging.info('\nConvertAndUpload, begin processing: '+filename )

    # gdcmimg для обработки джпег 2к.
	cstr="./bin/gdcmimg -V "+filename+" "+filenamedcm
    #cstr="./gdcmimg -V --depth 8 "+filename+" "+filenamedcm

	if Run([cstr]):
		logging.error("Conversion gdcmimg:"+filename+" failed. The reason above.")
		return False, '','',''
	else:
		logging.info("Coversion gdcmimg:"+filename+"  OK.") 

	ds=dicom.read_file(filenamedcm)
  
	if not dic['SeriesStudy']:                                                    #if(len(dic['SeriesStudy']) < 1):
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
	#ds.PhotometricInterpretation='RGB' #dirty hack for 07 server . wtf???
	
	################## new {
	ds.ConversionType='SI'
	ds.PlanarConfiguration=0
	#ds.InstanceNumber=? #ISномер экземпляра в исследовании?
	#ds.SeriesNumber=? #IS
	
	#ds.StudyID=''
	#ds.AccessionNumber=""
	#ds.StudyDate=''
	#ds.StudyTime=''
#ds
#(0008, 0012) Instance Creation Date              DA: '20110602'
#(0008, 0013) Instance Creation Time              TM: '223731.240'
#(0008, 0016) SOP Class UID                       UI: Secondary Capture Image Storage
#(0008, 0018) SOP Instance UID                    UI: 2.25.4598006894618118916315644979812889192
#(0008, 0020) Study Date                          DA: ''
#(0008, 0030) Study Time                          TM: ''
#(0008, 0050) Accession Number                    SH: ''
#(0008, 0060) Modality                            CS: 'OT'
#(0008, 0064) Conversion Type                     CS: 'SI'
#(0008, 0070) Manufacturer                        LO: ''
#(0008, 0090) Referring Physician's Name          PN: ''
#(0010, 0010) Patient's Name                      PN: ''
#(0010, 0020) Patient ID                          LO: ''
#(0010, 0030) Patient's Birth Date                DA: ''
#(0010, 0040) Patient's Sex                       CS: ''
#(0020, 000d) Study Instance UID                  UI: 2.25.11053659306578739178687942968366309583
#(0020, 000e) Series Instance UID                 UI: 2.25.221574020101481450611152833196732210792
#(0020, 0010) Study ID                            SH: ''
#(0020, 0011) Series Number                       IS: '1'
#(0020, 0013) Instance Number                     IS: '1'
#(0028, 0002) Samples per Pixel                   US: 3
#(0028, 0004) Photometric Interpretation          CS: 'YBR_FULL_422'
#(0028, 0006) Planar Configuration                US: 0
#(0028, 0010) Rows                                US: 585
#(0028, 0011) Columns                             US: 432
#(0028, 0100) Bits Allocated                      US: 8
#(0028, 0101) Bits Stored                         US: 8
#(0028, 0102) High Bit                            US: 7
#(0028, 0103) Pixel Representation                US: 0
#(7fe0, 0010) Pixel Data                          OB: Array of 45266 bytes

	
	################# new }
	try:
		ds.SaveAs(filenamedcm)
	except:
		logging.error("canot save dcm file")
		return False, '','',''

##############################################################################
## пробуем разместить полученный файл в хранилище
	cstr="./bin/storescu  --propose-jpeg8 -aec "+ cfg.dcmaetitle +" "+\
    " "+cfg.dcmhost+" "+ cfg.dcmport +" "+filenamedcm

    #print 'DBG cstr',cstr
	
	if Run([cstr]):
		logging.error("Storage "+str(filenamedcm)+" failed. The reason above.")
		return False, '','',''
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
