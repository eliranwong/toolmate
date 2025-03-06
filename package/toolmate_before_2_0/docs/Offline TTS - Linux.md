# Offline TTS - Linux

ToolMate v0.2.7+ integrates [piper-tts](https://github.com/rhasspy/piper) on Linux for offline text-to-speech feature.

Please note that piper-tts does not support Windows or macOS at the time of writing.

# Setup

1. Install piper-tss, e.g.

> cd ~/dev # this path depends on where your environment directory locates

> source toolmate/bin/activate

> pip install piper-tts

2. Select "change text-to-speech config" from action menu:

![piper1](https://github.com/eliranwong/toolmate/assets/25262722/6ec8a98b-4a12-49b3-99b5-d45683ee66f9)

3. Select "Piper" from available tts options:

![piper2](https://github.com/eliranwong/toolmate/assets/25262722/ffe1a21d-9f7e-431e-bcbb-07f09f3e0535)

4. Select a piper voice model:

(Details: https://github.com/rhasspy/piper/blob/master/VOICES.md)

![piper3](https://github.com/eliranwong/toolmate/assets/25262722/e2c841a6-3622-419e-bcdf-0301fccb74fb)

5. You can optionally specify voice speed if you have "[VLC player](https://www.videolan.org)" or "cvlc" command installed.

6. Select "toggle input audio" from action menu, to enable / disable reading input text

7. Select "toggle output audio" from action menu, to enable / disable reading output text

# Download More Voices

Voices are automatically downloaded when you first use them.

They are stored at ~/toolmate/LLMs/piper/ by default.

You can also manually downloaded more voices from https://github.com/rhasspy/piper/blob/master/VOICES.md and place them in the folder.

![piper_voice_storage](https://github.com/eliranwong/toolmate/assets/25262722/9c9f8d43-884f-4ff1-bb17-4fbdbd895c56)
