import math
import os
import subprocess

from fastmcp import FastMCP

# Create a server instance
video_mcp = FastMCP(name="video-mcp-server")


@video_mcp.tool(name="concat_videos")
def concat_videos(input_path_list: list, output_path: str) -> bool:
    """
    Concatenates multiple videos into a single video.
    :param input_path_list: Enter the list of absolute paths for the video
    :param output_path: Output the absolute path of the video
    :return: Whether the splicing is successful
    """
    inputs = []
    for file in input_path_list:
        inputs.extend(["-i", file])

    filter_complex = f"[0:v][0:a]"
    for i in range(1, len(input_path_list)):
        filter_complex += f"[{i}:v][{i}:a]"
    filter_complex += f"concat=n={len(input_path_list)}:v=1:a=1"

    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-preset",
        "fast",  # 可调整为 slow 以优化质量
        "-y",  # 覆盖输出文件
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"concat videos successful!, file: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"concat videos failed: {e}")
        return False


@video_mcp.tool(name="rotate_video")
def rotate_video(input_path: str, angle_degrees: int, output_path: str) -> bool:
    """
    旋转视频并调整输出尺寸
    功能:
        1. 将输入视频按指定角度旋转
        2. 自动调整输出视频的宽高比，避免黑边
        3. 支持覆盖已存在的输出文件
    注意:
        1. 需要预先安装 FFmpeg 并配置环境变量
        2. 输出视频格式由文件扩展名自动确定
        3. 旋转角度会自动转换为弧度制传递给 FFmpeg
    :param input_path: 输入视频文件的完整路径
    :param angle_degrees: 旋转角度（0-359度），支持任意角度
    :param output_path: 输出视频文件的保存路径
    :return: 是否成功
    """
    # 参数验证
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    if not 0 <= angle_degrees < 360:
        raise ValueError("旋转角度必须在 0-359 度之间")

    # 转换为弧度制（FFmpeg rotate 过滤器使用弧度）
    angle_radians = math.radians(angle_degrees)

    # 计算旋转后的宽高（当角度为90或270度时需要交换宽高）
    cmd_probe = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0",
        input_path
    ]
    result = subprocess.run(cmd_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if not result.stdout:
        raise RuntimeError("无法获取视频尺寸信息")

    width, height = map(int, result.stdout.strip().split(','))
    ow = height if angle_degrees in [90, 270] else width
    oh = width if angle_degrees in [90, 270] else height

    # 构建 FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"rotate={angle_radians}:ow={ow}:oh={oh}",
        "-preset", "fast",
        "-y",  # 自动覆盖输出文件
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"旋转完成: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else "未知错误"
        print(error_output)
        return False


@video_mcp.tool(name="resize_video")
def resize_video(input_path: str, scale_factor: float, output_path: str) -> str:
    """
    调整视频尺寸并保持原始分辨率
    功能:
        1. 按指定倍数缩放视频内容并保持原始分辨率
        2. 缩小时自动添加黑边（保持原始画面居中）
        3. 放大时自动裁剪超出区域（居中裁剪）
        4. 支持覆盖已存在的输出文件
    注意:
        1. 需要预先安装 FFmpeg 并配置环境变量
        2. 输出视频格式由文件扩展名自动确定
        3. 缩放倍数必须满足 0.0 < scale_factor <= 10.0
        4. 最终输出分辨率始终与输入视频保持一致
    :param input_path: 输入视频文件的完整路径
    :param scale_factor: 缩放倍数(0.0 < scale_factor <= 10.0)
    :param output_path: 输出视频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not os.path.exists(input_path):
        return f"错误：输入文件不存在 - {input_path}"

    if not 0 < scale_factor <= 100:
        return "错误：缩放倍数必须大于0且不超过100"

    # 获取原始视频尺寸
    try:
        ffprobe_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0",
            input_path
        ]
        result = subprocess.run(
            ffprobe_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        if not result.stdout:
            return "无法获取视频尺寸信息"

        width, height = map(int, result.stdout.strip().split(','))
        original_resolution = f"{width}x{height}"

    except subprocess.CalledProcessError as e:
        return f"获取视频尺寸失败: {e.stderr or '未知错误'}"

    # 计算新尺寸
    new_width = max(1, int(width * scale_factor))
    new_height = max(1, int(height * scale_factor))

    # 构建FFmpeg滤镜链
    if scale_factor <= 1:
        # 缩小：scale + pad（添加黑边）
        vf_filters = (f"scale={new_width}:{new_height}:force_original_aspect_ratio=decrease,pad={width}:{height}"
                      f":(ow-iw)/2:(oh-ih)/2")
    else:
        # 放大：scale + crop（裁剪超出区域）
        vf_filters = f"scale={new_width}:{new_height}:force_original_aspect_ratio=increase,crop={width}:{height}"

    # 构建FFmpeg命令
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", vf_filters,
        "-preset", "fast",
        "-y",  # 自动覆盖输出文件
        output_path
    ]

    try:
        subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return output_path

    except subprocess.CalledProcessError as e:
        return f"视频处理失败: {e.stderr or '未知错误'}"


if __name__ == "__main__":
    video_mcp.run(transport="stdio")
