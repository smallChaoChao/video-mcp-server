#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : video_resize_test.py
# @Time      : 2025/7/2 23:17
# @Author    : smallChaoChao
# @Function  :
from main import resize_video

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_1.mp4"
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.mp4"
    print(resize_video(video_1, 0.5, out_video))
