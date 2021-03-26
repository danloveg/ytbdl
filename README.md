# ytbeetdl: Music Downloader and Tagger

Combines the power of [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [beets](https://github.com/beetbox/beets) to download music from the internet and automatically tag it.

This application is targeted at those who are already familiar with youtube-dl and beets. This app
will work out of the box, but is great for those who want ultimate customization of the beets configuration used to tag the music, and to supply custom arguments to youtube-dl.

## Installation

Clone this repository, and run the included `setup.py` using Python 3. Note that only Python 3.6+ is
supported.

## Usage

Before using ytbeetdl for this first time, you need to create a configuration file. To do so, run:

```shell
ytbeetdl config create
```

Then, to download an album from a playlist at https://youtube.com/some_playlist:

```shell
ytbeetdl get --artist 'Artist' --album 'Album' 'https://youtube.com/some_playlist'
```

You can pass options to `youtube-dl` with `--ytdl-options`:

```shell
ytbeetdl get --ytdl-options "-f bestaudio[ext=m4a] --reject-title 'music mix 2021' --geo-bypass" ...
```

You can modify beets' behaviour by editing ytbeetdl's config. To edit the config, set an editor in the config file. First, open the configuration to edit it:

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

`ytbeetdl` will read this option and allow you to edit the configuration with that editor using the `edit` command:

```shell
ytbeetdl config edit
```

Add the [zero](https://beets.readthedocs.io/en/stable/plugins/zero.html) plugin to the list:

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

ytbeetdl exposes a configuration file that can be used to control the behaviour of beets during the auto-tag process. This configuration file *is* a beets config file, and "overwrites" your beets config when ytbeetdl calls beets. All of the configuration options you'd use with beets can be used in the ytbeetdl configuration. If you already have a beets config, it will not be modified, but the options specified in the ytbeetdl configuration have higher priority and will take precedence over any existing options.

The only option that ytbeetdl exposes that isn't a beets config option, is the `editor` option. For a list of beets' options, view the [beets documentation](https://beets.readthedocs.io/en/stable/reference/config.html).

For a list of youtube-dl options, view the [youtube-dl documentation](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#options). Note that the `--output` and `--extract-audio` options are used by default (and can't be turned off). Any attempt at re-specifying these options will result in a warning or an error.

## Updating youtube-dl

youtube-dl is frequently updated. If you find that downloads aren't working, try updating youtube-dl.

```shell
python -m pip install --upgrade youtube-dl
```
