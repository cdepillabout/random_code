import os
import wave
import ossaudiodev
#from . import sounds_path
import postured

class PlaySound():
    def __init__(self, filename=None):
        self.filename = filename

    def run(self):
        self.playsound()

    def playsound(self):

        if self.filename:
            sound = wave.open(filename, 'rb')
        else:
            sound = wave.open(os.path.join(postured.soundspath, 'bell17.wav'), 'rb')

        nchannels , sampwidth, framerate, nframes, comptype, compname = sound.getparams()
        print("params for %s:" % sound)
        print("\tnchannels (number of audio channels) = %s, sampwidth = %s, " % 
                (nchannels, sampwidth))
        print("\tframerate (sampling frequency) = %s, nframes (# of audio frames) = %s, " % 
                (framerate, nframes))
        print("\tcomptype (compression type) = %s, compname (compression name) = %s" % 
                (comptype, compname))

        dsp = ossaudiodev.open('/dev/dsp','w')

        try:
            from ossaudiodev import AFMT_S16_NE
        except ImportError:
            # assume little endian
            AFMT_S16_NE = ossaudiodev.AFMT_S16_LE

        dsp.setparameters(AFMT_S16_NE, nchannels, framerate)
        data = sound.readframes(nframes)
        sound.close()
        dsp.write(data)
        dsp.close()
