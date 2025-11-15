"""
Auto-Summary Reporter for Campus Resource Hub

Generates weekly summaries and system insights using AI reasoning based on actual database data.
Uses MCP server for safe database queries and supports both local LLMs and API-based models.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import requests
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class DatabaseQuery:
    """Helper class to query database directly (alternative to MCP for internal use).
    Supports both SQLite (local) and PostgreSQL (production) via SQLAlchemy."""
    
    def __init__(self, db_path: Union[Path, Engine, None] = None, engine: Optional[Engine] = None):
        """
        Initialize database query handler.
        
        Args:
            db_path: Path to SQLite database file (for local development)
            engine: SQLAlchemy engine (for production PostgreSQL)
        """
        self.db_path = db_path
        self.engine = engine
        
        # If engine is provided, use it (production)
        # Otherwise, use db_path for SQLite (local)
        if engine is not None:
            self.use_sqlalchemy = True
        elif db_path and isinstance(db_path, Engine):
            self.engine = db_path
            self.use_sqlalchemy = True
        else:
            self.use_sqlalchemy = False
    
    @contextmanager
    def get_connection(self):
        """Get a read-only database connection."""
        if self.use_sqlalchemy:
            # Use SQLAlchemy engine (PostgreSQL in production)
            conn = self.engine.connect()
            try:
                yield conn
            finally:
                conn.close()
        else:
            # Use SQLite directly (local development)
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as dictionaries."""
        if self.use_sqlalchemy:
            # Use SQLAlchemy for PostgreSQL (or SQLite via SQLAlchemy)
            with self.engine.connect() as conn:
                if params:
                    # SQLAlchemy text() can handle ? placeholders, but we need to bind them
                    # Convert tuple to list for bindparam, or use positional binding
                    # For compatibility, convert ? to :param style
                    
                    # Check if query uses ? placeholders (SQLite style)
                    if '?' in query:
                        # Convert ? placeholders to named parameters
                        param_dict = {}
                        modified_query = query
                        param_index = 0
                        while '?' in modified_query:
                            param_name = f'param_{param_index}'
                            modified_query = modified_query.replace('?', f':{param_name}', 1)
                            param_dict[param_name] = params[param_index]
                            param_index += 1
                        result = conn.execute(text(modified_query), param_dict)
                    else:
                        # Already using named parameters
                        if isinstance(params, tuple):
                            # Convert tuple to dict if needed
                            param_dict = {f'param_{i}': p for i, p in enumerate(params)}
                            result = conn.execute(text(query), param_dict)
                        else:
                            result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        else:
            # Use SQLite directly
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]


class LLMClient:
    """LLM client supporting both local (Ollama) and API-based models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('llm_provider', 'gemini')  # 'gemini', 'ollama', 'openai', 'anthropic'
        self.model = config.get('llm_model', 'gemini-2.0-flash')
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'http://localhost:11434')  # Default Ollama
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the configured LLM."""
        if self.provider == 'gemini':
            return self._generate_gemini(prompt, system_prompt)
        elif self.provider == 'ollama':
            return self._generate_ollama(prompt, system_prompt)
        elif self.provider == 'openai':
            return self._generate_openai(prompt, system_prompt)
        elif self.provider == 'anthropic':
            return self._generate_anthropic(prompt, system_prompt)
        else:
            # Fallback: return a simple template-based summary
            return self._generate_fallback(prompt)
    
    def _generate_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Google Gemini API."""
        try:
            if not self.api_key:
                raise ValueError("Gemini API key is required")
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Ensure model name includes 'models/' prefix (required by Gemini API)
            model_name = self.model
            if not model_name.startswith('models/'):
                model_name = f"models/{model_name}"
            
            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']
            
            # Fallback if response structure is different
            if 'error' in result:
                error_msg = result['error'].get('message', 'Unknown error')
                raise Exception(f"Gemini API error: {error_msg}")
            
            return str(result)
        except requests.exceptions.HTTPError as e:
            error_msg = "Unknown error"
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
            except:
                error_msg = str(e)
            print(f"Gemini HTTP error: {error_msg}")
            return self._generate_fallback(prompt)
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Ollama (local LLM)."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt or "You are a helpful assistant that generates data-driven summaries.",
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print(f"Ollama generation error: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using OpenAI API."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model or "gpt-4",
                "messages": messages,
                "temperature": 0.7
            }
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Anthropic Claude API."""
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model or "claude-3-sonnet-20240229",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text']
        except Exception as e:
            print(f"Anthropic generation error: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Fallback template-based summary when LLM is unavailable."""
        # Extract key information from prompt if it contains data
        if "Top 5 Most Reserved Resources" in prompt:
            return "Summary generation requires LLM configuration. Please configure Ollama, OpenAI, or Anthropic API."
        return "AI summary generation is currently unavailable. Please configure an LLM provider."


class SummaryGenerator:
    """Generates weekly summaries and system insights from database data."""
    
    def __init__(self, db_path: Union[Path, Engine, None] = None, llm_config: Dict[str, Any] = None, engine: Optional[Engine] = None):
        """
        Initialize summary generator.
        
        Args:
            db_path: Path to SQLite database file (for local development)
            llm_config: Configuration for LLM client
            engine: SQLAlchemy engine (for production PostgreSQL) - takes precedence over db_path
        """
        self.db = DatabaseQuery(db_path=db_path, engine=engine)
        self.llm = LLMClient(llm_config or {})
    
    def get_weekly_data(self) -> Dict[str, Any]:
        """Collect data for the past week."""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Top resources by bookings
        top_resources_query = """
            SELECT 
                r.resource_id,
                r.title,
                r.category,
                r.location,
                COUNT(b.booking_id) as booking_count
            FROM resources r
            LEFT JOIN bookings b ON r.resource_id = b.resource_id 
                AND b.created_at >= ? 
                AND b.status IN ('approved', 'pending')
            WHERE r.status = 'published'
            GROUP BY r.resource_id, r.title, r.category, r.location
            ORDER BY booking_count DESC
            LIMIT 5
        """
        top_resources = self.db.execute_query(top_resources_query, (week_ago.isoformat(),))
        
        # Booking statistics
        booking_stats_query = """
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM bookings
            WHERE created_at >= ?
        """
        booking_stats = self.db.execute_query(booking_stats_query, (week_ago.isoformat(),))
        
        # User activity
        user_activity_query = """
            SELECT 
                COUNT(DISTINCT requester_id) as active_users,
                COUNT(*) as total_bookings
            FROM bookings
            WHERE created_at >= ?
        """
        user_activity = self.db.execute_query(user_activity_query, (week_ago.isoformat(),))
        
        # Resource categories breakdown
        category_query = """
            SELECT 
                r.category,
                COUNT(DISTINCT r.resource_id) as resource_count,
                COUNT(b.booking_id) as booking_count
            FROM resources r
            LEFT JOIN bookings b ON r.resource_id = b.resource_id 
                AND b.created_at >= ?
            WHERE r.status = 'published'
            GROUP BY r.category
            ORDER BY booking_count DESC
        """
        categories = self.db.execute_query(category_query, (week_ago.isoformat(),))
        
        # Reviews and ratings
        reviews_query = """
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                COUNT(DISTINCT resource_id) as resources_reviewed
            FROM reviews
            WHERE timestamp >= ?
        """
        reviews = self.db.execute_query(reviews_query, (week_ago.isoformat(),))
        
        return {
            'top_resources': top_resources,
            'booking_stats': booking_stats[0] if booking_stats else {},
            'user_activity': user_activity[0] if user_activity else {},
            'categories': categories,
            'reviews': reviews[0] if reviews else {},
            'period_start': week_ago.isoformat(),
            'period_end': datetime.now().isoformat()
        }
    
    def generate_summary(self, summary_type: str = 'weekly') -> Dict[str, Any]:
        """Generate an AI-powered summary report."""
        data = self.get_weekly_data()
        
        # Format data for LLM
        data_summary = f"""
Database Statistics (Past 7 Days):

Top 5 Most Reserved Resources:
{json.dumps(data['top_resources'], indent=2, default=str)}

Booking Statistics:
- Total Bookings: {data['booking_stats'].get('total_bookings', 0)}
- Approved: {data['booking_stats'].get('approved', 0)}
- Pending: {data['booking_stats'].get('pending', 0)}
- Rejected: {data['booking_stats'].get('rejected', 0)}

User Activity:
- Active Users: {data['user_activity'].get('active_users', 0)}
- Total Bookings: {data['user_activity'].get('total_bookings', 0)}

Category Breakdown:
{json.dumps(data['categories'], indent=2, default=str)}

Reviews:
- Total Reviews: {data['reviews'].get('total_reviews', 0)}
- Average Rating: {round(data['reviews'].get('avg_rating', 0), 2) if data['reviews'].get('avg_rating') else 0}
- Resources Reviewed: {data['reviews'].get('resources_reviewed', 0)}
"""
        
        system_prompt = """You are a data analyst generating weekly summaries for a campus resource booking system. 
Your summaries must be:
1. Based ONLY on the provided data - never fabricate information
2. Clear and actionable insights
3. Professional but engaging
4. Focused on trends and patterns in the data

Format your response as a structured report with sections."""
        
        user_prompt = f"""Generate a comprehensive weekly summary report based on this data:

{data_summary}

Create a report with:
1. Executive Summary (2-3 sentences)
2. Top 5 Most Reserved Resources (with insights)
3. Booking Trends (approvals, pending, etc.)
4. User Activity Insights
5. Category Analysis
6. Key Takeaways and Recommendations

Be specific and reference actual numbers from the data."""
        
        ai_summary = self.llm.generate(user_prompt, system_prompt)
        
        return {
            'summary_type': summary_type,
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': data['period_start'],
                'end': data['period_end']
            },
            'data': data,
            'ai_summary': ai_summary,
            'raw_data_summary': data_summary
        }
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate system insights and recommendations."""
        data = self.get_weekly_data()
        
        # Calculate insights
        insights = []
        
        # Most popular resource
        if data['top_resources']:
            top = data['top_resources'][0]
            insights.append({
                'type': 'most_popular',
                'title': 'Most Popular Resource',
                'description': f"{top['title']} received {top['booking_count']} bookings this week.",
                'resource_id': top['resource_id']
            })
        
        # Booking approval rate
        total = data['booking_stats'].get('total_bookings', 0)
        approved = data['booking_stats'].get('approved', 0)
        if total > 0:
            approval_rate = (approved / total) * 100
            insights.append({
                'type': 'approval_rate',
                'title': 'Booking Approval Rate',
                'description': f"{approval_rate:.1f}% of bookings were approved this week.",
                'value': approval_rate
            })
        
        # Category insights
        if data['categories']:
            top_category = data['categories'][0]
            insights.append({
                'type': 'top_category',
                'title': 'Most Active Category',
                'description': f"{top_category['category']} had {top_category['booking_count']} bookings across {top_category['resource_count']} resources.",
                'category': top_category['category']
            })
        
        # User engagement
        active_users = data['user_activity'].get('active_users', 0)
        total_bookings = data['user_activity'].get('total_bookings', 0)
        if active_users > 0:
            avg_bookings = total_bookings / active_users
            insights.append({
                'type': 'user_engagement',
                'title': 'User Engagement',
                'description': f"Average of {avg_bookings:.1f} bookings per active user this week.",
                'value': avg_bookings
            })
        
        return {
            'insights': insights,
            'generated_at': datetime.now().isoformat(),
            'data': data
        }

