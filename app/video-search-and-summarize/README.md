# Instruction on using video search and summarize agent
## pre-requisite
#### This APP requires ffmpeg. Please first check whether it is already installed by running
```bash
which ffmpeg
```
#### Otherwise, install FFmpeg (e.g., on Mac, run brew install ffmpeg).

## Go to the video-search-and-summarize directory
```bash
cd <SlackAgents project path>/app/video-search-and-summarize
```
## Step 1: Install necessary dependencies

```bash
pip install -r requirements.txt
```

## step 2: Test query the agent

```bash
python test.py
```