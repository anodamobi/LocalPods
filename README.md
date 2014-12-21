LocalPods
=========

Automagically attach via :path locally hosted CocoaPods repos from Podfile.

Sometimes you need to create new private CocoaPod for your project, but it's very complicated to debug and improve it while it automatically attached via `pod update` command from remote repo because there is not a git repo in the __Pods__ folder. It's okay in production — you don't need to download whole repos of your pods each time you setup new projects, but when you developing new Pods — it's a required time-saving feature.

Solution
--------


To fix that CocoaPods offers `:path` parameter. You can use it in your __Podfile__:
```
pod 'MyPrivatePodName', :path => 'path/to/local/repo'
```

But when you have 10 or more private Pods it's going to be very painful to manage all local paths.

We have created a smart script that will do all the magic for you.

Just call the `localpods.py` script in the project folder and it will scan your __Podfile__ for a pods that installed locally and add `:path` parameter to them.

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

After you will run the `localpods.py` script, your __Podfile__ will looks like:

```
pod 'PrivatePod1', :path => '/Holy Folder/PrivatePod1'
pod 'PrivatePod2', :path => '/Holy Folder/PrivatePod2'
```

Note, that all paths will be absolute (we plan to add `--relative` option soon). In real life itthey will looks like `/Users/alex/Development/PrivatePod1`.

Exceptions
----------

* Script will skip pods with existing `:path` parameter. We plan to add some interactive solution soon.
* Script will check specified folder in `:path` parameter for existing and warn you if provided folder does not exists.
* Script will work with any additional __Podfile__ parameters such as pod's version, custom git URL and any other.
* Script can backup your __Podfile__ before changing (optionally with `-b` or `--backup` parameter).

Usage
-----

```
usage: localpods.py [-h] [--version] [-v] [--pods PODS] [--podfile PODFILE]
                    [-d] [-b] [-o] [-g] [-r] [-c CONFIG] [--generate-config]

Injects local copies of CocoaPods in Podfile

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v                    verbose output
  --pods PODS           local Pods folder path (default is parent dir)
  --podfile PODFILE     Podfile path (default is ./Podfile)
  -d, --dry-run         perform a trial run with no changes made
  -b, --backup          backup Podfile before update
  -o, --preserve-original
                        preserve original lines with comments
  -g, --group           group local pods
  -r, --runupdate       run `pod update` after saving
  -c CONFIG, --config CONFIG
                        config file (default is ~/.localpods)
  --generate-config     generate config file interactively and exit
```

### Example call

```
localpods.py -d -v
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

__Localpods__ is very flexible script that will turn your __Pods__ development from hell to heaven ^_^

#### Daily usage

Update __Podfile__ in current folder, look for a Pods in the parent folder (or custom folder from config file) and run `pod update` after completition:

```
./localpods.py -r
```

#### Changes preview

Don't want to apply changes immediately? It's okay, everybodylies.jpg :D

```
./localpods.py -d
```
This will perform dry run and output new __Podfile__ to the stdout instead of file.

#### Custom paths

Update __Podfile__ in folder `/Users/alex/Development/Projects/Trainings/Demo`, look for a Pods in the `/Users/alex/Development/Pods` folder:

```
./localpods.py \
    --pods /Users/alex/Development/Pods \
    --podfile /Users/alex/Development/Projects/Trainings/Demo
```

#### Customisation and configuration

It's logical to assume that you will store all your local pods in one separate folder and you don't want to enter pods folder path each time you using the script. So you can simply run `./localpods.py --generate-config` and the answer few questions. This will generate your personal config file for __localpods__ and store it in `~/.localpods` file. You can also create this file manually. Here is an example of config file:

```
[localpods]
pods = ~/Documents/Work/Pods
group = False
preserve = True
runupdate = True
backup = True
```

Each time you will run the script it will use options from config file. All options can be overrided from command line. For example, you have option `pods = ~/LocalPods` in your config file, but right now you want to use custom folder: `./localpods.py --pods ~/CustomLocalPods`.

Contribution
------------

Feel free to fork and update this script, we are waiting for your feedback at alex@anoda.mobi