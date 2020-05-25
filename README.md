# mlc
This is a minimal++ language compiler.  
<img src="/images/logo.png" width="500" height="500">  
## Usage:
```
python3 mlc.py --help                      : Print help information<br>
python3 mlc.py -save-temps program.min     : Does not delete idermediate,array of symbols,C files<br>
python3 mlc.py program.min                 : Delete idermediate,array of symbols,C files<br>
```

minimal++ produce assembly language for MIPS but produce and other files
if the -save-temps argument is passed.It produce the intermediate file,the
array of symbols and a file with the program in C for test(does not work with
nesting functions)<br>
