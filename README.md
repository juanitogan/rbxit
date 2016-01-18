# RBXIT - Really Basic sÍerra Tools
_(the X is x'd out)_

Welcome to my collection of utilities and patches for [Sierra](https://en.wikipedia.org/wiki/List_of_Sierra_Entertainment_video_games) and [Dynamix](https://en.wikipedia.org/wiki/Dynamix) games from early versions of Windows--particularly, Windows 95.  I am trying to fix the games up nice and shiny to run on Windows 7 through 10 and beyond.  For the full story, please see my blog post on the subject: [Fixing Up Old (Sierra) Computer Games](http://namethattech.wordpress.com).


## Game Patches to Make Your Games Shiny Again

RBXIT Win7 game patches!  First section!.. because that is why you are here, right?  Not the tools??

:trollface: Please do not "steal" these game patches by hosting them on your own site.  Link here instead or, more preferrably, to my [blog post](http://namethattech.wordpress.com).  If I can't determine how popular they might be by the traffic, then why should I make more?  Note how, in the RBXIT wiki, I didn't steal any of the Sierra udpate files from [The Sierra Help Pages](http://www.sierrahelp.com/).  That's the way to do it.  It's called respect for someone's work. :+1:

[**Please see the RBXIT wiki for game installation instructions and patches.**](https://github.com/juanitogan/rbxit/wiki)

Otherwise, here are direct links to just the RBXIT Win7 patch files:

- 3·D Ultra MiniGolf v1.0 _(on the way)_
- 3·D Ultra MiniGolf v1.1 _(on the way)_
- [3·D Ultra MiniGolf Deluxe v2.0](https://github.com/juanitogan/rbxit/releases/download/1.0.0.3d-ultra-minigolf-deluxe-20.0/3DUltraMiniGolfDeluxe-20-Win7fix.exe)
- [3·D Ultra MiniGolf Deluxe Demo](https://github.com/juanitogan/rbxit/releases/download/1.0.0.3d-ultra-minigolf-deluxe-demo.0/3DUltraMiniGolfDeluxeDemo-complete-Win7fixed.zip) (complete and patched)
- 3·D Ultra Pinball series _(coming soon)_
- [MissionForce: CyberStorm v1.0 and v1.1](https://github.com/juanitogan/rbxit/releases/download/1.0.0.cyberstorm-10-11.0/CyberStorm-10-11-Win7fix.exe)
- CyberStorm 2: Corporate Wars _(on the way)_

In brief, all that these patches do is replace the Sierra ADPCM audio data with standard 16-bit PCM audio data of the same sample rate, as well as adjusting the WAX header info so that the game knows what kind of audio data it is reading.  If you read through the patch's batch file, you will see that no EXE files are harmed during this production (thus far) and so there should be little threat of misconduct here.

In hindsight, this fix seems rather simple and, well, it kind of is... in hindsight.  It took a decent amount of research and testing to get here.


## "More?"

Feel free to sumbit pull requests for patches you create on your own.  It's not hard (just a process now that I've wrestled it out) and my immediate time is limited.  _(Maybe if I can find a better gig......)_

I'm also no expert on the Sierra/Dynamix collection so I need help finding the games that need fixing (and are fixable) with the RBXIT tools.  Basically, 90's games with RBX files in their folders.  Help me... but don't overload me with vague requests of "can you fix this or that" random game.  Be smart and look for the RBX files and have a reason to suspect the sound effects in the game.

There could possibly be non-Sierra titles as well if they borrowed ADPCM logic from each other.  Thus, anything with the following IMA ADPCM index table in the game's EXE file is a likely candidate.  Therefore, if you know how to use a hex editor, look for this sequence of bytes (yes, the same sequence of 16 bytes twice in a row):
```
    FF FF FF FF FF FF FF FF 02 00 04 00 06 00 08 00
    FF FF FF FF FF FF FF FF 02 00 04 00 06 00 08 00
```


## The Tools

My original intent was to EXEfy these but, the more I looked at and tested some of the compilers/packagers, the more I realized it simply wasn't worth my time at the moment to push it through.  I mean, why put too much into an execute-once-in-your-lifetime tool?  Besides, anyone who is bound to make use of these is surely adept enough to also install the [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#launcher) and maybe even wrap these scripts up into batch files in their path somewhere.

Personally, I use the absolutely fabtabulous [Babun shell](https://babun.github.io/) that makes it stoopidly easy to get a Cygwin and [oh-my-zsh](http://ohmyz.sh/) environment up and running on Windows!  Complete with package installers as well.  [Hushhh.  Don't tell anyone but Babun just killed the only thing I like better about a Mac.]  Anyway...

The Python scripts are what they are and more detailed descriptions are best found in the files instead of repeated here.  I added **wax2wav.py** to the set, not because I use it, but because I knew someone would eventually bug me for it and it was easiest to just do it now.  If you write audio codec stuff, feel free to steal the logic from it and add it to audio tools.

**rbx.py** and **unrbx.py** are pretty self explanatory--they pack and unpack Sierra's _Really Basic arXives_.  (My own name for them.)

**wax421.py** (WAX 4 to 1) is where all the work is really done in these rather basic game repairs and, even then, [**SoX (Sound eXchange)**](http://sox.sourceforge.net) does all the hard work.  wax421.py re-encodes WAX type 4 as WAX type 1 (as well as spitting out WAV test files).

:boom: If anyone wants to EXEfy these for me, or get fancy and friendly with the command line arguments, feel free.  Submit a pull request and I'll likely pull it in.  Although, really, I can't imagine these tools getting much use and needing this attention.  After I or someone else patches all the games that can be patched, they will likely fade away.  Unless, of course, I (or someone) gets around to decoding the BMX and other files for custom modding.


## Other Things for Beating Games Into Shape

[**InstallSHIELD Tools**](http://www.cdmediaworld.com/hardware/cdrom/files.shtml) for unpacking old installers that don't run on modern Windows.  [This read also helps.](http://blog.wisefaq.com/2010/07/24/how-to-open-an-installshield-data-cab-file/)

[**WinHelp Decompiler "HELPDECO"**](http://sourceforge.net/projects/helpdeco/) for unpacking those old Windows HLP files.

[**Windows Help program (WinHlp32.exe)**](https://support.microsoft.com/en-us/kb/917607) in case you are running a Windows version that is still supported for reading HLP files but does not come with the program built in (Vista through 8.1).  It is looking likely that Windows 8.1 will be the last.

[**DirectX 9**](https://www.microsoft.com/en-in/download/details.aspx?id=8109).  I had DX9 already installed before I began work on RBXIT because of [sound problems with Worms Crazy Golf](http://steamcommunity.com/app/70620/discussions/2/34094415776635336/#c451848855002491098).  Therefore, I list it here _just in case_ it is discovered this somehow affects the solutions here.

[**xdelta**](http://xdelta.org/) is a binary diff tool that works far better with what I do to the RBX files than any other diff/patcher I tried/read about.  It is designed for a different type of diff and isn't really "better" than the others.  The others were giving me 10% compression at most when I should have been getting 90%.

[**MP3Gain**](http://mp3gain.sourceforge.net/) for adjusting volume in MP3 files without rewriting the audio data.

[**MIDIVOL**](http://www.gnmidi.com/gnfreeen.htm) for adjusting volume in MIDI files.  16-bit DOS program.  Thus, this will not run in a modern Windows Command shell.  Might run in [DOSBox](http://www.dosbox.com/).  I haven't tried this tool yet (at least, not in recent memory).  _If anyone has a suggested replacement, I would like to hear it. It should to be a simple tool like this one and not a multi-tool or sequencer._
