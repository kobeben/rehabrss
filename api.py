from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.article import Article, News, db
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/articles', methods=['GET'])
@cross_origin()
def get_articles():
    """获取最新的学术文章，按时间倒序排列"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', None)
        
        query = Article.query
        if category:
            query = query.filter(Article.category == category)
            
        articles = query.order_by(Article.published_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [article.to_dict() for article in articles.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': articles.total,
                'pages': articles.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/news', methods=['GET'])
@cross_origin()
def get_news():
    """获取最新的康复医学新闻，按时间倒序排列"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        news = News.query.order_by(News.published_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in news.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': news.total,
                'pages': news.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """获取统计数据"""
    try:
        article_count = Article.query.count()
        news_count = News.query.count()
        
        # 获取最近7天的文章数量
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_articles = Article.query.filter(Article.created_at >= week_ago).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_articles': article_count,
                'total_news': news_count,
                'recent_articles': recent_articles,
                'last_updated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/search', methods=['GET'])
@cross_origin()
def search():
    """搜索文章和新闻"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
            
        # 搜索文章
        articles = Article.query.filter(
            db.or_(
                Article.title.contains(query),
                Article.title_zh.contains(query)
            )
        ).order_by(Article.published_date.desc()).limit(10).all()
        
        # 搜索新闻
        news = News.query.filter(
            db.or_(
                News.title.contains(query),
                News.content.contains(query)
            )
        ).order_by(News.published_date.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'articles': [article.to_dict() for article in articles],
                'news': [item.to_dict() for item in news]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

