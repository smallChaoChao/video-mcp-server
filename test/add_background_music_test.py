#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  : add_background_music_test.py
# @Time      : 2025/7/3 23:26
# @Author    : smallChaoChao
# @Function  :
from main import add_background_music

if __name__ == "__main__":
    video_1 = "/Users/chaochao/Python/Projects/video-mcp-server/resource/video_1.mp4"
    music = "/Users/chaochao/Python/Projects/video-mcp-server/resource/dogs.m4a"
    out_video = "/Users/chaochao/Python/Projects/video-mcp-server/resource/result.mp4"
    print(add_background_music(video_1, music,None, True, out_video))
