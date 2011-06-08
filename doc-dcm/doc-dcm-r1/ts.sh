export DCMDICTPATH="/home/user/work/endograb/bin/dicom.dic"
echo ddd=
echo $DCMDICTPATH
./bin/storescu  --propose-jpeg8 -aec DCM4CHEE localhost 11112 tt.jpg.dcm 