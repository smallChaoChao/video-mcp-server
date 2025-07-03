# 🎥 Video-MCP-Server  
*A powerful video processing server based on Model Context Protocol (MCP) and FFmpeg*  

[![License](https://img.shields.io/github/license/smallChaoChao/video-mcp-server)](https://github.com/smallChaoChao/video-mcp-server/blob/main/LICENSE)   
[![PyPI Version](https://img.shields.io/pypi/v/video-mcp-server)](https://pypi.org/project/video-mcp-server/)   
[![GitHub Issues](https://img.shields.io/github/issues/smallChaoChao/video-mcp-server)](https://github.com/smallChaoChao/video-mcp-server/issues)   

---

## 🔍 **Overview**  
**Video-MCP-Server** is an open-source video processing tool that leverages the **Model Context Protocol (MCP)** to enable seamless integration with AI agents. Built on top of FFmpeg, it provides a suite of advanced video editing capabilities through natural language commands or programmatic APIs. Ideal for developers, content creators, and AI-driven workflows [[6]](https://github.com/smallChaoChao/video-mcp-server).   

---

## ✨ **Key Features**  
- ✅**Video Concatenation**   
  Merge multiple videos into a single file effortlessly.  
- ✅**Video Rotation**  
  Rotate videos by any angle (90°, 180°, custom degrees).  
- ✅**Scaling & Resolution Adjustment**  
  Resize videos to specific dimensions or scale proportionally.  
- ⏩**Speed Control**  
  Adjust playback speed (slow motion, fast-forward).  
- ✅**Audio Management**  
  Modify volume levels or add background music (BGM).  
- ⏩**Visual Enhancements**  
  Adjust transparency/opacity and overlay subtitles.  
- ⏩**Subtitle Support**  
  Burn SRT/ASS subtitles into videos or apply dynamic text overlays [[10]](https://github.com/smallChaoChao/video-mcp-server).   

---

## 🚀 **Installation**  
### **Via PyPI**  
```bash
pip install video-mcp-server
```
> Note : Ensure FFmpeg is installed and accessible in your system's PATH 
(https://ffmpeg.org/download.html ). 


### **🛠️ Usage** 
#### Start the MCP Server
```bash
uvx video-mcp-server
```
or
```json
{
  "mcpServers": {
    "video-mcp-server": {
      "command": "uvx",
      "args": ["video-mcp-server"]
    }
  }
}
```
### 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

### 📢 Support
For questions, bug reports, or feature requests, please open an issue on GitHub.