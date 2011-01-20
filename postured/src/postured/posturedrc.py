import datetime
import os
import postured

# TODO: Ideally this should be moved out to postured.py
class PlaySound():
    def __init__(self, filename=None):
        self.filename = filename

    def run(self):
        self.playsound()

    def playsound(self):
        import wave
        import ossaudiodev

        if self.filename:
            sound = wave.open(filename, 'rb')
        else:
            sound = wave.open(os.path.join(postured.sounds_path, 'bell17.wav'), 'rb')

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

class Options(object):
    #minlength = datetime.time(minute=30)
    minlength = datetime.timedelta(minutes=30)
    #maxlength = datetime.time(hour=2)
    #maxlength = datetime.timedelta(minutes=30)
    maxlength = datetime.timedelta(hours=2)

    starttime = datetime.time(hour=9)  # 11 am
    endtime = datetime.time(hour=11)    # 7 pm

    # days of the week (monday is 0 and sunday is 6)
    days = [0, 1, 2, 3, 4]              # M, Tu, W, Th, F 

    action = PlaySound()


opts = Options()

