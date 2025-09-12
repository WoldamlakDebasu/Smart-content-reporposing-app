from flask import Blueprint, request, jsonify
from src.models.content import db, Content, DistributionLog
from src.services.ai_processor import AIProcessor
import threading
import uuid

content_bp = Blueprint('content', __name__)
ai_processor = AIProcessor()

@content_bp.route('/content/upload', methods=['POST'])
def upload_content():
    """Upload new long-form content for processing"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        
        title = data['title']
        content_text = data['content']
        content_format = data.get('format', 'text')
        
        # Create new content record
        content = Content(title=title, original_content=content_text, content_format=content_format)
        db.session.add(content)
        db.session.commit()
        
        # Start AI processing in background thread
        thread = threading.Thread(target=process_content_async, args=(content.id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'content_id': content.id,
            'status': 'processing',
            'message': 'Content uploaded successfully and processing started'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>/status', methods=['GET'])
def get_content_status(content_id):
    """Get processing status and results for content"""
    try:
        content = Content.query.get_or_404(content_id)
        return jsonify(content.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>/distribute', methods=['POST'])
def distribute_content(content_id):
    """Trigger distribution of repurposed content"""
    try:
        content = Content.query.get_or_404(content_id)
        
        if content.status != 'completed':
            return jsonify({'error': 'Content processing not completed yet'}), 400
        
        data = request.get_json()
        platforms = data.get('platforms', [])
        
        if not platforms:
            return jsonify({'error': 'At least one platform must be specified'}), 400
        
        # Create distribution logs
        distribution_logs = []
        for platform in platforms:
            log = DistributionLog(content_id=content_id, platform=platform)
            db.session.add(log)
            distribution_logs.append(log)
        
        db.session.commit()
        
        # Start distribution in background thread
        thread = threading.Thread(target=distribute_content_async, args=(content_id, platforms))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'distribution_id': str(uuid.uuid4()),
            'status': 'scheduled',
            'platforms': platforms,
            'message': 'Distribution scheduled successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content', methods=['GET'])
def list_content():
    """List all content with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        contents = Content.query.order_by(Content.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'contents': [content.to_dict() for content in contents.items],
            'total': contents.total,
            'pages': contents.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_content_async(content_id):
    """Background task to process content with AI"""
    try:
        with db.session.begin():
            content = Content.query.get(content_id)
            if not content:
                return
            
            content.status = 'processing'
            content.progress = 0.1
            db.session.commit()
            
            # Step 1: Analyze content
            content.progress = 0.3
            db.session.commit()
            
            analysis_results = ai_processor.analyze_content(content.original_content)
            content.set_analysis_results(analysis_results)
            content.progress = 0.6
            db.session.commit()
            
            # Step 2: Generate repurposed content
            repurposed_outputs = ai_processor.repurpose_content(content.original_content, analysis_results)
            content.set_repurposed_outputs(repurposed_outputs)
            content.progress = 1.0
            content.status = 'completed'
            db.session.commit()
            
    except Exception as e:
        with db.session.begin():
            content = Content.query.get(content_id)
            if content:
                content.status = 'error'
                content.progress = 0.0
                db.session.commit()
        print(f"Error processing content {content_id}: {str(e)}")

def distribute_content_async(content_id, platforms):
    """Background task to distribute content to platforms"""
    try:
        # Simulate distribution process
        import time
        
        for platform in platforms:
            # Update distribution log
            log = DistributionLog.query.filter_by(content_id=content_id, platform=platform).first()
            if log:
                log.status = 'posting'
                db.session.commit()
                
                # Simulate posting delay
                time.sleep(2)
                
                # Mark as posted
                log.status = 'posted'
                log.posted_time = db.func.now()
                db.session.commit()
                
    except Exception as e:
        print(f"Error distributing content {content_id}: {str(e)}")
        # Mark failed distributions
        for platform in platforms:
            log = DistributionLog.query.filter_by(content_id=content_id, platform=platform).first()
            if log:
                log.status = 'failed'
                log.error_message = str(e)
                db.session.commit()

