"""
Routes for AI-powered summary reports and insights.
"""

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from pathlib import Path
import os

summary_bp = Blueprint('summaries', __name__)


@summary_bp.route('/generate')
@login_required
def generate_summary():
    """Generate and display a weekly summary report."""
    # Only admins and staff can generate summaries
    if current_user.role not in ('admin', 'staff'):
        flash('You do not have permission to generate summaries.', 'error')
        from flask import redirect, url_for
        return redirect(url_for('resources.list_resources'))
    
    try:
        from src.ai.summary_generator import SummaryGenerator
        
        # Get database path
        db_path = Path(__file__).parent.parent.parent / "instance" / "site.db"
        
        # Get LLM configuration from environment or config
        from config import Config
        llm_config = {
            'llm_provider': Config.LLM_PROVIDER,
            'llm_model': Config.LLM_MODEL,
            'api_key': Config.LLM_API_KEY,
            'base_url': Config.OLLAMA_BASE_URL
        }
        
        generator = SummaryGenerator(db_path, llm_config)
        summary = generator.generate_summary()
        insights = generator.generate_insights()
        
        return render_template(
            'admin/summary_report.html',
            summary=summary,
            insights=insights
        )
    
    except Exception as e:
        flash(f'Error generating summary: {str(e)}', 'error')
        import traceback
        print(traceback.format_exc())
        from flask import redirect, url_for
        return redirect(url_for('admin.admin_dashboard'))


@summary_bp.route('/api/insights')
@login_required
def api_insights():
    """API endpoint to get system insights (JSON)."""
    if current_user.role not in ('admin', 'staff'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from src.ai.summary_generator import SummaryGenerator
        
        db_path = Path(__file__).parent.parent.parent / "instance" / "site.db"
        
        from config import Config
        llm_config = {
            'llm_provider': Config.LLM_PROVIDER,
            'llm_model': Config.LLM_MODEL,
            'api_key': Config.LLM_API_KEY,
            'base_url': Config.OLLAMA_BASE_URL
        }
        
        generator = SummaryGenerator(db_path, llm_config)
        insights = generator.generate_insights()
        
        return jsonify(insights)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

