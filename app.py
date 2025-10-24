from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import re
import requests
import os
import gc
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for MERN frontend

@dataclass
class ModelResult:
    """Data class for storing model prediction results"""
    name: str
    prediction: str
    confidence: float

@dataclass
class LineAnalysis:
    """Data class for storing line-by-line analysis results"""
    line_number: int
    content: str
    prediction: str
    confidence: float
    patterns: List[str]

@dataclass
class FileAnalysisResult:
    """Data class for storing file analysis results"""
    file_path: str
    prediction: str
    confidence: float
    line_count: int
    ai_lines: int
    human_lines: int
    model_results: List[Dict]

class GitHubRepoAnalyzer:
    """Class for analyzing GitHub repositories"""
    
    # GitHub token from environment (optional, for higher rate limits)
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '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')
    
    @staticmethod
    def parse_github_url(url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse GitHub URL to extract owner and repo name"""
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$',
            r'github\.com/([^/]+)/([^/]+)/tree/',
            r'github\.com/([^/]+)/([^/]+)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2).replace('.git', '')
        
        return None, None
    
    @staticmethod
    def get_repo_contents(owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get contents of a GitHub repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        try:
            headers = {}
            if GitHubRepoAnalyzer.GITHUB_TOKEN:
                headers["Authorization"] = f"token {GitHubRepoAnalyzer.GITHUB_TOKEN}"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repo contents: {str(e)}")
            return []
    
    @staticmethod
    def get_all_python_files(owner: str, repo: str, path: str = "", max_depth: int = 3) -> List[Dict]:
        """Recursively get all Python files from repository"""
        if max_depth <= 0:
            return []
            
        python_files = []
        contents = GitHubRepoAnalyzer.get_repo_contents(owner, repo, path)
        
        if not contents:
            return python_files
        
        for item in contents:
            try:
                if item['type'] == 'file' and item['name'].endswith('.py'):
                    python_files.append(item)
                elif item['type'] == 'dir':
                    # Skip common directories to save memory
                    skip_dirs = ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 'env']
                    if item['name'] not in skip_dirs:
                        subdir_files = GitHubRepoAnalyzer.get_all_python_files(
                            owner, repo, item['path'], max_depth - 1
                        )
                        python_files.extend(subdir_files)
            except Exception as e:
                logger.warning(f"Error processing item: {str(e)}")
                continue
        
        return python_files
    
    @staticmethod
    def get_file_content(download_url: str) -> Optional[str]:
        """Download and decode file content"""
        try:
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # Limit file size to prevent memory issues (max 50KB)
            if len(content) > 50000:
                logger.warning(f"File too large, truncating: {download_url}")
                content = content[:50000]
            
            return content
        except Exception as e:
            logger.warning(f"Error downloading file: {str(e)}")
            return None

class CodeAnalyzer:
    """Optimized analyzer using only Gradient Boosting model"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        """Load only Gradient Boosting model and vectorizer"""
        try:
            # Load only gradient boosting model (most accurate single model)
            model_path = 'model/gradientboost.pkl'
            if Path(model_path).exists():
                self.model = joblib.load(model_path)
                logger.info("✓ Loaded Gradient Boosting model")
            else:
                raise Exception(f"Model not found at {model_path}")
            
            # Load vectorizer
            vectorizer_path = 'model/vectorizer.pkl'
            if Path(vectorizer_path).exists():
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info("✓ Loaded vectorizer")
            else:
                raise Exception(f"Vectorizer not found at {vectorizer_path}")
            
            logger.info("✓ Models loaded successfully (Memory Optimized Mode)")
            
            # Force garbage collection to free memory
            gc.collect()
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[str, float]:
        """Make prediction with the model"""
        if not self.model:
            return "unknown", 0.0
            
        try:
            prediction = self.model.predict(X)[0]
            confidence = float(self.model.predict_proba(X).max())
            
            return prediction, confidence
            
        except Exception as e:
            logger.warning(f"Error during prediction: {str(e)}")
            return "unknown", 0.0
    
    def analyze_code(self, code: str) -> Tuple[str, float]:
        """Analyze code with gradient boosting model"""
        if not self.vectorizer or not self.model:
            return "Error", 0.0
        
        try:
            X = self.vectorizer.transform([code])
            prediction, confidence = self.predict(X)
            
            # Clean up to save memory
            del X
            gc.collect()
            
            return prediction, confidence
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return "Error", 0.0
    
    def analyze_lines(self, code: str, max_lines: int = 100) -> List[LineAnalysis]:
        """Perform line-by-line analysis (limited for memory efficiency)"""
        if not self.model or not self.vectorizer:
            return []
        
        lines = code.split('\n')
        line_analyses = []
        
        # Limit number of lines analyzed to save memory
        lines_to_analyze = [l for l in lines if l.strip()][:max_lines]
        
        for i, line in enumerate(lines_to_analyze):
            try:
                X_line = self.vectorizer.transform([line])
                prediction, confidence = self.predict(X_line)
                
                patterns = self.detect_patterns(line)
                line_analyses.append(LineAnalysis(
                    line_number=i + 1,
                    content=line[:100],  # Truncate long lines
                    prediction=prediction,
                    confidence=confidence,
                    patterns=patterns
                ))
                
                # Clean up
                del X_line
                
            except Exception:
                continue
        
        # Force garbage collection
        gc.collect()
        
        return line_analyses
    
    def analyze_file(self, file_path: str, code: str) -> FileAnalysisResult:
        """Analyze a single file and return results"""
        # Limit code size for analysis
        if len(code) > 50000:
            code = code[:50000]
            logger.warning(f"Truncated large file: {file_path}")
        
        prediction, confidence = self.analyze_code(code)
        line_analyses = self.analyze_lines(code, max_lines=30)
        
        ai_lines = sum(1 for a in line_analyses if a.prediction == "ai")
        human_lines = sum(1 for a in line_analyses if a.prediction == "human")
        
        result = FileAnalysisResult(
            file_path=file_path,
            prediction=prediction,
            confidence=confidence,
            line_count=len([l for l in code.split('\n') if l.strip()]),
            ai_lines=ai_lines,
            human_lines=human_lines,
            model_results=[{
                'name': 'Gradient Boosting',
                'prediction': prediction,
                'confidence': confidence
            }]
        )
        
        # Clean up
        del code
        gc.collect()
        
        return result
    
    def detect_patterns(self, line: str) -> List[str]:
        """Detect coding patterns in a line"""
        patterns = []
        line = line.strip()
        
        # Simplified pattern checks
        pattern_checks = {
            'function_def': r'^def\s+\w+',
            'class_def': r'^class\s+\w+',
            'import': r'^(import|from)\s+',
            'loop': r'^\s*(for|while)\s+',
            'conditional': r'^\s*if\s+',
        }
        
        for pattern_name, regex in pattern_checks.items():
            if re.search(regex, line, re.IGNORECASE):
                patterns.append(pattern_name.replace('_', ' ').title())
        
        return patterns

# Initialize analyzer globally
analyzer = None
try:
    logger.info("Initializing CodeAnalyzer (Memory Optimized)...")
    analyzer = CodeAnalyzer()
    logger.info("✓ Analyzer ready!")
except Exception as e:
    logger.error(f"Failed to load analyzer: {str(e)}")
    logger.error(traceback.format_exc())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if analyzer else 'unhealthy',
        'model_loaded': analyzer is not None and analyzer.model is not None,
        'model_type': 'Gradient Boosting (Optimized)',
        'memory_mode': 'low'
    })

@app.route('/api/analyze-code', methods=['POST'])
def analyze_single_code():
    """Analyze a single code snippet"""
    try:
        if not analyzer:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Missing "code" field in request body'}), 400
        
        code = data['code']
        
        if not code.strip():
            return jsonify({'error': 'Code cannot be empty'}), 400
        
        # Limit code size
        if len(code) > 100000:
            return jsonify({'error': 'Code too large (max 100KB)'}), 400
        
        # Analyze code
        prediction, confidence = analyzer.analyze_code(code)
        line_analyses = analyzer.analyze_lines(code, max_lines=50)
        
        # Prepare response
        response = {
            'prediction': prediction,
            'confidence': confidence,
            'model': 'Gradient Boosting',
            'statistics': {
                'total_lines': len([l for l in code.split('\n') if l.strip()]),
                'ai_lines': sum(1 for a in line_analyses if a.prediction == "ai"),
                'human_lines': sum(1 for a in line_analyses if a.prediction == "human"),
                'lines_analyzed': len(line_analyses),
                'ai_percentage': (sum(1 for a in line_analyses if a.prediction == "ai") / len(line_analyses) * 100) if line_analyses else 0,
                'human_percentage': (sum(1 for a in line_analyses if a.prediction == "human") / len(line_analyses) * 100) if line_analyses else 0
            },
            'line_analyses': [asdict(a) for a in line_analyses]
        }
        
        # Clean up
        del code
        gc.collect()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_single_code: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/analyze-repository', methods=['POST'])
def analyze_github_repository():
    """Analyze a GitHub repository (memory optimized)"""
    try:
        if not analyzer:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        if not data or 'github_url' not in data:
            return jsonify({'error': 'Missing "github_url" field in request body'}), 400
        
        github_url = data['github_url']
        max_files = min(data.get('max_files', 15), 20)  # Reduced limit for free tier
        
        # Parse GitHub URL
        owner, repo = GitHubRepoAnalyzer.parse_github_url(github_url)
        
        if not owner or not repo:
            return jsonify({'error': 'Invalid GitHub URL format'}), 400
        
        logger.info(f"Analyzing repository: {owner}/{repo}")
        
        # Get Python files
        python_files = GitHubRepoAnalyzer.get_all_python_files(owner, repo)
        
        if not python_files:
            return jsonify({'error': 'No Python files found in repository'}), 404
        
        logger.info(f"Found {len(python_files)} Python files")
        
        # Analyze files
        file_results = []
        files_to_analyze = python_files[:max_files]
        
        for idx, file_info in enumerate(files_to_analyze):
            logger.info(f"Analyzing file {idx+1}/{len(files_to_analyze)}: {file_info['path']}")
            
            code = GitHubRepoAnalyzer.get_file_content(file_info['download_url'])
            
            if code:
                try:
                    result = analyzer.analyze_file(file_info['path'], code)
                    file_results.append(asdict(result))
                    
                    # Clean up after each file
                    del code
                    gc.collect()
                    
                except Exception as e:
                    logger.warning(f"Error analyzing {file_info['path']}: {str(e)}")
        
        if not file_results:
            return jsonify({'error': 'Failed to analyze any files'}), 500
        
        # Calculate repository summary
        total_files = len(file_results)
        ai_files = sum(1 for f in file_results if f['prediction'] == "ai")
        human_files = total_files - ai_files
        
        avg_confidence = float(np.mean([f['confidence'] for f in file_results]))
        total_lines = sum(f['line_count'] for f in file_results)
        total_ai_lines = sum(f['ai_lines'] for f in file_results)
        total_human_lines = sum(f['human_lines'] for f in file_results)
        
        response = {
            'repository': {
                'owner': owner,
                'name': repo,
                'url': github_url
            },
            'summary': {
                'total_files_found': len(python_files),
                'files_analyzed': total_files,
                'ai_files': ai_files,
                'human_files': human_files,
                'ai_percentage': (ai_files / total_files) * 100,
                'human_percentage': (human_files / total_files) * 100,
                'avg_confidence': avg_confidence,
                'total_lines': total_lines,
                'total_ai_lines': total_ai_lines,
                'total_human_lines': total_human_lines,
                'ai_lines_percentage': (total_ai_lines / (total_ai_lines + total_human_lines) * 100) if (total_ai_lines + total_human_lines) > 0 else 0,
                'human_lines_percentage': (total_human_lines / (total_ai_lines + total_human_lines) * 100) if (total_ai_lines + total_human_lines) > 0 else 0
            },
            'files': file_results,
            'note': 'Optimized for free tier (single model, limited files)'
        }
        
        # Final cleanup
        gc.collect()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_github_repository: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'AI vs Human Code Detector API',
        'version': '1.0.0 (Memory Optimized)',
        'status': 'running',
        'model_loaded': analyzer is not None and analyzer.model is not None,
        'model_type': 'Gradient Boosting Only',
        'memory_optimization': 'Enabled for Render Free Tier',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/analyze-code': {
                'method': 'POST',
                'description': 'Analyze a single code snippet',
                'body': {
                    'code': 'string (required) - Python code to analyze (max 100KB)'
                },
                'limits': 'Max 100 lines analyzed, 100KB code size'
            },
            '/api/analyze-repository': {
                'method': 'POST',
                'description': 'Analyze a GitHub repository',
                'body': {
                    'github_url': 'string (required) - GitHub repository URL',
                    'max_files': 'integer (optional, default: 10, max: 20) - Maximum files to analyze'
                },
                'limits': 'Max 20 files, 50KB per file, 100 lines per file analyzed'
            }
        }
    })

# Memory cleanup before request
@app.before_request
def before_request():
    gc.collect()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Single worker, no debug mode for production
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)