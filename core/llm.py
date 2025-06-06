import json
import logging
from typing import Dict, List, Optional
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnnotator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._load_api_key()
        
    def _load_api_key(self) -> str:
        """Charge la clé API depuis les variables d'environnement ou un fichier de configuration."""
        import os
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            config_path = Path.home() / ".dnarecon" / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    api_key = config.get("llm_api_key")
        if not api_key:
            raise ValueError("LLM API key not found. Please set LLM_API_KEY environment variable or configure in ~/.dnarecon/config.json")
        return api_key

    def analyze_behavior(self, behavior_data: Dict) -> Dict:
        """Analyse le comportement et génère des annotations automatiques."""
        try:
            # Préparation des données pour l'analyse
            analysis_prompt = self._prepare_analysis_prompt(behavior_data)
            
            # Appel à l'API LLM (exemple avec OpenAI)
            response = self._call_llm_api(analysis_prompt)
            
            # Traitement de la réponse
            annotations = self._process_llm_response(response)
            
            return {
                "original_data": behavior_data,
                "annotations": annotations,
                "confidence_score": self._calculate_confidence(annotations)
            }
        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            raise

    def _prepare_analysis_prompt(self, data: Dict) -> str:
        """Prépare le prompt pour l'analyse LLM."""
        return f"""
        Analyze the following web application behavior:
        URL: {data.get('url', 'N/A')}
        Response Status: {data.get('status_code', 'N/A')}
        Response Time: {data.get('response_time', 'N/A')}
        Headers: {json.dumps(data.get('headers', {}), indent=2)}
        Body: {data.get('body', 'N/A')}
        
        Please provide:
        1. Security implications
        2. Potential vulnerabilities
        3. Recommended actions
        """

    def _call_llm_api(self, prompt: str) -> Dict:
        """Appelle l'API LLM pour l'analyse."""
        # Implémentation à adapter selon le service LLM utilisé
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Exemple avec OpenAI (à adapter selon le service choisi)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.text}")
            
        return response.json()

    def _process_llm_response(self, response: Dict) -> Dict:
        """Traite la réponse de l'API LLM."""
        try:
            content = response['choices'][0]['message']['content']
            # Parsing de la réponse en format structuré
            return {
                "analysis": content,
                "timestamp": response.get('created'),
                "model": response.get('model')
            }
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            raise

    def _calculate_confidence(self, annotations: Dict) -> float:
        """Calcule un score de confiance pour les annotations."""
        # Logique de calcul de confiance à implémenter
        return 0.85  # Valeur par défaut

def run(input_file: str) -> None:
    """Point d'entrée principal pour l'annotation LLM."""
    try:
        with open(input_file, 'r') as f:
            behavior_data = json.load(f)
        
        annotator = LLMAnnotator()
        results = annotator.analyze_behavior(behavior_data)
        
        output_file = input_file.replace('.json', '_annotated.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Annotations saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error in LLM annotation process: {str(e)}")
        raise