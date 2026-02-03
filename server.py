from flask import Flask, request, jsonify
from flask_cors import CORS
from keyboard_simulator import KeyboardSimulator
import volume_controller
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize keyboard simulator
keyboard_simulator = KeyboardSimulator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'KeyFree Companion API is running',
        'version': '1.1.0'
    })

@app.route('/api/keys', methods=['GET'])
def get_available_keys():
    """Get list of available keys"""
    try:
        keys = keyboard_simulator.get_available_keys()
        return jsonify({
            'keys': {key: key for key in keys}
        })
    except Exception as e:
        logger.error(f"Error getting available keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/single', methods=['POST'])
def single_key():
    """Send a single key press"""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': 'Key parameter is required'}), 400
        
        key = data['key']
        keyboard_simulator.single(key)
        
        return jsonify({
            'success': True,
            'message': f'Pressed key: {key}'
        })
    except Exception as e:
        logger.error(f"Error in single key: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/duo', methods=['POST'])
def duo_keys():
    """Send a two-key combination"""
    try:
        data = request.get_json()
        if not data or 'key1' not in data or 'key2' not in data:
            return jsonify({'error': 'key1 and key2 parameters are required'}), 400
        
        key1 = data['key1']
        key2 = data['key2']
        keyboard_simulator.duo(key1, key2)
        
        return jsonify({
            'success': True,
            'message': f'Pressed combination: {key1} + {key2}'
        })
    except Exception as e:
        logger.error(f"Error in duo keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trio', methods=['POST'])
def trio_keys():
    """Send a three-key combination"""
    try:
        data = request.get_json()
        if not data or 'key1' not in data or 'key2' not in data or 'key3' not in data:
            return jsonify({'error': 'key1, key2, and key3 parameters are required'}), 400
        
        key1 = data['key1']
        key2 = data['key2']
        key3 = data['key3']
        keyboard_simulator.trio(key1, key2, key3)
        
        return jsonify({
            'success': True,
            'message': f'Pressed combination: {key1} + {key2} + {key3}'
        })
    except Exception as e:
        logger.error(f"Error in trio keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quartet', methods=['POST'])
def quartet_keys():
    """Send a four-key combination"""
    try:
        data = request.get_json()
        if not data or 'key1' not in data or 'key2' not in data or 'key3' not in data or 'key4' not in data:
            return jsonify({'error': 'key1, key2, key3, and key4 parameters are required'}), 400
        
        key1 = data['key1']
        key2 = data['key2']
        key3 = data['key3']
        key4 = data['key4']
        keyboard_simulator.quartet(key1, key2, key3, key4)
        
        return jsonify({
            'success': True,
            'message': f'Pressed combination: {key1} + {key2} + {key3} + {key4}'
        })
    except Exception as e:
        logger.error(f"Error in quartet keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/down', methods=['POST'])
def key_down():
    """Send a key down event"""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': 'Key parameter is required'}), 400
        
        key = data['key']
        keyboard_simulator.down(key)
        
        return jsonify({
            'success': True,
            'message': f'Key down: {key}'
        })
    except Exception as e:
        logger.error(f"Error in key down: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/up', methods=['POST'])
def key_up():
    """Send a key up event"""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': 'Key parameter is required'}), 400
        
        key = data['key']
        keyboard_simulator.up(key)
        
        return jsonify({
            'success': True,
            'message': f'Key up: {key}'
        })
    except Exception as e:
        logger.error(f"Error in key up: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/string', methods=['POST'])
def type_string():
    """Type a string"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text parameter is required'}), 400
        
        text = data['text']
        keyboard_simulator.type_string(text)
        
        return jsonify({
            'success': True,
            'message': f'Typed string: {text}'
        })
    except Exception as e:
        logger.error(f"Error in type string: {str(e)}")
        return jsonify({'error': str(e)}), 500


# --- Volume (per-app) API ---

@app.route('/api/volume/apps', methods=['GET'])
def volume_list_apps():
    """List apps with active audio sessions (name, pid, volume, muted)."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        apps = volume_controller.get_audio_sessions()
        return jsonify({'apps': apps})
    except Exception as e:
        logger.error(f"Error listing volume apps: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/get', methods=['GET', 'POST'])
def volume_get():
    """Get current volume level (0.0-1.0) and mute state for an app.
    GET: ?app=chrome.exe or ?pid=1234
    POST: body {"app": "chrome.exe"} or {"pid": 1234}
    Returns: {"volume": 0.8, "muted": false}
    """
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        if request.method == 'GET':
            data = request.args
        else:
            data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        info = volume_controller.get_volume(identifier)
        if info is None:
            return jsonify({'error': f'App not found: {identifier}'}), 404
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting volume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/set', methods=['POST'])
def volume_set():
    """Set volume for an app. Body: {"app": "chrome.exe", "volume": 0.8} or {"pid": 1234, "volume": 0.5}. volume in 0.0-1.0."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'volume' not in data:
            return jsonify({'error': '"volume" is required (0.0 to 1.0)'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        success, message = volume_controller.set_volume(identifier, data['volume'])
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error setting volume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/up', methods=['POST'])
def volume_up():
    """Increase volume for an app. Body: {"app": "chrome.exe"} or {"app": "chrome.exe", "amount": 0.1}. amount default 0.1."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        amount = data.get('amount', volume_controller.DEFAULT_VOLUME_STEP)
        success, message = volume_controller.volume_up(identifier, amount)
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error increasing volume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/down', methods=['POST'])
def volume_down():
    """Decrease volume for an app. Body: {"app": "chrome.exe"} or {"app": "chrome.exe", "amount": 0.1}."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        amount = data.get('amount', volume_controller.DEFAULT_VOLUME_STEP)
        success, message = volume_controller.volume_down(identifier, amount)
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error decreasing volume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/mute', methods=['POST'])
def volume_mute():
    """Mute an app. Body: {"app": "chrome.exe"} or {"pid": 1234}."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        success, message = volume_controller.mute(identifier)
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error muting: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/unmute', methods=['POST'])
def volume_unmute():
    """Unmute an app. Body: {"app": "chrome.exe"} or {"pid": 1234}."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        success, message = volume_controller.unmute(identifier)
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        logger.error(f"Error unmuting: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/volume/toggle-mute', methods=['POST'])
def volume_toggle_mute():
    """Toggle mute for an app. Body: {"app": "chrome.exe"} or {"pid": 1234}. Returns new muted state."""
    if not volume_controller.is_available():
        return jsonify({'error': 'Per-app volume control is not available (Windows + pycaw required)'}), 503
    try:
        data = request.get_json() or {}
        identifier = data.get('pid') if 'pid' in data else data.get('app')
        if identifier is None:
            return jsonify({'error': 'Either "app" (process name) or "pid" is required'}), 400
        if 'pid' in data:
            try:
                identifier = int(identifier)
            except (TypeError, ValueError):
                return jsonify({'error': 'pid must be an integer'}), 400
        success, message, muted = volume_controller.toggle_mute(identifier)
        if not success:
            return jsonify({'error': message}), 404
        return jsonify({'success': True, 'message': message, 'muted': muted})
    except Exception as e:
        logger.error(f"Error toggling mute: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("KeyFree Companion API server starting...")
    print("Health check: http://localhost:3000/health")
    print("API documentation: http://localhost:3000/api/keys")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=3000, debug=False)
