#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : video_concat_test.py
# @Time      : 2025/7/2 22:39
# @Author    : smallChaoChao
# @Function  :
from main import concat_videos

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_1.mp4"
    video_2 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_2.mp4"
    video_3 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_3.mp4"
    video_list = [video_1, video_2, video_3]
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.mp4"
    print(concat_videos(video_list, out_video))
