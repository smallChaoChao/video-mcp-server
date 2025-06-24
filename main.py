import subprocess

from fastmcp import FastMCP


# Create a server instance
video_mcp = FastMCP(name="video-mcp-server")


@video_mcp.tool(name="concat_videos")
def concat_videos(input_videos: list, output_filename: str) -> bool:
    """
    Concatenates multiple videos into a single video.
    :param input_videos: Enter the list of absolute paths for the video
    :param output_filename: Output the absolute path of the video
    :return: Whether the splicing is successful
    """
    inputs = []
    for file in input_videos:
        inputs.extend(["-i", file])

    filter_complex = f"[0:v][0:a]"
    for i in range(1, len(input_videos)):
        filter_complex += f"[{i}:v][{i}:a]"
    filter_complex += f"concat=n={len(input_videos)}:v=1:a=1"

    cmd = [
        "ffmpeg", *inputs,
        "-filter_complex", filter_complex,
        "-preset", "fast",  # 可调整为 slow 以优化质量
        output_filename
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"concat videos successful!, file: {output_filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"concat videos failed: {e}")
        return False


if __name__ == "__main__":
    video_mcp.run(transport="stdio")
