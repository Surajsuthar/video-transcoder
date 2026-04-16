import uuid

import ffmpeg


def transcode_video(file_path: str, width: int, height: int, bitrate: int, resolution: str) -> str:
    try:
        output_path = f"{uuid.uuid4()}_{resolution}.transcoded.mp4"
        ffmpeg.input(file_path).output(output_path, vf=f"scale={width}:{height}", video_bitrate=bitrate).run(overwrite_output=True)
        return output_path
    except ffmpeg.Error as e:
        raise RuntimeError(f"Transcoding failed: {e}")
