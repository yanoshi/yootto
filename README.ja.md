# yootto

yoottoは「ヨーッと」って感じでサクッとYouTube Musicにアップロードとかを行うために作ったなにかです。

(俺得な感じで作っているので今後更新するかは分かりませんが)

## 環境

- Python 3.6以上

またこのアプリケーションはYouTube Musicの非公式APIである[ytmusicapi](https://github.com/sigma67/ytmusicapi)を利用しています。
なのでYouTube Music側の仕様変更で突然動かなくなっちゃうかもです。

便利なライブラリを作ってくれた作者さん([@sigma67](https://github.com/sigma67))に感謝。


## 機能

一応WindowsもmacOSもLinuxもサポートしているとは思います。

- オーディオファイルのアップロードに対応
  - 対応フォーマット(これはYouTube Musicの仕様に基づきます): `.flac`, `.m4a`, `.mp3`, `.oga`, `.wma`
  - 自動で「そのタイミングでアップロードしたファイルをまとめたプレイリスト」的なのを作成
- プレイリストファイルのアップロードに対応
  - 現状 `.m3u`, `.m3u8` にしか対応していません
  - プレイリストに記載されている曲は全て事前にアップロード済みである必要があります
- プレイリストのダウンロードに対応
  - YouTube Music上のプレイリストとローカルのファイルを突き合わせてm3u8ファイルを作ります
  - 現状「アーティスト名」「アルバム名」「タイトル名」が完全一致しないと同一曲と判定されません

## 設定

### インストール方法:

下記コマンドを実行してください。

**Posix環境の場合:**

```
pip install https://github.com/yanoshi/yootto/releases/download/v0.1.4/yootto-0.1.4.tar.gz
```

**Windowsの場合:**

```
python -m pip install https://github.com/yanoshi/yootto/releases/download/v0.1.4/yootto-0.1.4.tar.gz
```

### 認証設定:

初回のみ認証設定が必要です。(割とややこしい)

リクエストヘッダーの得方については下記ドキュメントを見てください。

https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers


**Firefoxユーザーの場合:** 下記コマンド実行した後に、Firefoxで得られたリクエストヘッダーのコピーを貼り付けてください。

```
yootto auth
```

**Google Chrome もしくは Edgeのユーザーの場合:** 下記のようにリクエストヘッダーを含むような形のコマンドを実行すると動くはずです。

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

### 設定ファイルを変更する場合:

設定ファイルは `~/.yootto/config.json` に自動で生成されます。

例: 

```json
{
  "auth_file_path": "./headers_auth.json",
  "online_catalog_cache_file_path": "./cache.json",
  "auto_create_playlist_format": "Upload List (%Y/%m/%d %H:%M:%S)"
}
```

もし任意の場所に保存された設定ファイルを利用したい場合は `--conf=XXX` オプションを付けてコマンドを実行すると幸せになれます。


## 使い方

下記でもわからない場合は `yootto --help` でヘルプが出るとは思いますが分かりやすいかは謎。

### 曲のアップロード

**単一ファイルの場合:**

こんな感じでオーディオファイルのパスを指定しましょう。

```
yootto upload music --path="hoge.mp3"
```

**複数ファイルをどかっと上げたい場合:**

ディレクトリでもパスは指定できます。音楽フォルダを適当に指定したら、そのフォルダ配下のファイルを全部上げようとします。

```
yootto upload music --path="/music/folder/path/"
```

**自動で作られるプレイリストを無効にする:**

`--disable_create_playlist` オプションを指定して実行しましょう。


### プレイリストのアップロード

こんな感じでプレイリストファイルとプレイリスト名を指定しましょう。

```
yootto upload playlist --path="playlist.m3u8" --title="プレイリスト名"
```

**もしほかのツールとかでオーディオファイルをアップしてしまったら:**

`yootto` はローカルにアップロード済みオーディオに関する情報をキャッシュしています。

他のツールでアップロードしたコンテンツがあった場合、それらの情報が最新になってないため、プレイリストが正常に作成できない可能性があります。

その場合は `--enable_reload_online_cache` オプションを付けて実行してください。キャッシュが自動更新されます。

**文字コードを設定したい場合:**

初期設定では `utf-8` でプレイリストファイルを読み込もうとします。
それ以外の文字コードで保存されたファイルは `--encoding=XXX` オプションを指定して読み込んでください. (ex: `--encoding="utf-16-le"`)


### プレイリストのダウンロード

プレイリストURLと、ローカルの楽曲フォルダのパス等を指定すると、YouTube Music上のプレイリストとローカルのファイルを突き合わせて、プレイリストファイル(`.m3u8`)を作ってくれます。

```
yootto download playlist --url="https://music.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxx" --music_path="/music/dir/path/" --output_path="./hogehoge.m3u8"
```

**文字コードを設定したい場合:**

初期設定では `utf-8` でプレイリストファイルを書き込もうとします。
それ以外の文字コードで保存したい場合は `--encoding=XXX` オプションを指定して読み込んでください. (ex: `--encoding="utf-16-le"`)


## License

MIT
