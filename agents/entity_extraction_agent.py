"""
Entity Extraction Agent - Extracts companies, sectors, regulators
TARGET: 90%+ precision
"""
import spacy
from typing import Dict, List, Set
from utils.logger import logger
import re

class EntityExtractionAgent:
    """
    Agent 3: Extract structured entities from news
    """
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Financial entity dictionaries (Indian market focus)
        self.companies = {
            'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'SBI', 'Kotak Bank',
            'TCS', 'Infosys', 'Wipro', 'HCL Tech', 'Tech Mahindra',
            'Reliance', 'Tata Motors', 'Maruti', 'Mahindra', 'Bajaj',
            'ITC', 'HUL', 'Nestle', 'Britannia', 'Asian Paints',
            'Sun Pharma', 'Dr Reddy', 'Cipla', 'Lupin', 'Biocon'
        }
        
        self.sectors = {
            'Banking', 'IT', 'Information Technology', 'Auto', 'Automobile',
            'Pharmaceuticals', 'Pharma', 'FMCG', 'Telecom', 'Energy',
            'Steel', 'Cement', 'Real Estate', 'Infrastructure', 'Metals',
            'Oil & Gas', 'Power', 'Healthcare', 'Finance', 'Insurance'
        }
        
        self.regulators = {
            'RBI', 'Reserve Bank of India', 'SEBI', 
            'Securities and Exchange Board', 'IRDAI', 'TRAI'
        }
        
        # Stock symbols mapping
        self.symbol_map = {
            'HDFC Bank': 'HDFCBANK',
            'ICICI Bank': 'ICICIBANK',
            'Axis Bank': 'AXISBANK',
            'SBI': 'SBIN',
            'TCS': 'TCS',
            'Infosys': 'INFY',
            'Reliance': 'RELIANCE',
            'Tata Motors': 'TATAMOTORS',
            'Maruti': 'MARUTI'
        }
    
    def process(self, article: Dict) -> Dict:
        """
        Extract entities from article
        Returns article with entities added
        """
        try:
            text = f"{article['title']} {article['content']}"
            
            entities = {
                'companies': [],
                'sectors': [],
                'regulators': [],
                'people': [],
                'locations': [],
                'events': []
            }
            
            # Method 1: Dictionary matching (fast & accurate for known entities)
            entities['companies'] = self._match_companies(text)
            entities['sectors'] = self._match_sectors(text)
            entities['regulators'] = self._match_regulators(text)
            
            # Method 2: NER using spaCy (for additional entities)
            if self.nlp:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ == "ORG" and ent.text not in entities['companies']:
                        # Could be a company
                        if self._is_likely_company(ent.text):
                            entities['companies'].append(ent.text)
                    
                    elif ent.label_ == "PERSON":
                        entities['people'].append(ent.text)
                    
                    elif ent.label_ in ["GPE", "LOC"]:
                        entities['locations'].append(ent.text)
            
            # Method 3: Pattern matching for events
            entities['events'] = self._extract_events(text)
            
            # Clean and deduplicate
            for key in entities:
                entities[key] = list(set(entities[key]))  # Remove duplicates
            
            article['entities'] = entities
            
            logger.info(f"✓ Extracted entities from: {article['title'][:50]} "
                       f"({len(entities['companies'])} companies, "
                       f"{len(entities['sectors'])} sectors)")
            
            return article
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            article['entities'] = {'companies': [], 'sectors': [], 'regulators': [], 
                                  'people': [], 'locations': [], 'events': []}
            return article
    
    def _match_companies(self, text: str) -> List[str]:
        """Match known companies"""
        found = []
        text_lower = text.lower()
        
        for company in self.companies:
            if company.lower() in text_lower:
                found.append(company)
        
        return found
    
    def _match_sectors(self, text: str) -> List[str]:
        """Match sectors"""
        found = []
        text_lower = text.lower()
        
        for sector in self.sectors:
            if sector.lower() in text_lower:
                found.append(sector)
        
        return found
    
    def _match_regulators(self, text: str) -> List[str]:
        """Match regulators"""
        found = []
        text_lower = text.lower()
        
        for regulator in self.regulators:
            if regulator.lower() in text_lower:
                found.append(regulator)
        
        return found
    
    def _is_likely_company(self, text: str) -> bool:
        """Check if text is likely a company name"""
        company_indicators = [
            'Ltd', 'Limited', 'Inc', 'Corp', 'Bank', 'Industries',
            'Motors', 'Tech', 'Pharma', 'Capital', 'Finance'
        ]
        
        return any(indicator in text for indicator in company_indicators)
    
    def _extract_events(self, text: str) -> List[str]:
        """Extract financial events using patterns"""
        events = []
        
        event_patterns = {
            r'dividend': 'Dividend Announcement',
            r'buyback|buy.?back': 'Stock Buyback',
            r'merger|acquisition': 'M&A Activity',
            r'ipo|initial public offering': 'IPO',
            r'earnings|results|quarterly': 'Earnings Report',
            r'rate.{0,10}hike|rate.{0,10}cut': 'Rate Change',
            r'policy.{0,10}change': 'Policy Update'
        }
        
        for pattern, event_name in event_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                events.append(event_name)
        
        return events
    
    def get_stock_symbols(self, companies: List[str]) -> List[str]:
        """Map company names to stock symbols"""
        symbols = []
        for company in companies:
            symbol = self.symbol_map.get(company)
            if symbol:
                symbols.append(symbol)
        
        return symbols