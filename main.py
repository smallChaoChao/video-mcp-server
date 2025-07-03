import math
import os
import subprocess

from fastmcp import FastMCP

# Create a server instance
video_mcp = FastMCP(name="video-mcp-server")


@video_mcp.tool(name="concat_videos")
def concat_videos(input_path_list: list, output_path: str) -> str:
    """
    使用 FFmpeg 按顺序拼接多个视频文件
    功能:
        1. 支持任意数量视频文件的顺序拼接
        2. 使用 concat demuxer 实现无损快速合并（要求视频编码格式一致）
        3. 自动创建临时文件列表并清理
        4. 支持覆盖已存在的输出文件

    注意:
        - 需要预先安装 FFmpeg 并配置环境变量
        - 所有输入视频需使用相同的编码格式
        - 输出视频格式由文件扩展名自动确定
    :param input_path_list: 输入视频文件路径列表（需按顺序排列）
    :param output_path: 输出视频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not input_path_list:
        return "错误：视频路径列表为空"

    missing_files = [path for path in input_path_list if not os.path.exists(path)]
    if missing_files:
        return f"错误：以下文件不存在 - {', '.join(missing_files)}"

    # 创建临时文件列表
    list_file = "temp_video_list.txt"
    try:
        with open(list_file, "w") as f:
            for path in input_path_list:
                f.write(f"file '{os.path.abspath(path)}'\n")

        # 构建 FFmpeg 命令
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-y",  # 自动覆盖输出文件
            output_path
        ]

        # 执行命令
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # 清理临时文件
        os.remove(list_file)
        return output_path

    except subprocess.CalledProcessError as e:
        # 捕获并返回错误信息
        error_msg = e.stderr or "未知错误"
        return f"视频拼接失败: {error_msg}"
    except Exception as e:
        return f"发生异常: {str(e)}"


@video_mcp.tool(name="rotate_video")
def rotate_video(input_path: str, angle_degrees: int, output_path: str) -> str:
    """
    使用 FFmpeg 旋转视频并保持原始分辨率（自动添加黑边以适应旋转后画面）
    功能:
        1. 按指定角度旋转视频内容
        2. 自动添加黑边保持原始分辨率不变
        3. 支持覆盖已存在的输出文件
        4. 自动保持画面居中显示

    注意:
        1. 需要预先安装 FFmpeg 并配置环境变量
        2. 输出视频格式由文件扩展名自动确定
        3. 旋转角度会自动转换为弧度制传递给 FFmpeg
    :param input_path: 输入视频文件的完整路径
    :param angle_degrees: 旋转角度（0-359度），支持任意角度
    :param output_path: 输出视频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not os.path.exists(input_path):
        return f"错误：输入文件不存在 - {input_path}"

    if not 0 <= angle_degrees < 360:
        return "错误：旋转角度必须在 0-359 度之间"

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

    except subprocess.CalledProcessError as e:
        return f"获取视频尺寸失败: {e.stderr or '未知错误'}"

    # 转换为弧度制（FFmpeg rotate 过滤器使用弧度）
    angle_radians = math.radians(angle_degrees)

    # 构建FFmpeg滤镜链
    vf_filters = (
        f"rotate={angle_radians}:c=black@0:ow='hypot(iw,ih)':oh='ow',"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )

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
        return f"视频旋转失败: {e.stderr or '未知错误'}"


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

# todo: 存在bug 输出的视频长度有问题
@video_mcp.tool(name="adjust_video_speed")
def adjust_video_speed(input_path: str, speed: float, output_path: str) -> str:
    """
    使用 FFmpeg 调整视频播放速度（支持 0.1-1000 倍速）
    功能:
        1. 支持任意速度调整（0.1-1000 倍速）
        2. 自动分解为多个 atempo 滤镜以支持大于 2 倍速的调整
        3. 自动保持音视频同步
        4. 支持覆盖已存在的输出文件

    注意:
        - 需要预先安装 FFmpeg 并配置环境变量
        - 输出视频格式由文件扩展名自动确定
        - 音频处理使用 libmp3lame 编码器（需预先安装）
    :param input_path: 输入视频文件的完整路径
    :param speed: 播放速度（0.1-1.0 为慢放，1.0-1000 为快进）
    :param output_path: 输出视频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not os.path.exists(input_path):
        return f"错误：输入文件不存在 - {input_path}"

    if not (0.1 <= speed <= 1000):
        return "错误：播放速度必须在 0.1 到 1000 之间"

    # 如果速度为 1.0，直接复制流
    if speed == 1.0:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            "-preset", "fast",
            "-y", output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return output_path
        except subprocess.CalledProcessError as e:
            return f"视频复制失败: {e.stderr or '未知错误'}"

    # 分解速度到多个 atempo 滤镜（FFmpeg atempo 限制在 0.5-2.0 之间）
    def decompose(factor):
        filters = []
        while factor < 0.5:
            filters.append(0.5)
            factor *= 2.0
        while factor > 2.0:
            filters.append(2.0)
            factor /= 2.0
        if factor != 1.0:
            filters.append(factor)
        return filters

    atempos = decompose(speed)
    afilters_str = ",".join(f"atempo={f:.2f}" for f in atempos)
    video_pts = 1.0 / speed
    vf_str = f"setpts=PTS*{video_pts}/TB"

    # 构建 FFmpeg 命令
    cmd = ["ffmpeg", "-i", input_path]

    # 添加视频处理逻辑
    cmd.extend(["-vf", vf_str])

    # 添加音频处理逻辑
    if speed != 1.0:
        cmd.extend(["-af", afilters_str])

    # 添加通用参数
    cmd.extend([
        "-preset", "fast",
        "-y", output_path
    ])

    # 自动选择音频编码器（优先使用 libmp3lame）
    has_audio = False
    try:
        # 检查是否包含音频流
        check_audio_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_type", "-of", "csv=p=0",
            input_path
        ]
        result = subprocess.run(
            check_audio_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=True
        )
        has_audio = bool(result.stdout.strip())
    except Exception:
        pass  # 忽略检查错误

    # 根据音频存在性选择编码器
    if has_audio:
        cmd.extend(["-c:a", "libmp3lame"])
    else:
        cmd.extend(["-c:a", "copy"])  # 无音频时直接复制流

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or "FFmpeg 执行失败"
        return f"视频处理失败: {error_output}"
    except Exception as e:
        return f"发生异常: {str(e)}"


@video_mcp.tool(name="adjust_video_volume")
def adjust_video_volume(input_path: str, volume_factor: float, output_path: str) -> str:
    """
    使用 FFmpeg 调整视频中音频的音量倍数（支持 0.1-10 倍）
    功能:
        1. 支持任意音量倍数调整（0.1-100 倍）
        2. 自动保持视频流不变，仅调整音频流
        3. 支持覆盖已存在的输出文件
        4. 自动检测并处理无音频场景

    注意:
        - 需要预先安装 FFmpeg 并配置环境变量
        - 输出视频格式由文件扩展名自动确定
        - 音量倍数必须满足 0.1 ≤ volume_factor ≤ 100
        - 如果输入视频无音频，会自动跳过音频处理
    :param input_path: 输入视频文件的完整路径
    :param volume_factor: 音量调整倍数（0.1-1.0 为缩小，1.0-10 为放大）
    :param output_path: 输出视频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not os.path.exists(input_path):
        return f"错误：输入文件不存在 - {input_path}"

    if not 0.1 <= volume_factor <= 100:
        return "错误：音量倍数必须在 0.1 到 100 之间"

    # 检查视频是否包含音频流
    check_audio_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_type", "-of", "csv=p=0",
        input_path
    ]
    has_audio = False
    try:
        result = subprocess.run(
            check_audio_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        has_audio = bool(result.stdout.strip())
    except Exception:
        pass  # 忽略检查错误，视为无音频

    # 构建 FFmpeg 命令
    ffmpeg_cmd = ["ffmpeg", "-i", input_path]

    # 添加视频流处理（直接复制）
    ffmpeg_cmd.extend(["-c:v", "copy"])

    if has_audio:
        # 添加音频处理逻辑
        ffmpeg_cmd.extend([
            "-af", f"volume={volume_factor:.2f}",
            "-c:a", "aac"  # 使用 AAC 编码器保证兼容性
        ])
    else:
        # 无音频时直接复制所有流
        ffmpeg_cmd.extend(["-c:a", "copy"])

    # 添加通用参数
    ffmpeg_cmd.extend([
        "-preset", "fast",
        "-y",  # 自动覆盖输出文件
        output_path
    ])

    try:
        # 执行 FFmpeg 命令
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=3600  # 设置超时防止卡死
        )
        return output_path
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or "FFmpeg 执行失败"
        return f"音量调整失败: {error_output}"
    except Exception as e:
        return f"发生异常: {str(e)}"


# todo: 存在bug 输出的视频没有声音
@video_mcp.tool(name="add_background_music")
def add_background_music(
        video_path: str,
        audio_path: str,
        time_range: list = None,
        loop_audio: bool = True,
        output_path: str = "output.mp4"
) -> str:
    """
    使用 FFmpeg 给视频添加背景音乐，支持自定义时间范围和循环播放

    参数:
        video_path (str): 输入视频文件的完整路径
        audio_path (str): 输入音频文件的完整路径
        time_range (list, optional): 音频添加的时间范围 [start, end]（秒），默认使用整个视频长度
        loop_audio (bool): 是否循环音频，默认为 True
        output_path (str): 输出视频文件的保存路径，默认为 "output.mp4"

    返回:
        str: 成功返回输出文件路径，失败返回错误原因

    功能:
        1. 支持指定音频添加的时间范围
        2. 支持循环播放音频以匹配视频长度
        3. 自动裁剪超出视频长度的音频
        4. 保持视频流不变，仅处理音频流
        5. 支持覆盖已存在的输出文件

    注意:
        - 需要预先安装 FFmpeg 并配置环境变量
        - 音频格式需兼容视频容器格式
        - 时间范围参数格式为 [start_seconds, end_seconds]
    """
    # 参数验证
    if not os.path.exists(video_path):
        return f"错误：视频文件不存在 - {video_path}"

    if not os.path.exists(audio_path):
        return f"错误：音频文件不存在 - {audio_path}"

    # 获取视频时长
    try:
        video_duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=nw=1", video_path
        ]
        video_duration = float(subprocess.check_output(video_duration_cmd).decode().strip().split("=")[1])
    except (subprocess.CalledProcessError, ValueError) as e:
        return f"无法获取视频时长: {str(e)}"

    # 获取音频时长
    try:
        audio_duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=nw=1", audio_path
        ]
        audio_duration = float(subprocess.check_output(audio_duration_cmd).decode().strip().split("=")[1])
    except (subprocess.CalledProcessError, ValueError) as e:
        return f"无法获取音频时长: {str(e)}"

    # 处理时间范围参数
    if time_range is None:
        start_time = 0
        end_time = video_duration
    else:
        start_time, end_time = time_range
        if start_time < 0:
            return "错误：开始时间不能为负数"
        if end_time > video_duration:
            print(f"警告：结束时间超过视频长度 {video_duration:.2f}s，已自动调整")
            end_time = video_duration

    # 计算音频处理参数
    audio_length = end_time - start_time

    # 构建音频滤镜链
    afilters = []

    # 添加时间范围裁剪
    if time_range is not None:
        afilters.append(f"atrim=0:{audio_length}")
        afilters.append(f"asetpts=PTS+{start_time}/TB")

    # 添加循环处理
    if loop_audio and audio_duration < audio_length:
        loop_count = int(audio_length // audio_duration) + 1
        afilters.append(f"aloop=loop={loop_count}:size={int(audio_duration * 48000)}")  # 假设48kHz采样率

    # 构建 FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",  # 视频流直接复制
        "-c:a", "libmp3lame",  # 使用 MP3 编码器
        "-b:a", "192k",  # 音频码率
        "-map", "0:v",  # 视频流来自第一个输入（视频）
        "-map", "1:a",  # 音频流来自第二个输入（音频）
    ]

    # 添加音频滤镜参数
    if afilters:
        cmd.extend(["-af", ",".join(afilters)])

    # 添加输出参数
    cmd.extend([
        "-preset", "fast",
        "-y",  # 自动覆盖输出文件
        output_path
    ])

    try:
        # 执行 FFmpeg 命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=3600  # 设置超时防止卡死
        )
        return output_path
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or "FFmpeg 执行失败"
        return f"音频叠加失败: {error_output}"
    except Exception as e:
        return f"发生异常: {str(e)}"


@video_mcp.tool(name="adjust_audio_volume")
def adjust_audio_volume(input_audio: str, volume_factor: float, output_audio: str) -> str:
    """
    使用 FFmpeg 调整音频文件的音量大小（支持 0.1-10 倍速）
    功能:
        1. 支持任意音量倍数调整（0.1-10 倍）
        2. 自动选择合适的音频编码器（如 libmp3lame）
        3. 支持覆盖已存在的输出文件
        4. 保留原始音频的采样率和声道配置

    注意:
        - 需要预先安装 FFmpeg 并配置环境变量
        - 输出音频格式由文件扩展名自动确定
        - 音量倍数必须满足 0.1 ≤ volume_factor ≤ 10
        - 默认使用 libmp3lame 编码器，需安装 lame 插件
    :param input_audio: 输入音频文件的完整路径
    :param volume_factor: 音量调整倍数（0.1-1.0 为缩小，1.0-10 为放大）
    :param output_audio: 输出音频文件的保存路径
    :return: 成功返回输出文件路径，失败返回错误原因
    """
    # 参数验证
    if not os.path.exists(input_audio):
        return f"错误：输入文件不存在 - {input_audio}"

    if not (0.1 <= volume_factor <= 10):
        return "错误：音量倍数必须在 0.1 到 10 之间"

    # 获取输入音频的格式
    def get_audio_format(path):
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=format_name", "-of", "default=nw=1", path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "mp3"  # 默认返回 mp3 格式

    input_format = get_audio_format(input_audio)

    # 构建 FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-i", input_audio,
        "-af", f"volume={volume_factor:.2f}",
        "-preset", "fast",
        "-y",  # 自动覆盖输出文件
        output_audio
    ]

    # 根据输出文件扩展名自动选择编码器
    ext = os.path.splitext(output_audio)[1].lower()
    encoders = {
        ".mp3": "libmp3lame",
        ".aac": "aac",
        ".flac": "flac",
        ".wav": "pcm_s16le",  # WAV 使用 PCM 编码
        ".ogg": "libvorbis"
    }

    if ext in encoders:
        cmd.extend(["-c:a", encoders[ext]])
    else:
        cmd.extend(["-c:a", "libmp3lame"])  # 默认使用 MP3 编码器 [[5]]

    try:
        # 执行 FFmpeg 命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=3600  # 设置超时防止卡死
        )
        return output_audio
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or "FFmpeg 执行失败"
        return f"音量调整失败: {error_output}"
    except Exception as e:
        return f"发生异常: {str(e)}"


if __name__ == "__main__":
    video_mcp.run(transport="stdio")
