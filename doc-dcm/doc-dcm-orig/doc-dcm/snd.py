from wave import open as waveOpen
from ossaudiodev import open as ossOpen

import threading

class MyThread(threading.Thread):

    def __init__(self,an):
      threading.Thread.__init__(self)
      self.aFile=an

    def run(self):
      try:        s = waveOpen(self.aFile,'rb')
      except:     return
    
      (nc,sw,fr,nf,comptype, compname) = s.getparams( )
      try:
        dsp = ossOpen('/dev/dsp','w')
      except:
        return
    
      try:
        from ossaudiodev import AFMT_S16_NE
      except ImportError:
        if byteorder == "little":
          AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
        else:
          AFMT_S16_NE = ossaudiodev.AFMT_S16_BE
      dsp.setparameters(AFMT_S16_NE, nc, fr)
      data = s.readframes(nf)
      s.close()
      dsp.write(data)
      dsp.close()

#   MyThread().start()

def psound(aFile):
  s=MyThread(aFile)
  s.start()
  
  '''
  try:
    s = waveOpen(aFile,'rb')
  except:
    return

  (nc,sw,fr,nf,comptype, compname) = s.getparams( )
  try:
    dsp = ossOpen('/dev/dsp','w')
  except:
    return

  try:
    from ossaudiodev import AFMT_S16_NE
  except ImportError:
    if byteorder == "little":
      AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
    else:
      AFMT_S16_NE = ossaudiodev.AFMT_S16_BE
  dsp.setparameters(AFMT_S16_NE, nc, fr)
  data = s.readframes(nf)
  s.close()
  dsp.write(data)
  dsp.close()
'''

#import threading
#class MyThread(threading.Thread):
#    def run(self):
#        print 'You called my start method, yeah.'
#        print 'Were you expecting something amazing?'
# MyThread().start()
