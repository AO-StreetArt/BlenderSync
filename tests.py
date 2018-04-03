import os
import glob
import subprocess
import sys

blenderExecutable = None
homeDirectory = None

# Accept Blender Executable as command line argument
if len(sys.argv) > 2:
    blenderExecutable = sys.argv[1]
    homeDirectory = sys.argv[2]
else:
    assert(False)

# iterate over each *.test.blend file in the "tests" directory
# and open up blender with the .test.blend file and the corresponding .test.py python script
for f in glob.glob('./tests/**/*.test.blend'):
    test_file = f.replace('.blend', '.py')
    print(f)
    print(test_file)
    subprocess.call([blenderExecutable, '--factory-startup', '-noaudio', '-b', f, '--python', test_file, '--', homeDirectory])
