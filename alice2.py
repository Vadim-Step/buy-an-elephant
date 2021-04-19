import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id]['sug'] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        sessionStorage[user_id]['animal'] = 'Слон'
        animal = sessionStorage[user_id]['animal']
        res['response']['text'] = f'Привет! Купи {animal}а!'
        res['response']['buttons'] = get_suggests(user_id)

        return
    if 'ладно' in req['request']['original_utterance'].lower() or 'куплю' in req['request'][
        'original_utterance'].lower() or 'покупаю' in req['request'][
        'original_utterance'].lower() or 'хорошо' in req['request']['original_utterance'].lower():
        animal = sessionStorage[user_id]['animal']
        # Пользователь согласился, прощаемся.
        res['response']['text'] = f'Слона можно найти на Яндекс.Маркете!'
        if sessionStorage[user_id]['animal'] == 'Кролик':
            res['response']['end_session'] = True
        else:
            sessionStorage[user_id]['animal'] = 'Кролик'
        return
    animal = sessionStorage[user_id]['animal']
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal}а!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]['sug']

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id]['sug'] = session
    animal = sessionStorage[user_id]['animal']
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animal}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
