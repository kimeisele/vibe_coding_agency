#!/usr/bin/env python3
"""
API Client - Test File for kdaf-fix
"""
import requests


# Line 15: Hardcoded secret (SEC-003)
API_KEY = 'sk-1234567890abcdef'
BASE_URL = 'https://api.example.com'


def make_request(endpoint, data=None):
    """Make an API request"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    url = f'{BASE_URL}/{endpoint}'
    response = requests.post(url, json=data, headers=headers)

    return response.json()


def get_user_data(user_id):
    """Fetch user data from API"""
    return make_request(f'users/{user_id}')
