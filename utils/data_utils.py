"""
Data utilities for import/export and data transformation
"""
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from config.settings import EXPORT_SETTINGS
from utils.error_handling import error_handler, DataError

logger = logging.getLogger(__name__)


class DataExporter:
    """Handles data export operations"""
    
    def __init__(self):
        self.export_settings = EXPORT_SETTINGS
    
    @error_handler("DataExporter.export_to_json")
    def export_to_json(self, data: Dict[str, Any], 
                      filename: Optional[str] = None) -> str:
        """Export data to JSON format"""
        if not filename:
            timestamp = datetime.now().strftime(self.export_settings['timestamp_format'])
            filename = f"{self.export_settings['file_prefix']}{timestamp}.json"
        
        # Add metadata
        export_data = {
            **data,
            'export_metadata': {
                'export_time': datetime.now().isoformat(),
                'version': '1.0',
                'application': 'Options Pricing Calculator'
            }
        }
        
        json_string = json.dumps(
            export_data,
            indent=self.export_settings['json_indent'],
            default=str,
            ensure_ascii=False
        )
        
        logger.info(f"Exported data to JSON format: {filename}")
        return json_string
    
    @error_handler("DataExporter.export_to_csv")
    def export_to_csv(self, data: Union[List[Dict], pd.DataFrame],
                     filename: Optional[str] = None) -> str:
        """Export data to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime(self.export_settings['timestamp_format'])
            filename = f"data_export_{timestamp}.csv"
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise DataError(f"Unsupported data type for CSV export: {type(data)}")
        
        csv_string = df.to_csv(index=False)
        
        logger.info(f"Exported data to CSV format: {filename}")
        return csv_string


class DataImporter:
    """Handles data import operations"""
    
    @error_handler("DataImporter.import_from_json")
    def import_from_json(self, json_data: str) -> Dict[str, Any]:
        """Import data from JSON string"""
        try:
            data = json.loads(json_data)
            
            # Validate required structure
            if not isinstance(data, dict):
                raise DataError("JSON data must be a dictionary")
            
            # Remove metadata if present
            if 'export_metadata' in data:
                del data['export_metadata']
            
            logger.info("Successfully imported data from JSON")
            return data
            
        except json.JSONDecodeError as e:
            raise DataError(f"Invalid JSON format: {e}")
    
    @error_handler("DataImporter.import_from_csv")
    def import_from_csv(self, csv_data: str) -> pd.DataFrame:
        """Import data from CSV string"""
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_data))
            
            logger.info(f"Successfully imported {len(df)} rows from CSV")
            return df
            
        except Exception as e:
            raise DataError(f"Error reading CSV data: {e}")


class DataValidator:
    """Validates data structure and content"""
    
    @error_handler("DataValidator.validate_entities_data")
    def validate_entities_data(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Validate entities data structure"""
        errors = []
        
        if not isinstance(entities, list):
            errors.append("Entities data must be a list")
            return errors
        
        required_fields = ['name', 'loan_duration']
        
        for i, entity in enumerate(entities):
            if not isinstance(entity, dict):
                errors.append(f"Entity {i} must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in entity:
                    errors.append(f"Entity {i} missing required field: {field}")
            
            # Validate field types
            if 'name' in entity and not isinstance(entity['name'], str):
                errors.append(f"Entity {i} name must be a string")
            
            if 'loan_duration' in entity and not isinstance(entity['loan_duration'], (int, float)):
                errors.append(f"Entity {i} loan_duration must be numeric")
        
        return errors
    
    @error_handler("DataValidator.validate_tranches_data")
    def validate_tranches_data(self, tranches: List[Dict[str, Any]]) -> List[str]:
        """Validate tranches data structure"""
        errors = []
        
        if not isinstance(tranches, list):
            errors.append("Tranches data must be a list")
            return errors
        
        required_fields = ['entity', 'option_type', 'strike_price', 'time_to_expiration']
        
        for i, tranche in enumerate(tranches):
            if not isinstance(tranche, dict):
                errors.append(f"Tranche {i} must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in tranche:
                    errors.append(f"Tranche {i} missing required field: {field}")
            
            # Validate option type
            if 'option_type' in tranche and tranche['option_type'] not in ['call', 'put']:
                errors.append(f"Tranche {i} option_type must be 'call' or 'put'")
            
            # Validate numeric fields
            numeric_fields = ['strike_price', 'time_to_expiration']
            for field in numeric_fields:
                if field in tranche and not isinstance(tranche[field], (int, float)):
                    errors.append(f"Tranche {i} {field} must be numeric")
        
        return errors
    
    @error_handler("DataValidator.validate_depths_data")
    def validate_depths_data(self, depths: List[Dict[str, Any]]) -> List[str]:
        """Validate quoting depths data structure"""
        errors = []
        
        if not isinstance(depths, list):
            errors.append("Depths data must be a list")
            return errors
        
        required_fields = ['entity', 'exchange', 'bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps']
        
        for i, depth in enumerate(depths):
            if not isinstance(depth, dict):
                errors.append(f"Depth entry {i} must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in depth:
                    errors.append(f"Depth entry {i} missing required field: {field}")
            
            # Validate numeric fields
            numeric_fields = ['bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps']
            for field in numeric_fields:
                if field in depth and not isinstance(depth[field], (int, float)):
                    errors.append(f"Depth entry {i} {field} must be numeric")
                elif field in depth and depth[field] < 0:
                    errors.append(f"Depth entry {i} {field} must be non-negative")
        
        return errors


class DataTransformer:
    """Transforms data between different formats and structures"""
    
    @error_handler("DataTransformer.normalize_entities")
    def normalize_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize entities data structure"""
        normalized = []
        
        for entity in entities:
            normalized_entity = {
                'name': str(entity.get('name', '')).strip(),
                'loan_duration': int(entity.get('loan_duration', 12))
            }
            normalized.append(normalized_entity)
        
        return normalized
    
    @error_handler("DataTransformer.normalize_tranches")
    def normalize_tranches(self, tranches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize tranches data structure"""
        normalized = []
        
        for tranche in tranches:
            normalized_tranche = {
                'entity': str(tranche.get('entity', '')).strip(),
                'option_type': str(tranche.get('option_type', 'call')).lower(),
                'loan_duration': int(tranche.get('loan_duration', 12)),
                'start_month': int(tranche.get('start_month', 0)),
                'time_to_expiration': float(tranche.get('time_to_expiration', 1.0)),
                'strike_price': float(tranche.get('strike_price', 10.0)),
                'allocation_method': str(tranche.get('allocation_method', 'Percentage of Total Tokens')),
                'token_percentage': tranche.get('token_percentage'),
                'token_count': tranche.get('token_count')
            }
            normalized.append(normalized_tranche)
        
        return normalized
    
    @error_handler("DataTransformer.normalize_depths")
    def normalize_depths(self, depths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize quoting depths data structure"""
        normalized = []
        
        for depth in depths:
            normalized_depth = {
                'entity': str(depth.get('entity', '')).strip(),
                'exchange': str(depth.get('exchange', '')).strip(),
                'bid_ask_spread': float(depth.get('bid_ask_spread', 10.0)),
                'depth_method': str(depth.get('depth_method', 'Absolute Values ($)')),
                'depth_50bps': float(depth.get('depth_50bps', 0.0)),
                'depth_100bps': float(depth.get('depth_100bps', 0.0)),
                'depth_200bps': float(depth.get('depth_200bps', 0.0)),
                'depth_50bps_pct': depth.get('depth_50bps_pct'),
                'depth_100bps_pct': depth.get('depth_100bps_pct'),
                'depth_200bps_pct': depth.get('depth_200bps_pct'),
                'entity_loan_value': depth.get('entity_loan_value', 0.0)
            }
            normalized.append(normalized_depth)
        
        return normalized


# Global instances
data_exporter = DataExporter()
data_importer = DataImporter()
data_validator = DataValidator()
data_transformer = DataTransformer()


# Convenience functions
def export_session_data(entities: List[Dict], tranches: List[Dict], 
                       depths: List[Dict], filename: Optional[str] = None) -> str:
    """Export complete session data to JSON"""
    data = {
        'entities': entities,
        'tranches': tranches,
        'quoting_depths': depths,
        'timestamp': datetime.now().isoformat()
    }
    return data_exporter.export_to_json(data, filename)


def import_session_data(json_data: str) -> Dict[str, Any]:
    """Import complete session data from JSON"""
    data = data_importer.import_from_json(json_data)
    
    # Validate and normalize imported data
    errors = []
    
    if 'entities' in data:
        errors.extend(data_validator.validate_entities_data(data['entities']))
        data['entities'] = data_transformer.normalize_entities(data['entities'])
    
    if 'tranches' in data:
        errors.extend(data_validator.validate_tranches_data(data['tranches']))
        data['tranches'] = data_transformer.normalize_tranches(data['tranches'])
    
    if 'quoting_depths' in data:
        errors.extend(data_validator.validate_depths_data(data['quoting_depths']))
        data['quoting_depths'] = data_transformer.normalize_depths(data['quoting_depths'])
    
    if errors:
        logger.warning(f"Data validation warnings: {errors}")
    
    return data