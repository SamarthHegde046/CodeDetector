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

# Supported languages and their file extensions
SUPPORTED_LANGUAGES = {
    'python': ['.py'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'java': ['.java']
}

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
    language: str
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
    def detect_language(filename: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(filename).suffix.lower()
        for language, extensions in SUPPORTED_LANGUAGES.items():
            if ext in extensions:
                return language
        return None
    
    @staticmethod
    def get_repo_contents(owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get contents of a GitHub repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}" 

        try:
            headers = {"Authorization": "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"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repo contents: {str(e)}")
            return []
    
    @staticmethod
    def get_all_code_files(owner: str, repo: str, path: str = "", max_depth: int = 3, 
                          languages: List[str] = None) -> List[Dict]:
        """Recursively get all code files from repository"""
        if max_depth <= 0:
            return []
        
        if languages is None:
            languages = list(SUPPORTED_LANGUAGES.keys())
        
        code_files = []
        contents = GitHubRepoAnalyzer.get_repo_contents(owner, repo, path)
        
        if not contents:
            return code_files
        
        # Get all valid extensions for selected languages
        valid_extensions = []
        for lang in languages:
            valid_extensions.extend(SUPPORTED_LANGUAGES.get(lang, []))
        
        for item in contents:
            try:
                if item['type'] == 'file':
                    ext = Path(item['name']).suffix.lower()
                    if ext in valid_extensions:
                        language = GitHubRepoAnalyzer.detect_language(item['name'])
                        if language:
                            item['language'] = language
                            code_files.append(item)
                elif item['type'] == 'dir':
                    # Skip common directories to save memory
                    skip_dirs = ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 
                                'env', 'build', 'dist', 'target', 'out']
                    if item['name'] not in skip_dirs:
                        subdir_files = GitHubRepoAnalyzer.get_all_code_files(
                            owner, repo, item['path'], max_depth - 1, languages
                        )
                        code_files.extend(subdir_files)
            except Exception as e:
                logger.warning(f"Error processing item: {str(e)}")
                continue
        
        return code_files
    
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
    """Multi-language analyzer using Gradient Boosting model"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        """Load Gradient Boosting model and vectorizer"""
        try:
            # Load gradient boosting model (trained for Python, Java, JavaScript)
            model_path = 'model/gradientboost.pkl'
            if Path(model_path).exists():
                self.model = joblib.load(model_path)
                logger.info("✓ Loaded Gradient Boosting model (Python, Java, JavaScript)")
            else:
                raise Exception(f"Model not found at {model_path}")
            
            # Load vectorizer
            vectorizer_path = 'model/vectorizer.pkl'
            if Path(vectorizer_path).exists():
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info("✓ Loaded vectorizer")
            else:
                raise Exception(f"Vectorizer not found at {vectorizer_path}")
            
            logger.info("✓ Multi-language analyzer ready! (Memory Optimized Mode)")
            
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
    
    def analyze_code(self, code: str, language: str = 'python') -> Tuple[str, float]:
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
    
    def analyze_lines(self, code: str, language: str = 'python', max_lines: int = 100) -> List[LineAnalysis]:
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
                
                patterns = self.detect_patterns(line, language)
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
    
    def analyze_file(self, file_path: str, code: str, language: str = 'python') -> FileAnalysisResult:
        """Analyze a single file and return results"""
        # Limit code size for analysis
        if len(code) > 50000:
            code = code[:50000]
            logger.warning(f"Truncated large file: {file_path}")
        
        prediction, confidence = self.analyze_code(code, language)
        line_analyses = self.analyze_lines(code, language, max_lines=30)
        
        ai_lines = sum(1 for a in line_analyses if a.prediction == "ai")
        human_lines = sum(1 for a in line_analyses if a.prediction == "human")
        
        result = FileAnalysisResult(
            file_path=file_path,
            language=language,
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
    
    def detect_patterns(self, line: str, language: str = 'python') -> List[str]:
        """Detect coding patterns in a line based on language"""
        patterns = []
        line = line.strip()
        
        if language == 'python':
            pattern_checks = {
                'function_def': r'^def\s+\w+',
                'class_def': r'^class\s+\w+',
                'import': r'^(import|from)\s+',
                'loop': r'^\s*(for|while)\s+',
                'conditional': r'^\s*if\s+',
                'list_comprehension': r'\[.*for.*in.*\]',
                'decorator': r'^@\w+',
            }
        elif language == 'javascript':
            pattern_checks = {
                'function_def': r'^(function|const|let|var)\s+\w+\s*=\s*(function|\()',
                'arrow_function': r'=>',
                'class_def': r'^class\s+\w+',
                'import': r'^(import|require)',
                'export': r'^export\s+(default|const|function|class)',
                'loop': r'^\s*(for|while)\s*\(',
                'conditional': r'^\s*if\s*\(',
                'async_await': r'(async|await)',
            }
        elif language == 'java':
            pattern_checks = {
                'class_def': r'^(public|private|protected)?\s*(class|interface|enum)\s+\w+',
                'method_def': r'^(public|private|protected|static)?\s+\w+\s+\w+\s*\(',
                'import': r'^import\s+',
                'annotation': r'^@\w+',
                'loop': r'^\s*(for|while)\s*\(',
                'conditional': r'^\s*if\s*\(',
                'exception': r'(try|catch|finally|throw|throws)',
            }
        else:
            # Generic patterns
            pattern_checks = {
                'function': r'\bfunction\b|\bdef\b',
                'class': r'\bclass\b',
                'import': r'\bimport\b|\brequire\b',
                'loop': r'\b(for|while)\b',
                'conditional': r'\bif\b',
            }
        
        for pattern_name, regex in pattern_checks.items():
            if re.search(regex, line, re.IGNORECASE):
                patterns.append(pattern_name.replace('_', ' ').title())
        
        return patterns

# Initialize analyzer globally
analyzer = None
try:
    logger.info("Initializing Multi-Language CodeAnalyzer (Memory Optimized)...")
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
        'model_type': 'Gradient Boosting (Multi-Language)',
        'supported_languages': list(SUPPORTED_LANGUAGES.keys()),
        'memory_mode': 'low'
    })

@app.route('/api/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported programming languages"""
    return jsonify({
        'supported_languages': [
            {
                'name': 'Python',
                'key': 'python',
                'extensions': SUPPORTED_LANGUAGES['python']
            },
            {
                'name': 'JavaScript',
                'key': 'javascript',
                'extensions': SUPPORTED_LANGUAGES['javascript']
            },
            {
                'name': 'Java',
                'key': 'java',
                'extensions': SUPPORTED_LANGUAGES['java']
            }
        ]
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
        language = data.get('language', 'python').lower()
        
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': f'Unsupported language: {language}',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        if not code.strip():
            return jsonify({'error': 'Code cannot be empty'}), 400
        
        # Limit code size
        if len(code) > 100000:
            return jsonify({'error': 'Code too large (max 100KB)'}), 400
        
        # Analyze code
        prediction, confidence = analyzer.analyze_code(code, language)
        line_analyses = analyzer.analyze_lines(code, language, max_lines=50)
        
        # Prepare response
        response = {
            'prediction': prediction,
            'confidence': confidence,
            'language': language,
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
    """Analyze a GitHub repository (multi-language, memory optimized)"""
    try:
        if not analyzer:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        if not data or 'github_url' not in data:
            return jsonify({'error': 'Missing "github_url" field in request body'}), 400
        
        github_url = data['github_url']
        max_files = min(data.get('max_files', 15), 20)
        languages = data.get('languages', list(SUPPORTED_LANGUAGES.keys()))
        
        # Validate languages
        if not isinstance(languages, list):
            languages = [languages]
        
        invalid_langs = [lang for lang in languages if lang not in SUPPORTED_LANGUAGES]
        if invalid_langs:
            return jsonify({
                'error': f'Unsupported languages: {invalid_langs}',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        # Parse GitHub URL
        owner, repo = GitHubRepoAnalyzer.parse_github_url(github_url)
        
        if not owner or not repo:
            return jsonify({'error': 'Invalid GitHub URL format'}), 400
        
        logger.info(f"Analyzing repository: {owner}/{repo} for languages: {languages}")
        
        # Get code files
        code_files = GitHubRepoAnalyzer.get_all_code_files(owner, repo, languages=languages)
        
        if not code_files:
            return jsonify({
                'error': f'No code files found for languages: {languages}'
            }), 404
        
        logger.info(f"Found {len(code_files)} code files")
        
        # Analyze files
        file_results = []
        files_to_analyze = code_files[:max_files]
        
        # Group files by language for statistics
        files_by_language = {lang: 0 for lang in languages}
        
        for idx, file_info in enumerate(files_to_analyze):
            file_language = file_info.get('language', 'python')
            logger.info(f"Analyzing file {idx+1}/{len(files_to_analyze)}: {file_info['path']} ({file_language})")
            
            code = GitHubRepoAnalyzer.get_file_content(file_info['download_url'])
            
            if code:
                try:
                    result = analyzer.analyze_file(file_info['path'], code, file_language)
                    file_results.append(asdict(result))
                    files_by_language[file_language] = files_by_language.get(file_language, 0) + 1
                    
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
        
        # Language breakdown
        language_stats = {}
        for lang in languages:
            lang_files = [f for f in file_results if f['language'] == lang]
            if lang_files:
                language_stats[lang] = {
                    'total_files': len(lang_files),
                    'ai_files': sum(1 for f in lang_files if f['prediction'] == 'ai'),
                    'human_files': sum(1 for f in lang_files if f['prediction'] == 'human'),
                    'avg_confidence': float(np.mean([f['confidence'] for f in lang_files]))
                }
        
        response = {
            'repository': {
                'owner': owner,
                'name': repo,
                'url': github_url
            },
            'summary': {
                'total_files_found': len(code_files),
                'files_analyzed': total_files,
                'languages_analyzed': list(language_stats.keys()),
                'ai_files': ai_files,
                'human_files': human_files,
                'ai_percentage': (ai_files / total_files) * 100,
                'human_percentage': (human_files / total_files) * 100,
                'avg_confidence': avg_confidence,
                'total_lines': total_lines,
                'total_ai_lines': total_ai_lines,
                'total_human_lines': total_human_lines,
                'ai_lines_percentage': (total_ai_lines / (total_ai_lines + total_human_lines) * 100) if (total_ai_lines + total_human_lines) > 0 else 0,
                'human_lines_percentage': (total_human_lines / (total_ai_lines + total_human_lines) * 100) if (total_ai_lines + total_human_lines) > 0 else 0,
                'language_breakdown': language_stats
            },
            'files': file_results,
            'note': 'Optimized for free tier (single model, multi-language support)'
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
        'version': '2.0.0 (Multi-Language, Memory Optimized)',
        'status': 'running',
        'model_loaded': analyzer is not None and analyzer.model is not None,
        'model_type': 'Gradient Boosting (Python, JavaScript, Java)',
        'supported_languages': list(SUPPORTED_LANGUAGES.keys()),
        'memory_optimization': 'Enabled for Render Free Tier',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/languages': {
                'method': 'GET',
                'description': 'Get list of supported programming languages'
            },
            '/api/analyze-code': {
                'method': 'POST',
                'description': 'Analyze a single code snippet',
                'body': {
                    'code': 'string (required) - Code to analyze (max 100KB)',
                    'language': 'string (optional, default: python) - Language: python, javascript, java'
                },
                'limits': 'Max 100 lines analyzed, 100KB code size'
            },
            '/api/analyze-repository': {
                'method': 'POST',
                'description': 'Analyze a GitHub repository',
                'body': {
                    'github_url': 'string (required) - GitHub repository URL',
                    'max_files': 'integer (optional, default: 15, max: 20) - Maximum files to analyze',
                    'languages': 'array (optional, default: all) - Languages to analyze: ["python", "javascript", "java"]'
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