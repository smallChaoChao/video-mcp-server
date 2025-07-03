#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : adjust_video_speed_test.py
# @Time      : 2025/7/3 23:03
# @Author    : smallChaoChao
# @Function  :
from main import adjust_video_speed

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_1.mp4"
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.mp4"
    print(adjust_video_speed(video_1, 0.5, out_video))
