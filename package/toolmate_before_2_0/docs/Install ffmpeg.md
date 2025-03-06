# Install ffmpeg

You need to install 'ffmpeg' in order to work with plugin 'download youtube media'.

# Examples

There are different ways to install 'ffmpeg'.  Read for details at: https://www.ffmpeg.org/

We briefly describe some examples below.

    [on Linux]<br>
    - Run in terminal:
    > sudo apt install ffmpeg

    [on Windows]
    - Install "chocolatey" first. read https://chocolatey.org/install
    - open Windows PowerShell (Admin), and run:
    > choco install ffmpeg

    Add ffmpeg path:<br>
    1) Search in Windows search bar "Edit the system environment variables", and open it
    2) Select "System Variables" > "Path" > "Edit" > "New"
    3) Enter "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\"
    4) Click "OK"

    [on macOS]
    - Install "homebrew" first. read https://brew.sh/
    - Run in terminal:
    > brew install ffmpeg
