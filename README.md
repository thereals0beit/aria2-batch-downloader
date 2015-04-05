aria2-batch-downloader
======================

Allows you to download files from HTTP file lists by single file or directory (with optional regex argument)

This file is coded like crap and not finished!
It was also made for lighttpd's file list HTML, it may require some patching for other designs.

### How-to

This script makes batch downloading and simple file downloading with aria2 easier.

Example of usage:
```
seed "https://myseedbox.com/file.mkv"
```

Will download one file

```
seed "https://myseedbox.com/some_show/"
```

Will download all files in that directory into the current working directory, however, there is no recursion so folders will not be saved. I am working on recursion support.

```
seed "https://myseedbox.com/some_folder/" "(.*).txt"
```

You can use regex to download only the files you need by adding a second parameter that contains the regex, the first parameter must be a folder.
