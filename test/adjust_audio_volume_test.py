#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : adjust_audio_volume_test.py
# @Time      : 2025/7/3 23:36
# @Author    : smallChaoChao
# @Function  :
from main import adjust_audio_volume

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/dogs.m4a"
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.m4a"
    print(adjust_audio_volume(video_1, 0.5, out_video))
