# -*- coding: utf-8 -*-
import tempfile
import os
import shutil

class TmpFile:
	directory = None
	
	@staticmethod
	def create( suffix='' ):
		if not TmpFile.directory or not os.path.exists( TmpFile.directory ):
			TmpFile.directory = tempfile.mkdtemp()
		fd, name = tempfile.mkstemp( suffix=suffix, dir=TmpFile.directory )
		os.close(fd)
		return name

	# Removes all temporary files (and the temporary directory)
	@staticmethod
	def clearAll():
		if TmpFile.directory:
			try:
				shutil.rmtree( TmpFile.directory )
			except: pass

	# brief Remove the given file
	@staticmethod
	def remove(path):
		try:
			os.unlink(path)
		except: pass

