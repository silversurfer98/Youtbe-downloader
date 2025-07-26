from yt_dlp import YoutubeDL as ytd
import sys
import click
import os
from dotenv import load_dotenv
load_dotenv()

class AppData():
    def __init__(self):
        self.resolution = ""
        self.url = ""
        self.download_loc = ""
    def set_resolution(self, resolution):
        resol = ""
        match resolution:
            case "2k":
                resol = "2560x1440"
            case "4k":
                resol = "3840x2160"
            case _:
                resol = os.environ.get("DEFAULT_RESOLUTION")
        self.resolution = resol
    def get_resolution(self):
        return self.resolution
    def set_url(self, url):
        self.url = url
    def get_url(self):
        return self.url
    def set_download_loc(self, download_loc):
        self.download_loc = download_loc
    def get_download_loc(self):
        return self.download_loc

appdata = AppData()

def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """
    resolution = appdata.get_resolution()
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

@click.command()
@click.argument("url")
@click.option("--resolution", "-r", type=str, default=os.environ.get("DEFAULT_RESOLUTION"), help="Select resolution [2k or 4k]", show_default=True)
@click.option("--download_directory", "-d", type=str, default=os.environ.get("DEFAULT_DOWNLOAD_LOCATION"), help=f"Specify download directory.", show_default=True)
def download(url: str, resolution: str, download_directory: str) -> None:
    """
    A program to download YouTube videos at specified resolution
    
    [url] is the YpuTube URL to download
    """
    appdata.set_resolution(resolution=resolution)
    appdata.set_url(url=url)
    appdata.set_download_loc(download_loc=download_directory)
    print(appdata.get_url())
    print(appdata.get_resolution())
    print(appdata.get_download_loc())
    ydl_opts = {
        'format': format_selector,
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
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
        'paths': {
            'home': f"{appdata.get_download_loc()}",  # Main download directory
            'subtitle': f"{appdata.get_download_loc()}",  # Optional: separate subtitle directory
        },
    }
    with ytd(ydl_opts) as ydl:
        ydl.download(appdata.get_url())

if __name__ == "__main__":
    download()
