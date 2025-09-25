from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from src.models.content import DistributionLog, db
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/overview', methods=['GET'])
@login_required
def get_analytics_overview():
    """Get analytics overview for the current user"""
    try:
        # Total content processed
        total_content = db.session.query(func.count(DistributionLog.content_id.distinct())).filter(
            DistributionLog.user_id == current_user.id
        ).scalar() or 0

        # Distribution stats
        distribution_stats = db.session.query(
            DistributionLog.platform,
            func.count(DistributionLog.id).label('total'),
            func.sum(func.case((DistributionLog.status == 'posted', 1), else_=0)).label('successful'),
            func.sum(func.case((DistributionLog.status == 'failed', 1), else_=0)).label('failed')
        ).filter(DistributionLog.user_id == current_user.id).group_by(DistributionLog.platform).all()

        stats = {}
        for stat in distribution_stats:
            stats[stat.platform] = {
                'total': stat.total,
                'successful': stat.successful or 0,
                'failed': stat.failed or 0,
                'success_rate': round((stat.successful or 0) / stat.total * 100, 2) if stat.total > 0 else 0
            }

        return jsonify({
            'total_content': total_content,
            'platform_stats': stats,
            'subscription_status': current_user.subscription_status
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/posts/<platform>', methods=['GET'])
@login_required
def get_platform_posts(platform):
    """Get recent posts for a specific platform"""
    try:
        posts = DistributionLog.query.filter_by(
            user_id=current_user.id,
            platform=platform.lower()
        ).order_by(DistributionLog.created_at.desc()).limit(10).all()

        return jsonify([{
            'id': post.id,
            'status': post.status,
            'post_id': post.post_id,
            'post_url': post.post_url,
            'error_message': post.error_message,
            'created_at': post.created_at.isoformat()
        } for post in posts]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500