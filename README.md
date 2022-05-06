# yootto
yootto(ヨーッと) is tiny YouTube Music unofficial uploader.

Japanese document: [README.ja.md](README.ja.md)

## Features

- Upload from local audio file (follow specifications by YouTube Music): `.flac`, `.m4a`, `.mp3`, `.oga`, `.wma`
  - When in uploaded, auto generate playlist by uploaded songs
- Upload from local playlist file (only support `.m3u`, `.m3u8`)
- Download playlist on YouTube Music to a m3u8 file (`artist name`, `album name` and `title` must be an exact match)


## Requirements

- Python 3.6 or higher

Using [ytmusicapi](https://github.com/sigma67/ytmusicapi). Thanks for [@sigma67](https://github.com/sigma67).

## Setup

### Install command:

**In posix:**

```
pip install https://github.com/yanoshi/yootto/releases/download/v0.1.6/yootto-0.1.6.tar.gz
```

**In Windows:**

```
python -m pip install https://github.com/yanoshi/yootto/releases/download/v0.1.6/yootto-0.1.6.tar.gz
```

### Setting auth:

At first time, please set auth config for YouTube Music.

Please see document about getting "Request headers": https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers

**When using intaractive interface:** please run that command and paste "Request headers" and press "Enter, Ctrl-Z, Enter".

```
yootto auth
```

**When running in shell script:** please run that command include "Request Headers".

```
yootto auth --header_raw=`cat << EOS
accept: */*
accept-encoding: gzip, deflate, br
accept-language: ja,en-US;q=0.9,en;q=0.8
authorization: SAPISIDHASH xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
content-length: 832
content-type: application/json
cookie: xxx=xxxxxx;
origin: https://music.youtube.com
referer: https://music.youtube.com
sec-ch-ua: "Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"
sec-ch-ua-mobile: ?0
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
x-client-data: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Decoded:
message ClientVariations {
  ///
}
x-goog-authuser: 0
x-goog-visitor-id: xxxxxxxxxxxxxxxxxxxxxxx
x-origin: https://music.youtube.com
x-youtube-ad-signals: 
x-youtube-client-name: 67
x-youtube-client-version: 0.1
x-youtube-device: cbr=Chrome&cbrver=87.0.4280.88&ceng=WebKit&cengver=537.36&cos=Windows&cosver=10.0&cplatform=DESKTOP
x-youtube-identity-token: xxxxxxxxxxxxxxxxxxx
x-youtube-page-cl: 350017246
x-youtube-page-label: youtube.music.web.client_20210104_00_RC01
x-youtube-time-zone: Asia/Tokyo
x-youtube-utc-offset: 540
EOS
`
```

**Config file:**

Config file is genereted automatically.
If you want change setting file, please see `~/.yootto/config.json` .

Example: 

```json
{
  "auth_file_path": "./headers_auth.json",
  "online_catalog_cache_file_path": "./cache.json",
  "auto_create_playlist_format": "Upload List (%Y/%m/%d %H:%M:%S)"
}
```

NOTE: You can set the config file(`config.json`) from any path using `--conf=XXX` command line option.

### Load songs cache:

If you want to manage your uploaded songs outside of yootto, please build a cache.

```
yootto caching
```

Note: This process will take some time. And if YouTube Music is not working properly, it may not come back from processing. In that case, abort the process and try again.

## Usage

If you want see help, please run `yootto --help`.

### Upload songs

**Single file:**

When upload a audio file, you can set file path.

```
yootto upload music --path="hoge.mp3"
```

**Multi files:**

When upload many audio files, you can set a directory path include audio files.

```
yootto upload music --path="/music/folder/path/"
```

There is also such an execution method.

```
cd "/music/folder/path/"
yootto upload music
```

NOTE: If you want disable auto generated playlist, please set `--disable_create_playlist`.

### Upload playlist

You can upload playlist from local file.

```
yootto upload playlist --path="playlist.m3u8" --title="PLAYLIST TITLE"
```

WARN: You can use in playlist only already been uploaded music file.

**When upload other tool/official web site/etc...:**

`yootto` has the songs catalog file.
If you upload other tool, that file will be not latest.

So in that case, please set `--enable_reload_online_cache`.

**When setting character encoding:**

Please use `--encoding=XXX` option. (ex: `--encoding="utf-16-le"`)

### Download playlist

You can download playlist to a m3u8 file.

```
yootto download playlist --url="https://music.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxx" --music_path="/music/dir/path/" --output_path="./hogehoge.m3u8"
```

**When setting character encoding:**

Please use `--encoding=XXX` option. (ex: `--encoding="utf-16-le"`)

## License

MIT
