from yt_dlp import YoutubeDL as ytd
import sys
URL = []
resolution = "1920x1080"

def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """
    global resolution
    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    try:
        print(resolution)
        best_video = next(f for f in formats
                        # if (f['vcodec'] != 'none' and f['acodec'] == 'none' and f['resolution'] == '1920x1080'))
                        if (f['vcodec'] != 'none' and f['acodec'] == 'none' and f['resolution'] == resolution))
    except:
        print("cannot find this resolution : ", resolution, " \n")
        best_video = next(f for f in formats
                        if (f['vcodec'] != 'none' and f['acodec'] == 'none'))


    
    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]

    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print(d['filename']," done, post processing in progress .......")


def custom_prepare_outtmpl(self, outtmpl, info_dict, sanitize=False):
    outtmpl = "%(playlist_index)s - %(title)s.%(ext)s"
    #outtmpl = '%(playlist_index|)s%(playlist_index& - |)s%(title)s.%(ext)s'

ydl_opts = {
    'format': format_selector,
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    #'prepare_outtmpl': custom_prepare_outtmpl,
    'restrictfilenames': False,
    #'subtitleslangs': "en",
    'writeautomaticsub': True,
    'writesubtitles': True,
    #'listsubtitles': True,
    'writedescription': False,
    'clean_infojson': False,
    'writeinfojson': False,
    'windowsfilenames': True,
    'outtmpl' : "%(playlist_index|)s%(playlist_index& - |)s%(title)s.%(ext)s",
    # 'playlist_items' : "37:58",
}

def main(argv):
    # print ('Number of arguments:', len(argv), 'arguments.')
    # print ('Argument List:', str(argv))
    global resolution
    try:
        if(argv[1]=="4k"):
            resolution = "3840x2160"
        elif(argv[1]=="2k"):
            resolution = "2560x1440"
    except:
        with ytd(ydl_opts) as ydl:
            ydl.download(argv[0])

if __name__ == "__main__":
   main(sys.argv[1:])