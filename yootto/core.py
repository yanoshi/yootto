"""
yootto is tiny YouTube Music unofficial uploader.
"""

import logging
import fire
import json
import time
import sys, os
import glob
import requests
import datetime
import platform
import urllib.parse
import functools

from pathlib import Path
from tqdm import tqdm
from ytmusicapi import YTMusic
from tinytag import TinyTag

TARGET_EXT = ["*.flac", "*.m4a", "*.mp3", "*.ogg", "*.wma"]


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_conf(conf_path):
  dummy_conf = {
    "auth_file_path": "headers_auth.json",
    "online_catalog_cache_file_path": "cache.json",
    "auto_create_playlist_format": "Upload List (%Y/%m/%d %H:%M:%S)"
  }

  conf = object()

  if conf_path == "" or not os.path.exists(conf_path):
    conf = dummy_conf

    conf_path = os.path.expanduser("~/.yootto/config.json")
    os.makedirs(os.path.dirname(conf_path), exist_ok = True)
    try:
      with open(conf_path, "w") as f:
        json.dump(dummy_conf, f)
    except:
      pass
  else:
    try:
      with open(conf_path, "r") as f:
        conf = json.load(f)
    except json.JSONDecodeError as e:
      logging.FATAL("JSONDecodeError: ", e)
      return dummy_conf

  basedir = os.path.dirname( os.path.abspath(conf_path) )
  if not Path(conf["auth_file_path"]).is_absolute():
    conf["auth_file_path"] = os.path.join(basedir, conf["auth_file_path"])
  if not Path(conf["online_catalog_cache_file_path"]).is_absolute():
    conf["online_catalog_cache_file_path"] = os.path.join(basedir, conf["online_catalog_cache_file_path"])
    
  return conf


def load_online_cache(cache_path):
  if not os.path.exists(cache_path):
    return []
  try:
    with open(cache_path, "r") as f:
      cache = json.load(f)
      return cache
  except json.JSONDecodeError as e:
    logging.warning("JSONDecodeError: %s", e)
    return []  


def store_online_cache(cache_path, cache):
  try:
    with open(cache_path, "w") as f:
      json.dump(cache, f)
      return "Stored cache: {f} | {cnt} songs".format(f = cache_path, cnt = len(cache))
  except:
    return "Error in store cache"


def compare_online_to_file(cache, tag):
  title = cache["title"]
  if title is None:
    title = ""

  artist = cache["artists"]
  if artist is None:
    artist = [{ "name": "" }]

  if title == tag.title:
    for art in artist:
      if art["name"] == tag.artist:
        return True
  elif title == tag.filename:
    return True

  return False


def get_tag_from_file(path):
  obj = TinyTag.get(path)
  obj.filename = os.path.basename(path)
  obj.filepath = os.path.abspath(path)
  return obj


def load_playlist(playlist_path, encoding):
  ret = []
  try:
    fileobj = open(playlist_path, "r", encoding=encoding)
    while True:
      line = fileobj.readline().replace("\n", "")
      if line and line[0] != "#" and ord(line[0]) != 65279:
        if not Path(line).is_absolute():
          if platform.system() == "Windows":
            line = line.replace("/", "\\")
          else:
            line = line.replace("\\", "/")
          basedir = os.path.dirname( os.path.abspath(playlist_path) )
          line = os.path.join(basedir, line)
        ret.append(get_tag_from_file(line))
      if line:
        pass
      else:
        break
  except:
    logging.FATAL("Playlist load error.")
    return []

  return ret


def get_music_file(path):
  abs_path = os.path.abspath(path)
  files = []

  if os.path.isdir(abs_path):
    for ext in TARGET_EXT:
      search_str = os.path.join("**", ext)
      files.extend(glob.glob(os.path.join(abs_path, search_str), recursive=True))
  else:
    files = [abs_path]
  
  return files



class Upload(object):
  """
  Upload audio file or playlist file.
  """

  def __init__(self, conf = ""):
    """
    :param conf: Config file path
    """
    self.conf = load_conf(conf)


  def music(self, path = "./", disable_create_playlist = False):
    """
    Upload audio file.

    :param path: A audio file path or directory path including audio files. (default value: "./")
    :param disable_create_playlist: Disable auto create playlist function.
    """
    ytmusic = object()

    try:
      s = requests.Session()
      s.request = functools.partial(s.request, timeout=120)
      ytmusic = YTMusic(self.conf["auth_file_path"], requests_session=s)
    except Exception as identifier:
      return "Can not connect YouTube Music API: {}".format(identifier)
    
    files = get_music_file(path)

    print("{} files found".format(len(files)))
    print("Start upload...")

    success_cnt, conflict_cnt, error_cnt = 0, 0, 0
    tags = list()
    for f in tqdm(files):
      try:
        while True:
          ret = ytmusic.upload_song(f)
          if type(ret) is requests.models.Response and ret.status_code == 409:
            print("Conflicted upload {}".format(f))
            conflict_cnt += 1
          elif type(ret) is requests.models.Response and ret.status_code == 503:
            print("YouTube Music say 503...Susspending 15 sec...")
            time.sleep(15)
            continue
          elif type(ret) is str and ret == "STATUS_SUCCEEDED":
            tags.append(get_tag_from_file(f))
            success_cnt += 1
          else:
            print("Error upload {f} / {err}".format(f = f, err = ret))
            error_cnt += 1
          break
      except Exception as e:
        print("Error upload {}: {}".format(f, e))
        error_cnt += 1
        return "success: {suc} / fail: {err}".format(suc = success_cnt, err = error_cnt)

    all_len = len(tags)
    processed_cnt = 0
    retry_cnt = 0
    cache = load_online_cache(self.conf["online_catalog_cache_file_path"])

    while len(tags) > processed_cnt:
      print("waiting... ({n}/{all})".format(n = processed_cnt, all = len(tags)))
      time.sleep(10)
      songs = ytmusic.get_library_upload_songs(all_len, "recently_added")
      last_cnt = processed_cnt

      for s in songs:
        for t in tags:
          if hasattr(t, "video_id"):
            continue
          if not compare_online_to_file(s, t):
            continue
          
          t.video_id = s["videoId"]
          try:
            cache.append(s)
            songs.remove(s)
          except Exception as identifier:
            logger.error("Upload error: %s", identifier)
            logger.error("Failed proccesing song: %s", s)
          processed_cnt += 1
      
      if last_cnt == processed_cnt:
        retry_cnt += 1
      else:
        retry_cnt = 0

      if retry_cnt > 30:
        logger.error("Can not get meta data. Unprocessed data: %s", songs)
        break

    print(store_online_cache(self.conf["online_catalog_cache_file_path"], cache))
    
    if not disable_create_playlist and len(tags) != 0:
      video_ids = list()
      for t in tags:
        if hasattr(t, "video_id"):
          video_ids.append(t.video_id)

      if len(video_ids) > 0:
        title = datetime.datetime.now().strftime(self.conf["auto_create_playlist_format"])
        res = ytmusic.create_playlist(
          title, 
          "Auto created by yootto",
          "PRIVATE",
          video_ids)
        
        if type(res) is str:
          print("Playlist created: {}".format(title))
        
    return "success: {suc} / fail: {err}".format(suc = success_cnt, err = error_cnt)


  def playlist(self, title, path, description = "Created by yootto", encoding = "utf_8", enable_reload_online_cache = False):
    """
    Upload playlist file(.m3u, .m3u8).

    :param title: Playlist title
    :param path: A playlist file path
    :param description: Playlist description (default value: "Created by yootto")
    :param encoding: Charactor encoding using in playlist file (default value: "utf_8")
    :param enable_reload_online_cache: Reload songs catalog from YouTube Music.
    """

    ytmusic = object()

    try:
      ytmusic = YTMusic(self.conf["auth_file_path"])
    except Exception as identifier:
      return "Can not connect YouTube Music API: {}".format(identifier)

    cache = []
    if enable_reload_online_cache:
      try:
        cache = ytmusic.get_library_upload_songs(100000)
        print(store_online_cache(self.conf["online_catalog_cache_file_path"], cache))
      except Exception as identifier:
        return "Error: {}".format(identifier)
    else:
      cache = load_online_cache(self.conf["online_catalog_cache_file_path"])

    playlist = load_playlist(path, encoding)
    if len(playlist) == 0:
      return "Can not read playlist or playlist dose not have tracks."

    print("Creating...")
    for s in cache:
      for p in playlist:
        if not compare_online_to_file(s, p):
          continue
        p.video_id = s["videoId"]

    video_ids = []
    for p in playlist:
      if not hasattr(p, 'video_id') or p.video_id is None:
        print("Error: '{}' is not found in YouTube Music or local cache".format(p.filename))
        continue
      video_ids.append(p.video_id)
    
    res = ytmusic.create_playlist(
      title, 
      description,
      "PRIVATE",
      video_ids)
    if type(res) is str:
      return "Playlist created: {}".format(title)
      
    return "Failed: {}".format(res)


class Download(object):
  """
  Downalod playlist file.
  """

  def __init__(self, conf = ""):
    """
    :param conf: Config file path
    """
    self.conf = load_conf(conf)

  def playlist(self, url, music_path, output_path, encoding = "utf_8"):
    """
    Download playlist (output to m3u8 playlist file)

    :param url: Playlist url(ex: https://music.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxx)
    :param music_path: A music folder path(ex: /music/dir/path/)
    :param output_path: Output playlist file path(ex: hogehoge.m3u8)
    :param encoding: Charactor encoding using in playlist file (default value: "utf_8")
    """

    ytmusic = object()

    try:
      ytmusic = YTMusic(self.conf["auth_file_path"])
    except Exception as identifier:
      return "Can not connect YouTube Music API: {}".format(identifier)

    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "list" not in query:
      return "Can not parse url"
    
    songs = ytmusic.get_playlist(query["list"][0], 2**31-1)["tracks"]
    files = get_music_file(music_path)

    print("Scan files...")
    tags = {}
    for f in tqdm(files):
      try:
        t = get_tag_from_file(f)

        artist = "-"
        if t.artist != "":
          artist = t.artist

        album = "-"
        if t.album != "":
          album = t.album

        title = t.filename
        if t.title != "":
          title = t.title

        if artist not in tags:
          tags[artist] = {}
        if album not in tags[artist]:
          tags[artist][album] = {}
        
        if title in tags[artist][album] and tags[artist][album][title].duration > t.duration:
          continue

        tags[artist][album][title] = t

      except:
        print("Error get music tag: {}".format(f))

    print("Write playlist...")
    try:
      fstr = open(output_path, 'w', encoding=encoding)
      
      for s in tqdm(songs):
        artist = "-"
        if "artists" in s and len(s["artists"]) > 0:
          artist = s["artists"][0]["name"]
        
        album = "-"
        if "album" in s and s["album"] != None:
          album = s["album"]["name"]
        
        title = "-"
        if "title" in s and s["title"] != None:
          title = s["title"]

        if artist in tags and album in tags[artist] and title in tags[artist][album]:
          fstr.write(tags[artist][album][title].filepath + "\n")
        else:
          print("Cannot find: {at} / {al} / {tl}".format(at=artist, al=album, tl=title))
      
      fstr.close()
    except:
      return "Cannot write playlist file..."
        
    return "Success: {}".format(output_path)

class Pipeline(object):
  def __init__(self):
    self.upload = Upload()
    self.download = Download()


  def auth(self, header_raw = "", conf = ""):
    """
    Create auth file.

    :param header_raw: If you don't want interactive interface, please set this.
    :param conf: Config file path
    """

    conf_data = load_conf(conf)

    if header_raw != "":
      YTMusic.setup(filepath = conf_data["auth_file_path"], header_raw = header_raw)
    else:
      print("How to get request header -> https://ytmusicapi.readthedocs.io/en/latest/setup.html#authenticated-requests")
      YTMusic.setup(filepath = conf_data["auth_file_path"])

    return "{path} is saved.".format(path = conf_data["auth_file_path"])


  def caching(self, conf = ""):
    """
    Load songs catalog from YouTube Music.

    :param conf: Config file path
    """

    conf_data = load_conf(conf)

    result = []
    print("Start downloading song list...")

    try:
      s = requests.Session()
      s.request = functools.partial(s.request, timeout=7200)
      ytmusic = YTMusic(auth=conf_data["auth_file_path"], requests_session=s)
      result = ytmusic.get_library_upload_songs(100000)
    except Exception as identifier:
      return "Error: {}".format(identifier)

    if len(result) == 0:
      return "Song is not found"
    
    return store_online_cache(conf_data["online_catalog_cache_file_path"], result)




def main():
  fire.Fire(Pipeline)




if __name__ == "__main__":
  main()
