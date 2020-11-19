# ytbeetdl: Youtube-DL/Beets Music Downloader and Tagger

Combines the power of [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [beets](https://github.com/beetbox/beets) to download music from the internet and automatically tag it.

This application is targeted at those who are already familiar with youtube-dl and beets. This app
will work out of the box, but is great for those who want ultimate customization of the beets configuration used to tag the music, and to supply custom arguments to youtube-dl.

## Installation

Clone this repository, and run the included `setup.py` using Python 3. Note that only Python 3.5+ is
supported.

Create a default configuration file:

```shell
ytbeetdl config create
```

Open the configuration to edit it:

```shell
# If you like vim!
vim $(ytbeetdl config path)

# If you're on Windows and like notepad!
notepad $(ytbeetdl config path)
```

Add an `editor` to the YAML configuration:

```yaml
editor: vim

youtube-dl:
    ...
```

`ytbeetdl` will read this option and allow you to edit the configuration with that editor using the `edit` command:

```shell
ytbeetdl config edit
```

## Usage

Download music from https://someurl and https://otherul, and autotag them as an album:

```shell
ytbeetdl get --artist 'Artist Name' --album 'Album Name' https://someurl https://otherurl
```
