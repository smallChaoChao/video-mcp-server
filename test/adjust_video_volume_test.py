#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : adjust_video_volume_test.py
# @Time      : 2025/7/3 23:10
# @Author    : smallChaoChao
# @Function  :
from main import adjust_video_volume

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_1.mp4"
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.mp4"
    print(adjust_video_volume(video_1, 10, out_video))
