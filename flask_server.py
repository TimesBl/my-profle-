"""
Flask сервер для хранения и отдачи отзывов
Установка: pip install flask flask-cors
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для запросов с фронтенда

# Файл для хранения отзывов
REVIEWS_FILE = 'reviews.json'


def load_reviews():
    """Загрузка отзывов из файла"""
    if not os.path.exists(REVIEWS_FILE):
        return []
    
    try:
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_reviews(reviews):
    """Сохранение отзывов в файл"""
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


@app.route('/')
def home():
    """Главная страница API"""
    return jsonify({
        'status': 'ok',
        'message': 'Timelyx Reviews API',
        'endpoints': {
            'GET /api/reviews': 'Получить все отзывы',
            'POST /api/reviews': 'Добавить новый отзыв',
            'GET /api/stats': 'Получить статистику'
        }
    })


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Получение всех отзывов"""
    reviews = load_reviews()
    # Сортируем по дате (новые первыми)
    reviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    return jsonify(reviews)


@app.route('/api/reviews', methods=['POST'])
def add_review():
    """Добавление нового отзыва"""
    try:
        data = request.get_json()
        
        # Валидация данных
        if not data.get('author'):
            return jsonify({'error': 'Требуется имя автора'}), 400
        
        if not data.get('rating') or not isinstance(data['rating'], int):
            return jsonify({'error': 'Требуется корректный рейтинг'}), 400
        
        if data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'error': 'Рейтинг должен быть от 1 до 5'}), 400
        
        if not data.get('text'):
            return jsonify({'error': 'Требуется текст отзыва'}), 400
        
        # Создаём отзыв
        review = {
            'id': datetime.now().timestamp(),
            'author': data['author'],
            'rating': data['rating'],
            'text': data['text'],
            'date': data.get('date', datetime.now().isoformat()),
            'telegram_id': data.get('telegram_id')
        }
        
        # Загружаем существующие отзывы
        reviews = load_reviews()
        
        # Добавляем новый отзыв
        reviews.append(review)
        
        # Сохраняем
        save_reviews(reviews)
        
        print(f"✅ Новый отзыв добавлен: {review['author']} - {review['rating']}⭐")
        
        return jsonify({
            'status': 'success',
            'message': 'Отзыв успешно добавлен',
            'review': review
        }), 200
    
    except Exception as e:
        print(f"❌ Ошибка при добавлении отзыва: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Удаление отзыва (для администратора)"""
    try:
        reviews = load_reviews()
        review_id = float(review_id)
        
        # Фильтруем отзывы
        reviews = [r for r in reviews if r.get('id') != review_id]
        
        save_reviews(reviews)
        
        return jsonify({
            'status': 'success',
            'message': 'Отзыв удалён'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получение статистики отзывов"""
    reviews = load_reviews()
    
    if not reviews:
        return jsonify({
            'total': 0,
            'average_rating': 0,
            'ratings_count': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        })
    
    total = len(reviews)
    ratings = [r['rating'] for r in reviews]
    average = sum(ratings) / len(ratings)
    
    ratings_count = {i: ratings.count(i) for i in range(1, 6)}
    
    return jsonify({
        'total': total,
        'average_rating': round(average, 2),
        'ratings_count': ratings_count,
        'latest_review': reviews[-1] if reviews else None
    })


@app.route('/api/clear', methods=['POST'])
def clear_reviews():
    """Очистка всех отзывов (для разработки)"""
    try:
        save_reviews([])
        return jsonify({
            'status': 'success',
            'message': 'Все отзывы удалены'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Создаём файл с отзывами, если его нет
    if not os.path.exists(REVIEWS_FILE):
        save_reviews([])
        print("📁 Создан файл для хранения отзывов")

    print("\n" + "="*50)
    print("🚀 Сервер запущен в PRODUCTION режиме (Waitress)")
    print("📍 URL: http://localhost:5000")
    print("📋 Документация API: http://localhost:5000")
    print("="*50 + "\n")

    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
