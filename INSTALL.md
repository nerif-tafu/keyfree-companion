# KeyFree Companion - Installation Guide

## 🚀 Quick Start

### Option 1: Run the Executable Directly
1. Download `KeyFreeCompanion.exe`
2. Double-click to run
3. The application will start both the GUI and server automatically
4. No terminal window will appear - the application runs silently
5. **System Tray**: When you minimize the window, it goes to the system tray
6. **Tray Menu**: Right-click the tray icon for options (Show Window, Server Status, Start with Windows, Exit)
7. **Startup Option**: Check the "Start with Windows" checkbox to enable automatic startup

### Option 2: Command Line Usage
```bash
# Start with GUI and server
KeyFreeCompanion.exe start

# Start server only
KeyFreeCompanion.exe server

# Start GUI only (requires server to be running)
KeyFreeCompanion.exe gui

# Test API endpoints
KeyFreeCompanion.exe test
```

## 🔧 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 50MB minimum
- **Storage**: 20MB free space
- **Network**: Local network access (for API calls)

## 🛡️ Security Notes

- The application runs a local web server on port 3000
- No internet access required
- All keyboard simulation is local to your machine
- No data is sent to external servers

## 🎯 Features

- **Single Key**: Press individual keys
- **Duo**: Press 2-key combinations
- **Trio**: Press 3-key combinations  
- **Quartet**: Press 4-key combinations
- **Down/Up**: Hold or release keys
- **String**: Type text strings
- **Delay**: Add delays before actions
- **Key Recording**: Record keys by pressing them
- **cURL Generation**: Generate API commands
- **Server Logs**: View real-time logs
- **System Tray**: Minimize to system tray with right-click menu
- **Startup Integration**: Checkbox to start automatically with Windows

## 🔗 API Endpoints

- `GET /health` - Check server status
- `GET /api/keys` - Get available keys
- `POST /api/single` - Press single key
- `POST /api/duo` - Press 2-key combo
- `POST /api/trio` - Press 3-key combo
- `POST /api/quartet` - Press 4-key combo
- `POST /api/down` - Hold key down
- `POST /api/up` - Release key
- `POST /api/string` - Type text

## 🚨 Troubleshooting

### "Port 3000 already in use"
- Close other applications using port 3000
- Or modify the port in the source code

### "Permission denied"
- Run as Administrator if needed
- Check Windows Defender settings

### "GUI not responding"
- Check if server is running
- Restart the application

### "System Tray Issues"
- Right-click the system tray icon for menu options
- Use "Show Window" to restore the application
- Use "Server Status" to check if the API is running
- Use "Exit" to completely close the application
- **Multiple Minimizes**: The application can be minimized to tray multiple times
- **Custom Icon**: Uses bunny.png icon in system tray
- **Process Name**: Shows as "KeyFree Companion" instead of "python.exe"
- **Startup Integration**: Checkbox to enable/disable automatic Windows startup

## 📞 Support

For issues or questions, please check the main README.md file or create an issue in the repository.

## 📄 License

This software is provided as-is for educational and personal use.
