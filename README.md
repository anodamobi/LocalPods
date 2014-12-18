Local-CocoaPods-auto-attacher
=============================

Automagically attach via :path locally hosted CocoaPods repos from Podfile.

Sometimes you need to create new private CocoaPod for your project, but it's very complicated to debug and improve it while it automatically attached via `pod update` command because there is not a git repo in the __Pods__ folder. It's okay in production — you don't need to download whole repos of your pods each time you setup new projects, but when you developing new Pods — it's a required time-saving feature.

Solution
--------


To fix that CocoaPods offers `:path` parameter. You can use it in your __Podfile__:
```
pod 'MyPrivatePodName', :path => 'path/to/local/repo'
```

But when you have 10 or more private Pods it's going to be very painful to manage all local paths.

We have created a smart script that will do all the magic for you.

Just call the `attach-local-pods.py` script in the project folder and it will scan your __Podfile__ for a pods that installed locally and add `:path` parameter to them.

By default script looks for a private Pods folders in the parent directory of current working directory.

For example, you have next folders structure on your disk:

```
[Holy Folder]
├── [iOS Project]
│   └── Podfile
├── [PrivatePod1]
└── [PrivatePod2]
```

And your __Podfile__ contains next pods:

```
pod 'PrivatePod1'
pod 'PrivatePod2'
```

After you will run the `attach-local-pods.py` script, your __Podfile__ will looks like:

```
pod 'PrivatePod1', :path => '/Holy Folder/PrivatePod1'
pod 'PrivatePod2', :path => '/Holy Folder/PrivatePod2'
```

Note, that all paths will be absolute (we plan to add `--relative` option soon). In real life itthey will looks like `/Users/alex/Development/PrivatePod1`.

Exceptions
----------

* Script will skip pods with existing `:path` parameter. We plan to add some interactive solution soon.
* Script will check specified folder in `:path` parameter for existing.
* Script will work with any additional __Podfile__ parameters such as pod's version, custom git URL and any other.

Usage
-----

```
usage: attach-local-pods.py [-h] [--version] [-v] [--pods PATH]
                            [--podfile PODFILE] [-d --dry-run]
                            [-o --preserve-originals]

Injects local copies of CocoaPods in Podfile

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v                    verbose output
  --pods PATH           local Pods folder path (default is parent dir)
  --podfile PODFILE     Podfile path (default is ./Podfile)
  -d --dry-run          perform a trial run with no changes made
  -o --preserve-original
                        preserve original lines with comments
```

### Example call

```
attach-local-pods.py -d -v
```

With this parameters (`-v` and `-d`) script will dry run produce more detailed output. So your __Podfile__ will be untouched, you will see new __Podfile__ in stdout.

```
Performing a trial run with no changes made

DEBUG: Using Local Pods folder: /Users/themengzor/Documents/Work/
DEBUG: Using Podfile: /Users/themengzor/Documents/Work/ctrldo-ios-latest/Podfile

DEBUG: Found pod 'ReactiveCocoa', '~> 2.3'
DEBUG: Pod name: ReactiveCocoa

DEBUG: Found pod 'LKAssetsLibrary', '~> 1.1'
DEBUG: Pod name: LKAssetsLibrary

DEBUG: Found pod 'KVOController'
DEBUG: Pod name: KVOController

DEBUG: Found pod 'SWParallaxScrollView', '~> 0.1.1'
DEBUG: Pod name: SWParallaxScrollView

DEBUG: Found pod 'GTScrollNavigationBar', '~> 0.1'
DEBUG: Pod name: GTScrollNavigationBar

DEBUG: Found pod 'pop'
DEBUG: Pod name: pop

DEBUG: Found pod 'POP+MCAnimate', '~> 1.1'
DEBUG: Pod name: POP+MCAnimate

DEBUG: Found pod 'Masonry'
DEBUG: Pod name: Masonry

DEBUG: Found pod 'MSSPopMasonry'
DEBUG: Pod name: MSSPopMasonry

DEBUG: Found pod 'FrameAccessor'
DEBUG: Pod name: FrameAccessor

DEBUG: Found pod 'libPhoneNumber-iOS', '~> 0.7.1'
DEBUG: Pod name: libPhoneNumber-iOS

DEBUG: Found pod 'FastEasyMapping', '~> 0.3.1'
DEBUG: Pod name: FastEasyMapping

DEBUG: Found pod 'CocoaLumberjack', '~> 1.9.0'
DEBUG: Pod name: CocoaLumberjack

DEBUG: Found pod 'ANCategories', :path => '/Users/themengzor/Documents/Work/ANCategories'
DEBUG: Pod name: ANCategories

WARNING: This pod already pointed at local path: /Users/themengzor/Documents/Work/ANCategories

WARNING: Local path /Users/themengzor/Documents/Work/ANCategories for Pod ANCategories does not exists!

The new Podfile:

source 'https://github.com/CocoaPods/Specs.git'
source 'https://github.com/anodamobi/ANODA-CocoaPods.git'

platform :ios, "7.0"
target "CtrlDo" do

#Core
pod 'ReactiveCocoa', '~> 2.3'
pod 'LKAssetsLibrary', '~> 1.1'
pod 'KVOController'

#UI
pod 'SWParallaxScrollView', '~> 0.1.1'
pod 'GTScrollNavigationBar', '~> 0.1'
pod 'pop'
pod 'POP+MCAnimate', '~> 1.1'
pod 'Masonry'
pod 'MSSPopMasonry'

#UI Categories
pod 'FrameAccessor'

#Helpers
pod 'libPhoneNumber-iOS', '~> 0.7.1'

#Core Data
pod 'FastEasyMapping', '~> 0.3.1'
#pod 'MagicalRecord',  '~>2.2' - added static sources;


#! ----- debugging tools, remove on prod --------- !
pod 'CocoaLumberjack', '~> 1.9.0'

pod 'ANCategories', :path => '/Users/themengzor/Documents/Work/ANCategories'

end
```

### Use cases

Update __Podfile__ in current folder, look for a Pods in the parent folder:

```
./attach-local-pods.py
```

Update __Podfile__ in folder `/Users/alex/Development/Projects/Trainings/Demo`, look for a Pods in the `/Users/alex/Development/Pods` folder:

```
./attach-local-pods.py \
    --pods /Users/alex/Development/Pods \
    --podfile /Users/alex/Development/Projects/Trainings/Demo
```

Contribution
------------

Feel free to fork and update this script, we are waiting for your feedback at alex@anoda.mobi