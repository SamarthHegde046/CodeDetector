from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import re
import requests
import os
import sys
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
            headers = {"Authorization": "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"}
            response = requests.get(url, headers=headers)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repo contents: {str(e)}")
            return []
    
    @staticmethod
    def get_all_python_files(owner: str, repo: str, path: str = "", max_depth: int = 5) -> List[Dict]:
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
            return response.text
        except Exception as e:
            logger.warning(f"Error downloading file: {str(e)}")
            return None

class CodeAnalyzer:
    """Main class for analyzing code with multiple ML models"""
    
    def __init__(self):
        self.models = {}
        self.vectorizer = None
        self.label_encoder = None
        self.load_models()
    
    def load_models(self):
        """Load all required models and encoders"""
        try:
            model_files = {
                'logistic': 'model/logistic.pkl',
                'random_forest': 'model/randomforest.pkl',
                'gradient_boost': 'model/gradientboost.pkl',
                'xgboost': 'model/xgboost.pkl'
            }
            
            for name, path in model_files.items():
                if Path(path).exists():
                    try:
                        self.models[name] = joblib.load(path)
                        logger.info(f"Loaded model: {name}")
                    except Exception as e:
                        logger.warning(f"Failed to load model {name}: {str(e)}")
                else:
                    logger.warning(f"Model {name} not found at {path}")
            
            if Path('model/vectorizer.pkl').exists():
                self.vectorizer = joblib.load('model/vectorizer.pkl')
                logger.info("Loaded vectorizer")
            else:
                raise Exception("Vectorizer not found!")
            
            if Path('model/labelencoder.pkl').exists():
                self.label_encoder = joblib.load('model/labelencoder.pkl')
                logger.info("Loaded label encoder")
            
            logger.info(f"Successfully loaded {len(self.models)} models")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def predict_with_model(self, X: np.ndarray, model_name: str) -> Optional[ModelResult]:
        """Make prediction with a specific model"""
        if model_name not in self.models:
            return None
            
        try:
            model = self.models[model_name]
            
            if model_name == 'xgboost':
                y_pred = model.predict(X)
                if self.label_encoder:
                    prediction = self.label_encoder.inverse_transform(y_pred)[0]
                else:
                    prediction = "ai" if y_pred[0] == 0 else "human"
            else:
                prediction = model.predict(X)[0]
            
            confidence = float(model.predict_proba(X).max())
            
            return ModelResult(
                name=model_name.replace('_', ' ').title(),
                prediction=prediction,
                confidence=confidence
            )
            
        except Exception as e:
            logger.warning(f"Error with {model_name}: {str(e)}")
            return None
    
    def analyze_code(self, code: str) -> Tuple[List[ModelResult], str, float]:
        """Analyze code with all available models"""
        if not self.vectorizer:
            return [], "Error", 0.0
        
        X = self.vectorizer.transform([code])
        results = []
        
        for model_name in self.models.keys():
            result = self.predict_with_model(X, model_name)
            if result:
                results.append(result)
        
        final_prediction, final_confidence = self.ensemble_vote(results)
        
        return results, final_prediction, final_confidence
    
    def ensemble_vote(self, results: List[ModelResult]) -> Tuple[str, float]:
        """Calculate ensemble prediction using weighted voting"""
        if not results:
            return "unknown", 0.0
        
        ai_votes = [r.confidence for r in results if r.prediction == "ai"]
        human_votes = [r.confidence for r in results if r.prediction == "human"]
        
        ai_score = np.mean(ai_votes) * len(ai_votes) if ai_votes else 0
        human_score = np.mean(human_votes) * len(human_votes) if human_votes else 0
        
        if ai_score > human_score:
            return "ai", float(ai_score / len(results))
        else:
            return "human", float(human_score / len(results))
    
    def analyze_lines(self, code: str, model_name: str = 'gradient_boost') -> List[LineAnalysis]:
        """Perform line-by-line analysis"""
        if model_name not in self.models or not self.vectorizer:
            return []
        
        lines = code.split('\n')
        line_analyses = []
        
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    X_line = self.vectorizer.transform([line])
                    result = self.predict_with_model(X_line, model_name)
                    
                    if result:
                        patterns = self.detect_patterns(line)
                        line_analyses.append(LineAnalysis(
                            line_number=i + 1,
                            content=line,
                            prediction=result.prediction,
                            confidence=result.confidence,
                            patterns=patterns
                        ))
                        
                except Exception:
                    continue
        
        return line_analyses
    
    def analyze_file(self, file_path: str, code: str) -> FileAnalysisResult:
        """Analyze a single file and return results"""
        results, final_pred, final_conf = self.analyze_code(code)
        line_analyses = self.analyze_lines(code, 'gradient_boost')
        
        ai_lines = sum(1 for a in line_analyses if a.prediction == "ai")
        human_lines = sum(1 for a in line_analyses if a.prediction == "human")
        
        return FileAnalysisResult(
            file_path=file_path,
            prediction=final_pred,
            confidence=final_conf,
            line_count=len([l for l in code.split('\n') if l.strip()]),
            ai_lines=ai_lines,
            human_lines=human_lines,
            model_results=[asdict(r) for r in results]
        )
    
    def detect_patterns(self, line: str) -> List[str]:
        """Detect coding patterns in a line"""
        patterns = []
        line = line.strip()
        
        pattern_checks = {
            'function_def': r'^def\s+\w+\s*\(',
            'class_def': r'^class\s+\w+',
            'import_statement': r'^(import|from)\s+',
            'comment': r'^\s*#',
            'loop': r'^\s*(for|while)\s+',
            'conditional': r'^\s*if\s+',
            'print_statement': r'print\s*\(',
            'input_statement': r'input\s*\(',
            'list_comprehension': r'\[.*for.*in.*\]',
            'lambda': r'lambda\s+',
            'exception_handling': r'^\s*(try|except|finally):',
            'docstring': r'""".*"""',
            'f_string': r'f["\'].*\{.*\}.*["\']',
        }
        
        for pattern_name, regex in pattern_checks.items():
            if re.search(regex, line, re.IGNORECASE):
                patterns.append(pattern_name.replace('_', ' ').title())
        
        return patterns

# Initialize analyzer globally
analyzer = None
try:
    logger.info("Initializing CodeAnalyzer...")
    analyzer = CodeAnalyzer()
    logger.info("Models loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load models: {str(e)}")
    logger.error(traceback.format_exc())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if analyzer else 'unhealthy',
        'models_loaded': analyzer is not None and len(analyzer.models) > 0,
        'num_models': len(analyzer.models) if analyzer else 0
    })

@app.route('/api/analyze-code', methods=['POST'])
def analyze_single_code():
    """Analyze a single code snippet"""
    try:
        if not analyzer:
            return jsonify({'error': 'Models not loaded'}), 500
        
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Missing "code" field in request body'}), 400
        
        code = data['code']
        
        if not code.strip():
            return jsonify({'error': 'Code cannot be empty'}), 400
        
        # Analyze code
        results, final_pred, final_conf = analyzer.analyze_code(code)
        line_analyses = analyzer.analyze_lines(code, 'gradient_boost')
        
        # Prepare response
        response = {
            'prediction': final_pred,
            'confidence': final_conf,
            'model_results': [asdict(r) for r in results],
            'statistics': {
                'total_lines': len([l for l in code.split('\n') if l.strip()]),
                'ai_lines': sum(1 for a in line_analyses if a.prediction == "ai"),
                'human_lines': sum(1 for a in line_analyses if a.prediction == "human"),
                'ai_percentage': (sum(1 for a in line_analyses if a.prediction == "ai") / len(line_analyses) * 100) if line_analyses else 0,
                'human_percentage': (sum(1 for a in line_analyses if a.prediction == "human") / len(line_analyses) * 100) if line_analyses else 0
            },
            'line_analyses': [asdict(a) for a in line_analyses[:50]]  # Limit to first 50 lines
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_single_code: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/analyze-repository', methods=['POST'])
def analyze_github_repository():
    """Analyze a GitHub repository"""
    try:
        if not analyzer:
            return jsonify({'error': 'Models not loaded'}), 500
        
        data = request.get_json()
        
        if not data or 'github_url' not in data:
            return jsonify({'error': 'Missing "github_url" field in request body'}), 400
        
        github_url = data['github_url']
        max_files = min(data.get('max_files', 20), 50)  # Limit to 50 files max
        
        # Parse GitHub URL
        owner, repo = GitHubRepoAnalyzer.parse_github_url(github_url)
        
        if not owner or not repo:
            return jsonify({'error': 'Invalid GitHub URL format'}), 400
        
        # Get Python files
        python_files = GitHubRepoAnalyzer.get_all_python_files(owner, repo)
        
        if not python_files:
            return jsonify({'error': 'No Python files found in repository'}), 404
        
        # Analyze files
        file_results = []
        files_to_analyze = python_files[:max_files]
        
        for file_info in files_to_analyze:
            code = GitHubRepoAnalyzer.get_file_content(file_info['download_url'])
            
            if code:
                try:
                    result = analyzer.analyze_file(file_info['path'], code)
                    file_results.append(asdict(result))
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
            'files': file_results
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_github_repository: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'AI vs Human Code Detector API',
        'version': '1.0.0',
        'status': 'running',
        'models_loaded': analyzer is not None and len(analyzer.models) > 0,
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/analyze-code': {
                'method': 'POST',
                'description': 'Analyze a single code snippet',
                'body': {
                    'code': 'string (required) - Python code to analyze'
                }
            },
            '/api/analyze-repository': {
                'method': 'POST',
                'description': 'Analyze a GitHub repository',
                'body': {
                    'github_url': 'string (required) - GitHub repository URL',
                    'max_files': 'integer (optional, default: 20, max: 50) - Maximum files to analyze'
                }
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)