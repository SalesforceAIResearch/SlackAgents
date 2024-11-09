import os
import yt_dlp
import librosa
from openai import OpenAI
import soundfile as sf
from slackagents import FunctionTool, OpenAILLM, BaseLLMConfig


def summarize_youtube_video(
        youtube_url: str
        ) -> str:
    """A tool to summarize youtube video content
    :param youtube_url: The youtube video url to be summarized
    :type youtube_url: string
    :return: A text summary of the youtube video
    :rtype: string
    """
    client = OpenAI()
    output_dir = "audio_cache"  # temp dir to store video cache
    # Step 1: Download audio from YouTube
    audio_file = download_audio(youtube_url, output_dir)
    # Step 2: chunk audio
    chunk_audio(audio_file)
    # # Step 2: Transcribe the audio
    transcription = transcribe_audio(audio_file, client)
    # step 3: summarize video
    summary = summarize(transcription)
    os.remove(audio_file)
    return summary

def chunk_audio(audio_file, segment_length=600):
    audio, sr = librosa.load(audio_file, sr=44100)
    end = int(segment_length * sr)
    # Use the first chucnk for summarization for now.
    first_chunk = audio[:end]
    sf.write(audio_file, first_chunk, sr)
    return audio_file


def chunk_text(text, max_length=3000):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence + '.'
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def summarize(transcription):
    chunks = chunk_text(transcription)
    # only summarize the first chunk for now
    llm = OpenAILLM(BaseLLMConfig(model="gpt-4o"))
    system_prompt = """
    You are a helpful assistant tasked with summarizing YouTube videos. 
    You will be provided with text transcribed from the video's audio. 
    Your task is to generate a summary of the video based on this transcribed text. Please make the summary less than 5 sentences.
    The summary should clearly convey the video's main content, and if possible, include bullet points highlighting key points.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chunks[0]}
    ]
    summary = llm.chat_completion(messages)["content"].strip()
    return summary


def transcribe_audio(file_path, client):
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcription.text


def download_audio(youtube_url, output_dir="outputs"):
    a_type = "mp3"
    ydl_config = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": a_type,
                "preferredquality": "192"
            }
        ],
        "outtmpl": os.path.join(output_dir, "temp"),
        "verbose": True,
    }
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Downloading video from {youtube_url}")

    try:
        with yt_dlp.YoutubeDL(ydl_config) as ydl:
            ydl.download([youtube_url])
    except:
        return False
    return os.path.join(output_dir, f"temp.{a_type}")

video_summarization_tool = FunctionTool.from_function(summarize_youtube_video)
# print(f"Video Summarization Tool: {json.dumps(video_summarization_tool.info, indent=4)}")