from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from simple_policy_search import search

policy_bp = Blueprint('policy', __name__)


@policy_bp.route('/search', methods=['POST'])
@jwt_required(optional=True)
def policy_search():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    top_k = int(data.get('top_k', 5))
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        results = search(query, top_k=top_k)
        return jsonify(results), 200
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": "Search failed"}), 500

