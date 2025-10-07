import streamlit as st
import joblib
import numpy as np
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

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
            
            # Load models
            for name, path in model_files.items():
                if Path(path).exists():
                    self.models[name] = joblib.load(path)
                else:
                    st.warning(f"Model {name} not found at {path}")
            
            # Load vectorizer
            if Path('model/vectorizer.pkl').exists():
                self.vectorizer = joblib.load('model/vectorizer.pkl')
            else:
                st.error("Vectorizer not found!")
                return
            
            # Load label encoder (optional for XGBoost)
            if Path('model/labelencoder.pkl').exists():
                self.label_encoder = joblib.load('model/labelencoder.pkl')
                
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
    
    def predict_with_model(self, X: np.ndarray, model_name: str) -> Optional[ModelResult]:
        """Make prediction with a specific model"""
        if model_name not in self.models:
            return None
            
        try:
            model = self.models[model_name]
            
            if model_name == 'xgboost':
                # Special handling for XGBoost
                y_pred = model.predict(X)
                if self.label_encoder:
                    prediction = self.label_encoder.inverse_transform(y_pred)[0]
                else:
                    prediction = "ai" if y_pred[0] == 0 else "human"
            else:
                prediction = model.predict(X)[0]
            
            confidence = model.predict_proba(X).max()
            
            return ModelResult(
                name=model_name.replace('_', ' ').title(),
                prediction=prediction,
                confidence=confidence
            )
            
        except Exception as e:
            st.warning(f"Error with {model_name}: {str(e)}")
            return None
    
    def analyze_code(self, code: str) -> Tuple[List[ModelResult], str, float]:
        """Analyze code with all available models"""
        if not self.vectorizer:
            return [], "Error", 0.0
        
        X = self.vectorizer.transform([code])
        results = []
        
        # Get predictions from all models
        for model_name in self.models.keys():
            result = self.predict_with_model(X, model_name)
            if result:
                results.append(result)
        
        # Calculate ensemble prediction
        final_prediction, final_confidence = self.ensemble_vote(results)
        
        return results, final_prediction, final_confidence
    
    def ensemble_vote(self, results: List[ModelResult]) -> Tuple[str, float]:
        """Calculate ensemble prediction using weighted voting"""
        if not results:
            return "unknown", 0.0
        
        ai_votes = [r.confidence for r in results if r.prediction == "ai"]
        human_votes = [r.confidence for r in results if r.prediction == "human"]
        
        # Weighted average based on confidence
        ai_score = np.mean(ai_votes) * len(ai_votes) if ai_votes else 0
        human_score = np.mean(human_votes) * len(human_votes) if human_votes else 0
        
        if ai_score > human_score:
            return "ai", ai_score / len(results)
        else:
            return "human", human_score / len(results)
    
    def analyze_lines(self, code: str, model_name: str = 'gradient_boost') -> List[LineAnalysis]:
        """Perform line-by-line analysis"""
        if model_name not in self.models or not self.vectorizer:
            return []
        
        lines = code.split('\n')
        line_analyses = []
        
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
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
                        
                except Exception as e:
                    continue  # Skip problematic lines
        
        return line_analyses
    
    def detect_patterns(self, line: str) -> List[str]:
        """Detect coding patterns in a line"""
        patterns = []
        line = line.strip()
        
        # Common patterns
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

class SummarizationEngine:
    """Enhanced summarization engine for code analysis results"""
    
    @staticmethod
    def generate_summary(results: List[ModelResult], final_pred: str, 
                        line_analyses: List[LineAnalysis]) -> Dict[str, str]:
        """Generate comprehensive analysis summary"""
        
        # Model consensus analysis
        consensus = SummarizationEngine._analyze_consensus(results, final_pred)
        
        # Pattern analysis
        patterns = SummarizationEngine._analyze_patterns(line_analyses)
        
        # Line distribution analysis
        distribution = SummarizationEngine._analyze_distribution(line_analyses)
        
        # Generate reasoning
        reasoning = SummarizationEngine._generate_reasoning(
            final_pred, consensus, patterns, distribution
        )
        
        return {
            'consensus': consensus,
            'patterns': patterns,
            'distribution': distribution,
            'reasoning': reasoning
        }
    
    @staticmethod
    def _analyze_consensus(results: List[ModelResult], final_pred: str) -> str:
        """Analyze model consensus"""
        if not results:
            return "No models available for analysis."
        
        ai_count = sum(1 for r in results if r.prediction == "ai")
        total = len(results)
        
        if ai_count == total:
            return f"All {total} models unanimously predict AI-generated code."
        elif ai_count == 0:
            return f"All {total} models unanimously predict human-written code."
        else:
            return f"{ai_count}/{total} models predict AI-generated, {total-ai_count}/{total} predict human-written."
    
    @staticmethod
    def _analyze_patterns(line_analyses: List[LineAnalysis]) -> str:
        """Analyze detected patterns"""
        if not line_analyses:
            return "No patterns detected."
        
        # Count pattern frequencies
        pattern_counts = {}
        ai_patterns = {}
        human_patterns = {}
        
        for analysis in line_analyses:
            for pattern in analysis.patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                
                if analysis.prediction == "ai":
                    ai_patterns[pattern] = ai_patterns.get(pattern, 0) + 1
                else:
                    human_patterns[pattern] = human_patterns.get(pattern, 0) + 1
        
        # Find most significant patterns
        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if top_patterns:
            pattern_text = f"Most common patterns: {', '.join([p[0] for p in top_patterns])}. "
            
            # Analyze AI vs Human pattern preferences
            ai_indicators = [p for p, count in ai_patterns.items() if count > human_patterns.get(p, 0)]
            human_indicators = [p for p, count in human_patterns.items() if count > ai_patterns.get(p, 0)]
            
            if ai_indicators:
                pattern_text += f"AI-leaning patterns: {', '.join(ai_indicators)}. "
            if human_indicators:
                pattern_text += f"Human-leaning patterns: {', '.join(human_indicators)}."
                
            return pattern_text
        
        return "No significant patterns detected."
    
    @staticmethod
    def _analyze_distribution(line_analyses: List[LineAnalysis]) -> str:
        """Analyze line prediction distribution"""
        if not line_analyses:
            return "No lines analyzed."
        
        ai_lines = [a for a in line_analyses if a.prediction == "ai"]
        human_lines = [a for a in line_analyses if a.prediction == "human"]
        
        total = len(line_analyses)
        ai_count = len(ai_lines)
        human_count = len(human_lines)
        
        ai_pct = (ai_count / total) * 100
        human_pct = (human_count / total) * 100
        
        # Calculate confidence statistics
        avg_confidence = np.mean([a.confidence for a in line_analyses])
        
        return (f"{ai_count}/{total} lines ({ai_pct:.1f}%) flagged as AI-generated, "
                f"{human_count}/{total} lines ({human_pct:.1f}%) as human-written. "
                f"Average confidence: {avg_confidence:.2f}")
    
    @staticmethod
    def _generate_reasoning(final_pred: str, consensus: str, patterns: str, distribution: str) -> str:
        """Generate final reasoning explanation"""
        reasoning = []
        
        # Primary prediction reasoning
        if final_pred == "ai":
            reasoning.append("🤖 **AI-Generated Code Detected**")
            reasoning.append("The ensemble analysis suggests this code was likely generated by AI based on:")
        else:
            reasoning.append("👨‍💻 **Human-Written Code Detected**")
            reasoning.append("The ensemble analysis suggests this code was likely written by a human based on:")
        
        reasoning.append(f"• **Model Consensus**: {consensus}")
        reasoning.append(f"• **Pattern Analysis**: {patterns}")
        reasoning.append(f"• **Line Distribution**: {distribution}")
        
        return "\n".join(reasoning)

# Streamlit UI
def main():
    st.set_page_config(
        page_title="AI vs Human Code Detector",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI vs Human Code Detector")
    st.markdown("**Advanced ensemble analysis with dynamic summarization**")
    st.markdown("---")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        with st.spinner("Loading models..."):
            st.session_state.analyzer = CodeAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        code_input = st.text_area(
            "📝 Enter your Python code here:",
            height=400,
            placeholder="# Paste your Python code here...\nprint('Hello, World!')"
        )
    
    with col2:
        st.markdown("### ⚙️ Analysis Options")
        
        line_model = st.selectbox(
            "Model for line analysis:",
            ["gradient_boost", "random_forest", "logistic", "xgboost"],
            help="Choose which model to use for line-by-line analysis"
        )
        
        show_confidence = st.checkbox("Show confidence scores", value=True)
        show_patterns = st.checkbox("Show detected patterns", value=True)
    
    # Analysis button
    if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
        if not code_input.strip():
            st.warning("⚠️ Please enter some code to analyze.")
            return
        
        with st.spinner("Analyzing code..."):
            # Main analysis
            results, final_pred, final_conf = analyzer.analyze_code(code_input)
            
            if not results:
                st.error("❌ Analysis failed. Please check if models are loaded correctly.")
                return
            
            # Line-by-line analysis
            line_analyses = analyzer.analyze_lines(code_input, line_model)
            
            # Generate summary
            summary = SummarizationEngine.generate_summary(results, final_pred, line_analyses)
        
        # Display results
        st.markdown("## 📊 Analysis Results")
        
        # Final prediction
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if final_pred == "ai":
                st.error(f"🤖 **AI-Generated**")
                st.metric("Confidence", f"{final_conf:.1%}")
            else:
                st.success(f"👨‍💻 **Human-Written**")
                st.metric("Confidence", f"{final_conf:.1%}")
        
        with col2:
            ai_count = sum(1 for r in results if r.prediction == "ai")
            st.metric("Models Voting AI", f"{ai_count}/{len(results)}")
        
        with col3:
            avg_conf = np.mean([r.confidence for r in results])
            st.metric("Average Confidence", f"{avg_conf:.1%}")
        
        # Model breakdown
        st.markdown("### 🔬 Individual Model Predictions")
        
        for result in results:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{result.name}**")
            
            with col2:
                if result.prediction == "ai":
                    st.write("🤖 AI-Generated")
                else:
                    st.write("👨‍💻 Human-Written")
            
            with col3:
                if show_confidence:
                    st.write(f"{result.confidence:.1%}")
        
        # Line-by-line analysis
        if line_analyses:
            st.markdown("### 📝 Line-by-Line Analysis")
            
            for analysis in line_analyses:
                if analysis.prediction == "ai":
                    bg_color = "#ffebee"  # Light red
                    icon = "🤖"
                else:
                    bg_color = "#e8f5e8"  # Light green  
                    icon = "👨‍💻"
                
                pattern_text = ""
                if show_patterns and analysis.patterns:
                    pattern_text = f" | Patterns: {', '.join(analysis.patterns)}"
                
                conf_text = f" ({analysis.confidence:.1%})" if show_confidence else ""
                
                st.markdown(
                    f'<div style="background-color:{bg_color}; padding:8px; margin:4px 0; border-radius:4px; border-left:4px solid {"#f44336" if analysis.prediction == "ai" else "#4caf50"};">'
                    f'<strong>Line {analysis.line_number}</strong> {icon}{conf_text}{pattern_text}<br>'
                    f'<code>{analysis.content}</code>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        # Dynamic summary
        st.markdown("### 🧠 Analysis Summary")
        st.markdown(summary['reasoning'])
        
        with st.expander("📈 Detailed Statistics"):
            st.write("**Consensus Analysis:**", summary['consensus'])
            st.write("**Pattern Analysis:**", summary['patterns'])
            st.write("**Distribution Analysis:**", summary['distribution'])

if __name__ == "__main__":
    main()