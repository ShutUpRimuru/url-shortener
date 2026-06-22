from flask import Flask, request, jsonify, redirect
import redis
import hashlib
import validators
import os

app = Flask(__name__)

# Инициализация подключения к Redis
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    original_url = data['url']
    if not validators.url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400

    custom_code = data.get('custom_code')
    
    if custom_code:
        # Проверка кастомного кода
        if not custom_code.replace('-', '').isalnum():
            return jsonify({'error': 'Custom code must contain only letters, numbers, and hyphens'}), 400
        if redis_client.exists(custom_code):
            return jsonify({'error': 'Custom code already exists'}), 409
        short_code = custom_code
    else:
        # Генерация короткого кода из хэша
        short_code = hashlib.md5(original_url.encode()).hexdigest()[:6]

    # Сохранение в Redis
    redis_client.set(short_code, original_url)
    
    short_url = f"http://{request.host}/{short_code}"

    return jsonify({
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url
    }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    original_url = redis_client.get(short_code)
    if original_url:
        return redirect(original_url)
    return jsonify({'error': 'Short URL not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
