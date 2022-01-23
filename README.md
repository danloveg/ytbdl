# ytbeetdl: Music Downloader and Tagger

Combines the power of [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [beets](https://github.com/beetbox/beets) to download music from the internet and automatically tag it.

This application is targeted at those who are already familiar with youtube-dl and beets. This app will work out of the box, but is great for those who want ultimate customization of the beets configuration used to tag the music, and to supply custom arguments to yt-dlp.

Note that this application only supports Python 3.6+.

## Installation

Clone this repository, open a terminal or shell in the `ytbeetdl` directory, and run the following command:

```shell
pip install -e .
```

## Usage

Before using ytbdl for this first time, you need to create a configuration file. To do so, run:

```shell
ytbdl config create
```

Then, to download an album from a playlist at https://youtube.com/some_playlist:

```shell
ytbdl get 'Artist' 'Album' 'https://youtube.com/some_playlist'
```

You can control `ytbdl` with the config file, or using command line arguments.

## Changing yt-dlp's Behaviour

You may change how yt-dlp behaves by specifying arguments on the command line, or by adding arguments to the configuration file.

To pass options to `yt-dlp` from the command line, use the `--ytdl-args` option:

```shell
ytbdl get --ytdl-args "-f bestaudio[ext=m4a] --reject-title 'music mix 2021' --geo-bypass" ...
```

You can also specify arguments by editing the `ytdl_args` setting in the config file. To get the path to your config file, run `ytbdl config path`. The `ytdl_args` setting can be edited like so:

```yaml
ytdl_args:
    - -f
    - bestaudio[ext=m4a]
    - --geo-bypass
```

Use `ytdl_args` in the config file for settings you want to use all the time. Use `--ytdl-args` on the command line for settings that may change between downloads.

## Changing beets' Behaviour

You can modify beets' behaviour by editing ytbdl's config. ytbdl's config file *is* a beets config file, so edit it as you would a beets config file. To edit the config, set an editor in the config file. First, open the configuration to edit it:

```shell
# If you like vim!
vim $(ytbeetdl config path)

# If you're on Windows and like notepad!
notepad $(ytbeetdl config path)
```

Add an `editor` to the YAML configuration:

```yaml
editor: vim
```

`ytbdl` will read this option and allow you to edit the configuration with that editor using the `edit` command:

```shell
ytbeetdl config edit
```

For example, maybe you want to add the [zero](https://beets.readthedocs.io/en/stable/plugins/zero.html) plugin. Simply add it to the list of plugins:

```yaml
plugins: # DO NOT REMOVE
    - fromdirname # DO NOT REMOVE
    - fromyoutubetitle # DO NOT REMOVE
    - fetchart
    - embedart
    - zero # <-- Just added!

# Options for zero
zero:
    fields: day month genre
```

Make sure not to remove any lines that say "DO NOT REMOVE" or you will encounter issues!

## Configuration Notes

ytbdl exposes a configuration file that can be used to control the behaviour of beets during the auto-tag process. This configuration file *is* a beets config file, and "overwrites" your beets config when ytbdl calls beets. All of the configuration options you'd use with beets can be used in the ytbeetdl configuration. If you already have a beets config, it will not be modified, but the options specified in the ytbeetdl configuration have higher priority and will take precedence over any existing options.

The only two option that ytbdl exposes that aren't beets config options are the `editor` and `ytdl_args` options. For a list of beets' options, view the [beets documentation](https://beets.readthedocs.io/en/stable/reference/config.html).

For a list of yt-dlp options, view the [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp#usage-and-options). Note that the `--output` and `--extract-audio` options are used by default (and can't be turned off). Any attempt at re-specifying these options will result in an error.

## Updating yt-dlp

yt-dlp is frequently updated. If you find that downloads aren't working, try updating yt-dlp.

```shell
pip install --upgrade yt-dlp
```
